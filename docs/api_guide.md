# 🔌 API Integration Guide

The Expertise Inflation Index provides multiple ways to integrate with external systems and automate content analysis workflows.

## 🎯 Overview

The EII system offers several integration points:

1. **Web Dashboard API** - Direct HTTP endpoints for web applications
2. **n8n Webhook API** - Automated workflow triggers  
3. **Python SDK** - Native Python integration
4. **Command Line Interface** - Script automation and batch processing

## 🌐 Web Dashboard API

### Base URL
```
http://localhost:8080  # Development
https://your-domain.com  # Production
```

### Authentication
Currently no authentication required for local deployment. For production use, implement API key authentication.

### Endpoints

#### `POST /api/analyze-article`
Analyze a single article for EII scoring.

**Request Body:**
```json
{
  "url": "https://example.com/article",
  "title": "Optional: Article Title",
  "content": "Optional: Article Content (if not provided, will scrape URL)"
}
```

**Response:**
```json
{
  "success": true,
  "eii_score": 7.2,
  "scores": {
    "confidence": 8,
    "jargon_density": 7,
    "self_reference": 6,
    "originality": 8,
    "humor_rating": 2
  },
  "analysis": {
    "reasoning": "Detailed analysis explanation...",
    "evidence": ["Supporting quotes from the article"],
    "recommendations": ["Suggestions for improvement"]
  },
  "metadata": {
    "author": "John Doe",
    "published_date": "2024-01-15",
    "word_count": 1500,
    "analysis_timestamp": "2024-01-16T10:30:00Z"
  }
}
```

**Example Usage:**
```bash
curl -X POST http://localhost:8080/api/analyze-article \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/ai-article"}'
```

#### `POST /api/demo-discover`
Simulate content discovery for demo purposes.

**Response:**
```json
{
  "success": true,
  "total_found": 46,
  "articles": [
    {
      "title": "Article Title",
      "url": "https://example.com/article",
      "author": "Author Name",
      "published_date": "2024-01-15",
      "excerpt": "Article summary...",
      "relevance_score": 0.85
    }
  ]
}
```

#### `POST /api/demo-analyze`
Run comprehensive team analysis (Trilogy AI demo).

**Response:**
```json
{
  "success": true,
  "results": {
    "analysis_summary": {
      "total_articles_analyzed": 46,
      "total_authors": 4,
      "overall_avg_eii": 6.2,
      "total_anomalies_found": 8
    },
    "author_rankings": [
      {
        "rank": 1,
        "author": "Leonardo Gonzalez",
        "avg_score": 7.4,
        "article_count": 36,
        "consistency": "High"
      }
    ]
  },
  "redirect_url": "/team-championship"
}
```

#### `GET /discovery-report`
View content discovery results with filtering.

**Query Parameters:**
- `source`: Filter by content source (`trilogy`, `rss`, `reddit`, `hackernews`, `semantic_scholar`)

**Response:** HTML page with article listings and analysis options.

### Error Handling

All API endpoints return errors in this format:

```json
{
  "success": false,
  "error": "Error message",
  "error_code": "INVALID_URL",
  "details": {
    "field": "url",
    "message": "URL format is invalid"
  }
}
```

**Common Error Codes:**
- `INVALID_URL` - Malformed or inaccessible URL
- `CONTENT_NOT_FOUND` - Unable to extract content from URL
- `API_RATE_LIMIT` - Too many requests (if rate limiting enabled)
- `ANALYSIS_FAILED` - LLM analysis failed
- `INTERNAL_ERROR` - Server error

## 🔄 n8n Webhook API

The n8n workflow provides a production-ready webhook endpoint for automated analysis.

### Webhook URL
```
https://your-n8n-instance.com/webhook/eii-analyze
```

### Request Format
```json
{
  "url": "https://example.com/article",
  "metadata": {
    "source": "manual",
    "submitted_by": "user@example.com",
    "tags": ["ai", "analysis"]
  }
}
```

### Response Format
```json
{
  "status": "success",
  "analysis_id": "uuid-here",
  "eii_score": 7.2,
  "scores": {
    "confidence": 8,
    "jargon_density": 7,
    "self_reference": 6,
    "originality": 8,
    "humor_rating": 2
  },
  "storage": {
    "dynamodb_item_id": "article-uuid",
    "created_at": "2024-01-16T10:30:00Z"
  }
}
```

