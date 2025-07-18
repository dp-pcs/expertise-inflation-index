#!/usr/bin/env python3
"""
Test script for the Expertise Inflation Index (EII) prompt.
Tests the prompt against example articles using various LLM APIs.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Try importing API clients (install with: pip install openai anthropic google-generativeai)
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("⚠️  OpenAI package not found. Install with: pip install openai")

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("⚠️  Anthropic package not found. Install with: pip install anthropic")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def load_prompt() -> str:
    """Load the EII scoring prompt."""
    with open('prompts/score_prompt.txt', 'r') as f:
        return f.read()

def load_example_article(filename: str) -> str:
    """Load an example article, extracting just the content between the first --- and last ---"""
    filepath = Path('examples') / filename
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Extract content between --- markers
    parts = content.split('---')
    if len(parts) >= 3:
        # Return the middle section (the actual article content)
        return parts[1].strip()
    else:
        # Fallback: return everything after the first ---
        if len(parts) >= 2:
            return parts[1].strip()
        return content

def test_with_openai(prompt: str, article: str) -> Optional[Dict[str, Any]]:
    """Test prompt with OpenAI GPT-4."""
    if not HAS_OPENAI:
        return None
    
    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        full_prompt = prompt.replace('[INSERT ARTICLE TEXT HERE]', article)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        result_text = response.choices[0].message.content
        
        # Try to parse JSON response
        try:
            # Look for JSON in the response
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_text = result_text[json_start:json_end]
                return {
                    "model": "gpt-4",
                    "raw_response": result_text,
                    "parsed_json": json.loads(json_text),
                    "success": True
                }
        except json.JSONDecodeError:
            pass
        
        return {
            "model": "gpt-4", 
            "raw_response": result_text,
            "parsed_json": None,
            "success": False,
            "error": "Could not parse JSON response"
        }
        
    except Exception as e:
        return {
            "model": "gpt-4",
            "success": False,
            "error": str(e)
        }

def test_with_anthropic(prompt: str, article: str) -> Optional[Dict[str, Any]]:
    """Test prompt with Anthropic Claude."""
    if not HAS_ANTHROPIC:
        return None
    
    try:
        client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        full_prompt = prompt.replace('[INSERT ARTICLE TEXT HERE]', article)
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.3,
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )
        
        result_text = response.content[0].text
        
        # Try to parse JSON response
        try:
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_text = result_text[json_start:json_end]
                return {
                    "model": "claude-3-haiku",
                    "raw_response": result_text,
                    "parsed_json": json.loads(json_text),
                    "success": True
                }
        except json.JSONDecodeError:
            pass
        
        return {
            "model": "claude-3-haiku",
            "raw_response": result_text, 
            "parsed_json": None,
            "success": False,
            "error": "Could not parse JSON response"
        }
        
    except Exception as e:
        return {
            "model": "claude-3-haiku",
            "success": False,
            "error": str(e)
        }

def main():
    """Run the EII prompt test suite."""
    print("🧠 Expertise Inflation Index (EII) - Prompt Testing\n")
    
    # Load prompt
    try:
        prompt = load_prompt()
        print("✅ Loaded EII prompt")
    except Exception as e:
        print(f"❌ Failed to load prompt: {e}")
        return
    
    # Test examples
    examples = [
        ("high_inflation_example.md", "High Inflation Example"),
        ("balanced_example.md", "Balanced Example"), 
        ("satirical_example.md", "Satirical Example")
    ]
    
    results = {}
    
    for filename, name in examples:
        print(f"\n📄 Testing: {name}")
        print("-" * 50)
        
        try:
            article = load_example_article(filename)
            print(f"✅ Loaded article ({len(article)} characters)")
            
            # Test with available APIs
            example_results = {}
            
            if HAS_OPENAI and os.getenv('OPENAI_API_KEY'):
                print("🤖 Testing with GPT-4...")
                result = test_with_openai(prompt, article)
                if result:
                    example_results['openai'] = result
                    if result['success']:
                        scores = result['parsed_json']['scores']
                        overall = result['parsed_json']['analysis']['overall_eii_score']
                        print(f"   EII Score: {overall:.1f}/10")
                        print(f"   Breakdown: Conf:{scores['confidence']} Jarg:{scores['jargon_density']} Self:{scores['self_reference']} Orig:{scores['originality']} Humor:{scores['humor_rating']}")
                    else:
                        print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                time.sleep(1)  # Rate limiting
            
            if HAS_ANTHROPIC and os.getenv('ANTHROPIC_API_KEY'):
                print("🤖 Testing with Claude...")
                result = test_with_anthropic(prompt, article)
                if result:
                    example_results['anthropic'] = result
                    if result['success']:
                        scores = result['parsed_json']['scores']
                        overall = result['parsed_json']['analysis']['overall_eii_score']
                        print(f"   EII Score: {overall:.1f}/10")
                        print(f"   Breakdown: Conf:{scores['confidence']} Jarg:{scores['jargon_density']} Self:{scores['self_reference']} Orig:{scores['originality']} Humor:{scores['humor_rating']}")
                    else:
                        print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                time.sleep(1)  # Rate limiting
            
            results[filename] = example_results
            
        except Exception as e:
            print(f"❌ Failed to test {filename}: {e}")
    
    # Save results
    output_file = 'test_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to {output_file}")
    print("\n🎯 Test complete! Check the results to see how well the prompt performs.")

if __name__ == "__main__":
    main() 