
#!/usr/bin/env python3
"""
Enhanced EII Analysis
=====================

This script extends the original test_prompt.py by adding readability metrics and
synthetic ethos detection to the Expertise Inflation Index (EII) scoring. It
supports running both OpenAI and Anthropic models and computes cross‑model
calibration metrics. The script expects API keys to be provided via
environment variables `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`.

Usage:
    python enhanced_analysis.py --article examples/ai_vision_example.md --model both

Options:
    --article: Path to the article file to analyze.
    --prompt:  Path to the scoring prompt (default: prompts/score_prompt_enhanced.txt).
    --model:   Which model to use: 'openai', 'anthropic', or 'both'.
    --output:  Path to save the JSON results (optional).

Note:
    This script does not require external libraries beyond the standard
    library and the OpenAI/Anthropic clients. If those clients are not
    available, the script will gracefully skip calls to that service.
"""

import os
import json
import re
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("\u26a0\ufe0f  OpenAI package not found. Install with: pip install openai")

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("\u26a0\ufe0f  Anthropic package not found. Install with: pip install anthropic")


def load_prompt(path: str) -> str:
    """Load the scoring prompt from a file."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def load_article(path: str) -> str:
    """Load article content from a file, stripping YAML front matter if present."""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Remove YAML front matter delineated by --- markers
    parts = content.split('---')
    if len(parts) > 2:
        return parts[1].strip()
    return content.strip()


def count_syllables(word: str) -> int:
    """A simple heuristic to count syllables in a word."""
    word = word.lower()
    vowels = "aeiouy"
    # Short words counted as single syllable
    if len(word) <= 3:
        return 1
    count = 0
    prev_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    # Subtract silent 'e'
    if word.endswith('e') and count > 1 and word[-2] not in vowels:
        count -= 1
    return max(count, 1)


def compute_readability(text: str) -> int:
    """
    Compute a readability score on a 1–10 scale based on Flesch reading ease.
    Returns an integer between 1 and 10, where higher values indicate easier
    readability.
    """
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    num_sentences = max(len(sentences), 1)
    words = re.findall(r'\b\w+\b', text)
    num_words = max(len(words), 1)
    syllable_count = sum(count_syllables(word) for word in words)
    # Flesch Reading Ease formula
    reading_ease = 206.835 - 1.015 * (num_words / num_sentences) - 84.6 * (syllable_count / num_words)
    # Clamp to [0, 100]
    reading_ease = max(min(reading_ease, 100), 0)
    # Map to 1–10 scale
    score = int(1 + (reading_ease / 100) * 9)
    return max(min(score, 10), 1)


def query_openai(prompt: str, article: str) -> Optional[Dict[str, Any]]:
    """Send the prompt to OpenAI and return the parsed JSON response."""
    if not HAS_OPENAI:
        return None
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("\u26a0\ufe0f  OPENAI_API_KEY not set. Skipping OpenAI analysis.")
        return None
    
    # Use the new OpenAI v1.0+ client format
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    full_prompt = prompt.replace('[INSERT ARTICLE TEXT HERE]', article)
    try:
        response = client.chat.completions.create(
            model="gpt-4-0613",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        result_text = response.choices[0].message.content
        # Find JSON object in the response
        json_start = result_text.find('{')
        json_end = result_text.rfind('}') + 1
        if json_start == -1 or json_end == -1:
            raise ValueError("No JSON object found in OpenAI response.")
        json_data = result_text[json_start:json_end]
        return json.loads(json_data)
    except Exception as e:
        print(f"\u274c Error querying OpenAI: {e}")
        return None


def query_anthropic(prompt: str, article: str) -> Optional[Dict[str, Any]]:
    """Send the prompt to Anthropic and return the parsed JSON response."""
    if not HAS_ANTHROPIC:
        return None
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("\u26a0\ufe0f  ANTHROPIC_API_KEY not set. Skipping Anthropic analysis.")
        return None
    client = Anthropic(api_key=api_key)
    full_prompt = prompt.replace('[INSERT ARTICLE TEXT HERE]', article)
    try:
        # Use the correct Claude-3 messages API
        completion = client.messages.create(
            model="claude-3-haiku-20240307",  # Using Haiku for cost efficiency
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=1000,
            temperature=0.3
        )
        result_text = completion.content[0].text
        json_start = result_text.find('{')
        json_end = result_text.rfind('}') + 1
        if json_start == -1 or json_end == -1:
            raise ValueError("No JSON object found in Anthropic response.")
        json_data = result_text[json_start:json_end]
        return json.loads(json_data)
    except Exception as e:
        print(f"\u274c Error querying Anthropic: {e}")
        return None


def compute_differences(scores_a: Dict[str, Any], scores_b: Dict[str, Any]) -> Dict[str, Any]:
    """Compute absolute differences between two score dictionaries."""
    differences: Dict[str, Any] = {}
    for key in scores_a:
        if key in scores_b:
            try:
                differences[key] = abs(int(scores_a[key]) - int(scores_b[key]))
            except (ValueError, TypeError):
                differences[key] = None
    return differences


def main():
    parser = argparse.ArgumentParser(description="Enhanced EII Analysis")
    parser.add_argument('--article', type=str, required=True, help="Path to article file")
    parser.add_argument('--prompt', type=str, default='config/score_prompt_enhanced.txt', help="Path to prompt file")
    parser.add_argument('--model', type=str, choices=['openai','anthropic','both'], default='both', help="Which model to use")
    parser.add_argument('--output', type=str, help="Path to save output JSON")
    args = parser.parse_args()

    prompt_text = load_prompt(args.prompt)
    article_text = load_article(args.article)

    # Compute readability using our own metric
    readability_score = compute_readability(article_text)

    results: Dict[str, Any] = {
        'readability_computed': readability_score,
        'article': Path(args.article).stem
    }

    openai_result = None
    anthropic_result = None
    if args.model in ('openai','both'):
        openai_result = query_openai(prompt_text, article_text)
        if openai_result:
            results['openai'] = openai_result
    if args.model in ('anthropic','both'):
        anthropic_result = query_anthropic(prompt_text, article_text)
        if anthropic_result:
            results['anthropic'] = anthropic_result
    # If both results exist, compute cross‑model differences
    if openai_result and anthropic_result:
        diff = compute_differences(openai_result.get('scores',{}), anthropic_result.get('scores',{}))
        results['score_differences'] = diff
    # Save results if requested
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as out_f:
                json.dump(results, out_f, indent=2)
            print(f"\u2705 Results saved to {args.output}")
        except Exception as e:
            print(f"\u274c Could not save results: {e}")
    else:
        print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
