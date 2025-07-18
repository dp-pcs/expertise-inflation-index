# n8n Workflow Setup Guide

This guide walks you through setting up the Expertise Inflation Index (EII) n8n workflow for automated article analysis.

## 🎯 Workflow Overview

The EII workflow automates the complete pipeline:

1. **Webhook Trigger** → Receives URL to analyze
2. **Firecrawl Scrape** → Extracts article content
3. **LLM Analysis** → Analyzes content with both OpenAI and Anthropic
4. **Supabase Storage** → Saves article and scores to database
5. **Response** → Returns analysis results

## 🚀 Quick Setup

### 1. Install n8n

**Option A: n8n Cloud (Recommended)**
- Sign up at [n8n.cloud](https://n8n.cloud)
- Import the workflow directly

**Option B: Self-Hosted**
```bash
npm install n8n -g
n8n start
```

### 2. Import Workflow

1. Open n8n interface
2. Click **"+ Add workflow"**
3. Click **"Import from file"**
4. Upload `n8n/eii_workflow.json`

### 3. Configure Environment Variables

Set these environment variables in n8n:

```bash
# API Keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
FIRECRAWL_API_KEY=fc-your-firecrawl-key

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

**In n8n Cloud:**
- Go to Settings → Environment Variables
- Add each variable with its value

**In Self-Hosted n8n:**
- Add to your `.env` file or system environment

### 4. Activate Workflow

1. Click **"Activate"** toggle in the workflow
2. Note the webhook URL (will be something like: `https://your-n8n.app/webhook/eii-analyze`)

## 📡 Using the Workflow

### Simple API Call

Send a POST request to your webhook URL:

```bash
curl -X POST https://your-n8n.app/webhook/eii-analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/ai-article"}'
```

### Example Response

```json
{
  "success": true,
  "message": "Article analyzed successfully",
  "data": {
    "url": "https://example.com/ai-article",
    "title": "The Future of AI",
    "eii_score": 7.2,
    "scores": {
      "confidence": 8,
      "jargon_density": 7,
      "self_reference": 6,
      "originality": 8,
      "humor_rating": 2
    },
    "analysis": {
      "tone_summary": "The article exhibits high confidence with technical jargon...",
      "inflation_type": "Technical Guru",
      "key_phrases": ["revolutionary breakthrough", "paradigm shift", "my research"]
    },
    "model_used": "gpt-4"
  }
}
```

## 🛠️ Workflow Components Explained

### 1. Webhook Trigger
- **Purpose**: Receives URL to analyze
- **Input**: `{"url": "https://article-url.com"}`
- **Configuration**: No special setup needed

### 2. Firecrawl Scrape
- **Purpose**: Extracts clean article content
- **API**: Firecrawl /v0/scrape endpoint
- **Output**: Markdown content, title, author, metadata

### 3. Check Scrape Success
- **Purpose**: Validates scraping worked
- **Logic**: Checks if `success` field is true
- **Error Handling**: Returns error response if scraping failed

### 4. Load EII Prompt
- **Purpose**: Loads scoring prompt template
- **Source**: Reads from prompts/score_prompt.txt
- **Fallback**: Hardcoded prompt if file not found

### 5. LLM Analysis (Parallel)
- **OpenAI Node**: Uses GPT-4 for analysis
- **Anthropic Node**: Uses Claude-3-Haiku as backup
- **Logic**: Tries OpenAI first, falls back to Anthropic
- **Output**: Structured JSON with scores and analysis

### 6. Prepare Supabase Data
- **Purpose**: Parses LLM responses and structures data
- **Logic**: Extracts JSON from responses, handles errors
- **Output**: Clean article and scores objects

### 7. Database Insert (Parallel)
- **Insert Article**: Adds article to `articles` table
- **Insert Scores**: Adds scores to `scores` table with article reference
- **Database**: Uses Supabase REST API

### 8. Webhook Response
- **Purpose**: Returns structured response to caller
- **Format**: JSON with scores, analysis, and metadata

## 🔧 Customization Options

### Change LLM Models

Edit the model parameters in the LLM nodes:

```json
// OpenAI node
"model": "gpt-4-turbo"  // or "gpt-3.5-turbo"

// Anthropic node  
"model": "claude-3-opus-20240229"  // or "claude-3-sonnet-20240229"
```

### Add Scheduling

Replace webhook trigger with:
- **Cron node**: For scheduled analysis
- **RSS Feed node**: To monitor specific sources
- **Google Sheets node**: To process URL lists

### Extend Analysis

Add nodes for:
- **Sentiment analysis**
- **Readability scoring** 
- **Keyword extraction**
- **Social media posting**

## 🔍 Testing & Debugging

### Test Individual Nodes

1. **Manual execution**: Click "Execute Node" on each step
2. **Check outputs**: Verify data structure at each stage
3. **Error inspection**: Review error messages and logs

### Common Issues

**Firecrawl fails:**
- Check API key is correct
- Verify URL is accessible
- Some sites block scrapers

**LLM parsing fails:**
- Check API keys and quotas
- Review prompt formatting
- Verify JSON response structure

**Supabase insert fails:**
- Check database connection
- Verify table schema matches
- Review API key permissions

### Debug Mode

Enable detailed logging:
1. Go to Settings → Log Level → Debug
2. Check execution logs for detailed output
3. Monitor API rate limits and errors

## 📊 Monitoring & Analytics

### Workflow Metrics

Monitor in n8n dashboard:
- **Execution count**: Total analyses run
- **Success rate**: Percentage of successful completions
- **Average duration**: Time per analysis
- **Error patterns**: Common failure points

### Database Queries

Useful Supabase queries:

```sql
-- Recent high-inflation articles
SELECT title, source, (confidence + jargon_density + self_reference + originality) / 4 as eii_score
FROM articles a
JOIN scores s ON a.id = s.article_id
WHERE scored_at > NOW() - INTERVAL '7 days'
ORDER BY eii_score DESC;

-- Analysis by source
SELECT source, AVG((confidence + jargon_density + self_reference + originality) / 4) as avg_eii
FROM articles a
JOIN scores s ON a.id = s.article_id
GROUP BY source
ORDER BY avg_eii DESC;
```

## 🌐 Production Deployment

### Security

- **API Keys**: Never hardcode in workflow, use environment variables
- **Webhook Auth**: Add authentication to webhook if public
- **Rate Limiting**: Implement limits to prevent abuse
- **CORS**: Configure if building web frontend

### Scaling

- **n8n Cloud**: Automatically scales
- **Self-hosted**: Use Docker containers with load balancing
- **Database**: Monitor Supabase usage and upgrade plan as needed

### Backup

- **Export workflow**: Regularly save updated workflow JSON
- **Database backup**: Use Supabase automatic backups
- **Environment vars**: Document all required variables

---

## 🎉 You're Ready!

Your EII workflow is now configured and ready to analyze articles at scale. Start with test URLs and gradually increase usage as you validate the results.

For advanced use cases, consider building a web frontend that calls your webhook, or integrating with tools like Zapier for no-code automation. 