### Workflow Steps
1. **Webhook Trigger** - Receives article URL
2. **Firecrawl Scraping** - Extracts article content
3. **OpenAI Analysis** - GPT-4 scoring and analysis
4. **Anthropic Analysis** - Claude scoring and analysis  
5. **Results Aggregation** - Combine and weight scores
6. **DynamoDB Storage** - Store results for future queries
7. **Response** - Return analysis results

## 🐍 Python SDK

### Installation
```bash
# Install the EII package (when available)
pip install expertise-inflation-index

# Or use the local modules
from content_discovery import ContentDiscovery
from web_dashboard import analyze_article
```

### Basic Usage
```python
from eii import ExpertiseInflationIndex

# Initialize the EII client
eii = ExpertiseInflationIndex(
    openai_key="your-openai-key",
    anthropic_key="your-anthropic-key"
)

# Analyze a single article
result = eii.analyze_article("https://example.com/article")
print(f"EII Score: {result.eii_score}")
print(f"Confidence: {result.scores.confidence}")

# Batch analysis
articles = [
    "https://example.com/article1",
    "https://example.com/article2"
]
results = eii.analyze_batch(articles)

# Content discovery
discovery = eii.discover_content(
    sources=["rss", "reddit"],
    limit=10,
    keywords=["artificial intelligence"]
)
```

### Advanced Usage
```python
# Custom scoring weights
eii.set_scoring_weights({
    "confidence": 0.3,
    "jargon_density": 0.2,
    "self_reference": 0.2,
    "originality": 0.2,
    "humor_rating": 0.1
})

# Custom prompts
eii.set_custom_prompt("path/to/custom_prompt.txt")

# Team analysis
team_results = eii.analyze_team(
    articles=article_urls,
    group_by="author"
)
```

## 🖥️ Command Line Interface

### Article Analysis
```bash
# Analyze single article
python -m eii analyze https://example.com/article

# Batch analysis from file
python -m eii analyze --file article_urls.txt

# Output to JSON
python -m eii analyze https://example.com/article --output results.json
```

### Content Discovery
```bash
# Discover from all sources
python content_discovery.py --source all --limit 20

# Specific source with keywords
python content_discovery.py --source reddit --keywords "AI,machine learning" --limit 10

# Save results
python content_discovery.py --source trilogy --output trilogy_articles.json
```

### Team Analysis
```bash
# Analyze Trilogy AI team
python trilogy_team_analysis.py

# Custom team analysis
python -m eii team-analyze --articles articles.json --group-by author
```

### Testing
```bash
# Test prompts
python test_prompt.py

# Test full workflow
python test_workflow.py

# Test specific component
python -m eii test content-discovery
```

## 📊 Data Formats

### Article Object
```json
{
  "title": "Article Title",
  "url": "https://example.com/article",
  "author": "Author Name", 
  "published_date": "2024-01-15T10:00:00Z",
  "content": "Full article text...",
  "excerpt": "Brief summary...",
  "word_count": 1500,
  "source": "rss|reddit|hackernews|trilogy|manual",
  "tags": ["ai", "analysis"],
  "relevance_score": 0.85
}
```

### Analysis Result Object
```json
{
  "eii_score": 7.2,
  "scores": {
    "confidence": 8,
    "jargon_density": 7, 
    "self_reference": 6,
    "originality": 8,
    "humor_rating": 2
  },
  "analysis": {
    "reasoning": "Detailed explanation...",
    "evidence": ["Quote 1", "Quote 2"],
    "recommendations": ["Suggestion 1", "Suggestion 2"]
  },
  "metadata": {
    "model_used": "gpt-4+claude-3",
    "analysis_version": "1.0",
    "processing_time_ms": 3500,
    "confidence_level": 0.92
  }
}
```

### Team Analysis Object
```json
{
  "team_summary": {
    "total_articles": 46,
    "team_avg_eii": 6.2,
    "most_productive": "Leonardo Gonzalez",
    "inflation_champion": "Leonardo Gonzalez"
  },
  "author_stats": {
    "Leonardo Gonzalez": {
      "article_count": 36,
      "avg_eii_score": 7.4,
      "consistency": "High",
      "anomalies": 2
    }
  },
  "rankings": {
    "highest_avg_eii": ["Leonardo Gonzalez", "Stanislav Huseletov"],
    "most_consistent": ["David Proctor", "Praveen Koka"]
  }
}
```

