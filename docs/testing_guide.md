# Testing Guide: Expertise Inflation Index (EII) Prompt

This guide explains how to test the EII scoring prompt against example articles.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

Required API keys for testing:
- `OPENAI_API_KEY`: For GPT-4 testing
- `ANTHROPIC_API_KEY`: For Claude testing

### 3. Run Tests

```bash
python test_prompt.py
```

## Example Articles

The test suite includes three types of articles:

### High Inflation Example (`high_inflation_example.md`)
- **Expected Score**: ~8.5/10
- Characteristics: Extreme overconfidence, heavy jargon, self-promotion
- Example claims: "Revolutionary AGI framework", "cracked the code"

### Balanced Example (`balanced_example.md`) 
- **Expected Score**: ~2.8/10
- Characteristics: Humble tone, acknowledges limitations, cites others
- Example language: "might be useful", "we're still learning"

### Satirical Example (`satirical_example.md`)
- **Expected Score**: ~4.8/10 (high humor, moderate other metrics)
- Characteristics: Self-aware, humorous, meta-commentary on AI discourse

## Output

The test script will:
1. Load each example article
2. Test with available LLM APIs (OpenAI, Anthropic)
3. Parse JSON responses and display scores
4. Save detailed results to `test_results.json`

## Understanding Scores

Each article gets scored on five dimensions (1-10):

- **Confidence**: How certain/overconfident the author sounds
- **Jargon Density**: Use of technical buzzwords and complexity
- **Self-Reference**: Amount of self-promotion and authority claims
- **Originality**: Claims of novelty and breakthrough discoveries
- **Humor/Self-Awareness**: Use of humor and acknowledgment of limitations

The **Overall EII Score** is the average of the first four metrics (humor is separate).

## Troubleshooting

- **"Package not found"**: Install missing dependencies with pip
- **"API key not found"**: Ensure your `.env` file has the correct API keys
- **"JSON parse error"**: The LLM didn't return valid JSON - try adjusting the prompt
- **Rate limiting**: The script includes 1-second delays between API calls 