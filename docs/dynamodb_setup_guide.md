# DynamoDB Setup Guide

This guide walks you through setting up AWS DynamoDB for the Expertise Inflation Index (EII) instead of Supabase - perfect for cost optimization!

## 🎯 Why DynamoDB?

- **Cost-effective**: Pay per request, no monthly subscription
- **Serverless**: No infrastructure management
- **Highly scalable**: Handles massive traffic automatically
- **AWS Integration**: Easy to integrate with other AWS services

## 🚀 Quick Setup

### 1. AWS Account Setup

If you don't have an AWS account:
1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Click "Create AWS Account"
3. Follow the registration process

### 2. Install AWS CLI (Optional but Recommended)

```bash
# macOS
brew install awscli

# Windows
pip install awscli

# Configure credentials
aws configure
```

### 3. Get AWS Credentials

**Option A: IAM User (Recommended)**
1. Go to AWS Console → IAM → Users
2. Create new user: `eii-user`
3. Attach policy: `AmazonDynamoDBFullAccess`
4. Create access key
5. Note down:
   - Access Key ID
   - Secret Access Key

**Option B: Temporary Credentials**
1. AWS Console → CloudShell
2. Use temporary session credentials

### 4. Set Environment Variables

Add to your `.env` file:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your-access-key-here
AWS_SECRET_ACCESS_KEY=your-secret-key-here
AWS_REGION=us-east-1

# DynamoDB
DYNAMODB_TABLE_NAME=eii-articles
```

### 5. Create DynamoDB Table

**Option A: Automated Script** (Recommended)
```bash
# Install dependencies first
pip install boto3

# Run setup script
python aws/create_table.py
```

**Option B: Manual via AWS Console**
1. Go to AWS Console → DynamoDB
2. Create table:
   - Table name: `eii-articles`
   - Partition key: `article_id` (String)
   - Settings: On-demand billing
3. Create Global Secondary Index:
   - Index name: `source-scored_at-index`
   - Partition key: `source` (String)
   - Sort key: `scored_at` (String)

## 📊 Data Structure

DynamoDB uses a **single-table design** for optimal performance:

```json
{
  "article_id": "uuid-string",
  "title": "Article Title",
  "source": "example.com",
  "url": "https://example.com/article",
  "author": "Author Name",
  "content": "Full article content...",
  "published_at": "2025-01-01T00:00:00Z",
  "scored_at": "2025-01-01T00:00:00Z",
  "scores": {
    "confidence": 8,
    "jargon_density": 7,
    "self_reference": 6,
    "originality": 9,
    "humor_rating": 2,
    "overall_eii_score": 7.5
  },
  "analysis": {
    "tone_summary": "Confident with technical jargon...",
    "inflation_type": "Technical Guru",
    "key_phrases": ["revolutionary", "paradigm shift"],
    "model_used": "gpt-4"
  }
}
```

## 🔧 n8n Configuration

### Environment Variables for n8n

Set these in your n8n environment:

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1

# API Keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
FIRECRAWL_API_KEY=fc-your-firecrawl-key
```

### Import DynamoDB Workflow

1. In n8n, go to **Workflows**
2. Click **Import from file**
3. Upload `n8n/eii_workflow_dynamodb.json`
4. Configure AWS credentials in n8n settings

## 💰 Cost Estimation

DynamoDB pricing (us-east-1):
- **Write requests**: $1.25 per million requests
- **Read requests**: $0.25 per million requests
- **Storage**: $0.25 per GB per month

**Example monthly costs:**
- 1,000 articles analyzed: ~$0.02
- 10,000 articles analyzed: ~$0.20
- 100,000 articles analyzed: ~$2.00

Much cheaper than most database services! 💰

## 🔍 Querying Your Data

### Using AWS Console
1. Go to DynamoDB → Tables → `eii-articles`
2. Click **Explore table items**
3. Query by partition key or scan all items

### Using AWS CLI
```bash
# Get specific article
aws dynamodb get-item \
  --table-name eii-articles \
  --key '{"article_id":{"S":"your-article-id"}}'

# Query by source
aws dynamodb query \
  --table-name eii-articles \
  --index-name source-scored_at-index \
  --key-condition-expression "source = :source" \
  --expression-attribute-values '{":source":{"S":"example.com"}}'
```

### Using Python (boto3)
```python
import boto3

# Initialize client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('eii-articles')

# Get article
response = table.get_item(Key={'article_id': 'your-article-id'})
article = response.get('Item')

# Query by source
response = table.query(
    IndexName='source-scored_at-index',
    KeyConditionExpression='source = :source',
    ExpressionAttributeValues={':source': 'example.com'}
)
articles = response['Items']

# Get high-inflation articles
response = table.scan(
    FilterExpression='scores.overall_eii_score > :threshold',
    ExpressionAttributeValues={':threshold': 7.0}
)
high_inflation = response['Items']
```

## 📈 Analytics Queries

### Top Overconfident Articles
```python
# Scan for high confidence scores
response = table.scan(
    FilterExpression='scores.confidence >= :high_confidence',
    ExpressionAttributeValues={':high_confidence': 8}
)
```

### Average EII by Source
```python
from collections import defaultdict

# Get all articles
response = table.scan()
articles = response['Items']

# Calculate averages by source
source_scores = defaultdict(list)
for article in articles:
    source = article['source']
    score = article['scores']['overall_eii_score']
    source_scores[source].append(score)

# Average by source
averages = {
    source: sum(scores) / len(scores) 
    for source, scores in source_scores.items()
}
```

## 🛠️ Advanced Features

### Backup and Restore
```bash
# Enable point-in-time recovery
aws dynamodb update-continuous-backups \
  --table-name eii-articles \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true
```

### Auto Scaling (if needed)
```bash
# Enable auto scaling for high-traffic scenarios
aws application-autoscaling register-scalable-target \
  --service-namespace dynamodb \
  --scalable-dimension dynamodb:table:WriteCapacityUnits \
  --resource-id table/eii-articles \
  --min-capacity 5 \
  --max-capacity 100
```

## 🐛 Troubleshooting

### Common Issues

**Access Denied**
- Check IAM permissions
- Verify AWS credentials
- Ensure region matches

**Table Not Found**
- Verify table name in environment variables
- Check region configuration
- Run `aws dynamodb list-tables` to confirm

**Rate Limiting**
- DynamoDB has built-in throttling
- Consider on-demand billing mode
- Add exponential backoff in applications

### Debug Commands

```bash
# Test AWS connection
aws sts get-caller-identity

# List tables
aws dynamodb list-tables

# Describe table
aws dynamodb describe-table --table-name eii-articles

# Check table status
aws dynamodb describe-table --table-name eii-articles \
  --query 'Table.TableStatus'
```

## 🔄 Migration from Supabase

If you were previously using Supabase:

1. **Export existing data** from Supabase
2. **Transform data** to DynamoDB format
3. **Bulk import** using AWS Data Pipeline or scripts
4. **Update n8n workflow** to use DynamoDB version
5. **Test thoroughly** before switching

## 🎉 You're Ready!

Your DynamoDB setup is complete! The EII system now uses:
- ✅ Cost-effective NoSQL storage
- ✅ Serverless architecture
- ✅ Automatic scaling
- ✅ Global secondary indexes for fast queries

Next step: Deploy your n8n workflow and start analyzing articles! 🚀 