## 🔗 Integration Examples

### Slack Bot Integration
```python
from slack_sdk import WebClient
from eii import ExpertiseInflationIndex

def analyze_article_command(event, say):
    url = event['text'].split()[1]  # Get URL from command
    
    # Analyze with EII
    eii = ExpertiseInflationIndex()
    result = eii.analyze_article(url)
    
    # Format response
    message = f"""
    📊 *EII Analysis Results*
    
    *Article*: {result.title}
    *EII Score*: {result.eii_score}/10
    
    *Breakdown*:
    • Confidence: {result.scores.confidence}/10
    • Jargon: {result.scores.jargon_density}/10  
    • Self-Reference: {result.scores.self_reference}/10
    • Originality: {result.scores.originality}/10
    • Humor: {result.scores.humor_rating}/10
    """
    
    say(message)
```

### WordPress Plugin Integration
```php
<?php
function eii_analyze_post($post_content) {
    $api_url = 'http://your-eii-instance.com/api/analyze-article';
    
    $data = array(
        'content' => $post_content,
        'title' => get_the_title()
    );
    
    $response = wp_remote_post($api_url, array(
        'headers' => array('Content-Type' => 'application/json'),
        'body' => json_encode($data)
    ));
    
    return json_decode(wp_remote_retrieve_body($response), true);
}

// Add EII meta box to post editor
add_action('add_meta_boxes', 'add_eii_meta_box');
function add_eii_meta_box() {
    add_meta_box(
        'eii-analysis',
        'EII Content Analysis', 
        'eii_meta_box_callback',
        'post'
    );
}
?>
```

### GitHub Action Integration
```yaml
name: EII Content Analysis
on: 
  pull_request:
    paths: ['docs/**', '*.md']

jobs:
  analyze-content:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Analyze Documentation Changes
        run: |
          # Get changed files
          git diff --name-only HEAD^ HEAD | grep -E '\.(md|rst)$' | while read file; do
            # Analyze each changed documentation file
            curl -X POST ${{ secrets.EII_API_URL }}/api/analyze-article \
              -H "Content-Type: application/json" \
              -d "{\"content\": \"$(cat $file)\"}" \
              >> eii_results.json
          done
          
      - name: Comment PR with Results
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('eii_results.json'));
            
            let comment = '## 📊 EII Content Analysis Results\n\n';
            results.forEach(result => {
              comment += `### ${result.title}\n`;
              comment += `**EII Score**: ${result.eii_score}/10\n`;
              comment += `**Suggestions**: ${result.analysis.recommendations.join(', ')}\n\n`;
            });
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

## ⚡ Performance Considerations

### Rate Limiting
- **OpenAI API**: 3 requests/minute (free tier)
- **Anthropic API**: 5 requests/minute (free tier)
- **Firecrawl API**: 20 requests/minute (free tier)

### Caching
- **Article Content**: Cache scraped content for 24 hours
- **Analysis Results**: Cache EII scores for 7 days  
- **Content Discovery**: Cache source feeds for 1 hour

### Optimization Tips
1. **Batch Processing**: Group multiple articles together
2. **Async Processing**: Use background jobs for large batches
3. **Result Caching**: Store and reuse analysis results
4. **Content Deduplication**: Check for existing analyses before processing

## 🔒 Security Best Practices

### API Key Management
- Store API keys in environment variables
- Use different keys for development/production
- Implement key rotation policies
- Monitor API usage and costs

### Input Validation
- Validate all URLs before processing
- Sanitize content inputs
- Implement CORS policies for web APIs
- Use HTTPS for all API communications

### Error Handling
- Never expose internal errors to users
- Implement proper logging and monitoring
- Use rate limiting to prevent abuse
- Validate all inputs and responses

---

## 🚀 Getting Started

1. **Quick Test**: Start with the web dashboard API for immediate results
2. **Automation**: Set up n8n workflows for production use
3. **Integration**: Use the Python SDK for custom applications
4. **Scaling**: Implement proper caching and error handling

For detailed setup instructions, see the [Setup Guide](../SETUP.md).

For production deployment, see the [Infrastructure Guides](./dynamodb_setup_guide.md).

---

**💡 Need Help?** Check out our [examples directory](../examples/) for more integration samples, or submit an issue on GitHub for support! 