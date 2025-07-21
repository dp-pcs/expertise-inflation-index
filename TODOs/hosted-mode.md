# 🌐 Hosted Mode Deployment Guide

Transform your local EII instance into a production-ready hosted service.

## 🎯 Deployment Options

### 1. Quick Deploy (Recommended for Testing)

#### Heroku
```bash
# Install Heroku CLI
npm install -g heroku

# Create Heroku app
heroku create your-eii-app

# Set environment variables
heroku config:set OPENAI_API_KEY=your_key
heroku config:set ANTHROPIC_API_KEY=your_key
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main
```

#### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### DigitalOcean App Platform
1. Connect your GitHub repository
2. Configure environment variables
3. Deploy with one click

### 2. Self-Hosted (Production)

#### VPS with Docker
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["python", "web_dashboard.py", "--port", "8080", "--host", "0.0.0.0"]
```

```bash
# Deploy to VPS
docker build -t eii-app .
docker run -d -p 80:8080 --env-file .env eii-app
```

#### Kubernetes
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: eii-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: eii-app
  template:
    metadata:
      labels:
        app: eii-app
    spec:
      containers:
      - name: eii-app
        image: your-registry/eii-app:latest
        ports:
        - containerPort: 8080
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: eii-secrets
              key: openai-key
```

### 3. Cloud Functions/Serverless

#### AWS Lambda
```bash
# Install Zappa
pip install zappa

# Configure zappa_settings.json
{
    "dev": {
        "app_function": "web_dashboard.app",
        "aws_region": "us-east-1",
        "profile_name": "default",
        "project_name": "eii-lambda",
        "runtime": "python3.9",
        "s3_bucket": "your-lambda-bucket"
    }
}

# Deploy
zappa deploy dev
```

#### Vercel
```json
{
  "functions": {
    "api/analyze.py": {
      "runtime": "python3.9"
    }
  },
  "env": {
    "OPENAI_API_KEY": "@openai-key",
    "ANTHROPIC_API_KEY": "@anthropic-key"
  }
}
```

## 🔒 Production Configuration

### Environment Variables
```env
# Required
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Production settings
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secure-secret-key

# Database
DATABASE_URL=your_database_url
REDIS_URL=your_redis_url  # For caching

# Security
ALLOWED_HOSTS=your-domain.com,api.your-domain.com
CORS_ORIGINS=https://your-frontend.com

# Rate limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Monitoring
SENTRY_DSN=your_sentry_dsn
LOG_LEVEL=INFO
```

### Database Migration
```python
# production_setup.py
import os
import boto3
from web_dashboard import create_dynamodb_table

def setup_production_db():
    """Set up production database tables"""
    
    # DynamoDB setup
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    create_dynamodb_table(dynamodb, 'eii-production')
    
    # Redis setup for caching
    import redis
    redis_client = redis.from_url(os.getenv('REDIS_URL'))
    redis_client.ping()  # Test connection
    
    print("✅ Production database setup complete")

if __name__ == "__main__":
    setup_production_db()
```

### Load Balancing & Scaling
```nginx
# nginx.conf
upstream eii_app {
    server app1.your-domain.com:8080;
    server app2.your-domain.com:8080;
    server app3.your-domain.com:8080;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://eii_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://eii_app;
    }
}
```

## 🔐 Security Hardening

### API Key Management
```python
# utils/security.py
import os
import hashlib
import secrets
from functools import wraps
from flask import request, jsonify

def generate_api_key():
    """Generate secure API key for users"""
    return secrets.token_urlsafe(32)

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not validate_api_key(api_key):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

def validate_api_key(api_key):
    """Validate API key against database"""
    # Implementation depends on your user management system
    pass
```

### Rate Limiting
```python
# utils/rate_limiting.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

# Redis-backed rate limiting
redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))

limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri=os.getenv('REDIS_URL', 'redis://localhost:6379'),
    default_limits=["1000 per hour", "100 per minute"]
)

# Apply to routes
@app.route('/api/analyze-article', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key
def analyze_article():
    # Implementation
    pass
```

### Input Validation
```python
# utils/validation.py
from urllib.parse import urlparse
import validators
from werkzeug.datastructures import FileStorage

def validate_url(url):
    """Validate and sanitize URL input"""
    if not url or not isinstance(url, str):
        return False, "URL is required"
    
    if not validators.url(url):
        return False, "Invalid URL format"
    
    parsed = urlparse(url)
    if parsed.scheme not in ['http', 'https']:
        return False, "Only HTTP/HTTPS URLs allowed"
    
    # Block internal/private IPs
    if parsed.hostname in ['localhost', '127.0.0.1']:
        return False, "Local URLs not allowed"
    
    return True, url

def validate_content(content):
    """Validate article content"""
    if not content or not isinstance(content, str):
        return False, "Content is required"
    
    if len(content) > 100000:  # 100KB limit
        return False, "Content too large"
    
    if len(content) < 100:  # Minimum content length
        return False, "Content too short for analysis"
    
    return True, content
```

## 📊 Monitoring & Analytics

### Health Checks
```python
# routes/health.py
@app.route('/health')
def health_check():
    """System health check endpoint"""
    status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'checks': {}
    }
    
    # Check database connectivity
    try:
        # Test DynamoDB connection
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('eii-production')
        table.item_count  # This will fail if table doesn't exist
        status['checks']['database'] = 'healthy'
    except Exception as e:
        status['checks']['database'] = f'unhealthy: {str(e)}'
        status['status'] = 'unhealthy'
    
    # Check external APIs
    try:
        import openai
        openai.api_key = os.getenv('OPENAI_API_KEY')
        # Make test request
        status['checks']['openai'] = 'healthy'
    except Exception as e:
        status['checks']['openai'] = f'unhealthy: {str(e)}'
    
    return jsonify(status), 200 if status['status'] == 'healthy' else 503
```

### Logging & Metrics
```python
# utils/monitoring.py
import logging
import structlog
from prometheus_client import Counter, Histogram, generate_latest
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Prometheus metrics
request_count = Counter('eii_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('eii_request_duration_seconds', 'Request duration')
analysis_count = Counter('eii_analyses_total', 'Total analyses', ['source'])

# Sentry error tracking
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1
)

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': 'text/plain'}
```

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          pytest tests/ --cov=web_dashboard
          
      - name: Security scan
        run: |
          pip install bandit safety
          bandit -r .
          safety check

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to production
        run: |
          # Your deployment script here
          ./scripts/deploy.sh
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### Deployment Script
```bash
#!/bin/bash
# scripts/deploy.sh

set -e  # Exit on any error

echo "🚀 Starting deployment..."

# Build and tag Docker image
docker build -t eii-app:latest .
docker tag eii-app:latest your-registry/eii-app:$(git rev-parse --short HEAD)

# Push to registry
docker push your-registry/eii-app:$(git rev-parse --short HEAD)

# Update Kubernetes deployment
kubectl set image deployment/eii-app eii-app=your-registry/eii-app:$(git rev-parse --short HEAD)
kubectl rollout status deployment/eii-app

# Run database migrations if needed
kubectl exec -it deployment/eii-app -- python production_setup.py

echo "✅ Deployment complete!"
```

## 💰 Cost Optimization

### Resource Allocation
- **Small Scale** (< 1K requests/day): Single server, minimal resources
- **Medium Scale** (1K-10K requests/day): Load balancer + 2-3 app servers
- **Large Scale** (10K+ requests/day): Auto-scaling, CDN, database replicas

### Caching Strategy
```python
# utils/caching.py
import redis
import json
from functools import wraps

redis_client = redis.from_url(os.getenv('REDIS_URL'))

def cache_result(expiry=3600):
    """Cache function results in Redis"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{f.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            redis_client.setex(cache_key, expiry, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(expiry=86400)  # Cache for 24 hours
def analyze_article_cached(url):
    """Cached version of article analysis"""
    return analyze_article(url)
```

## 🌍 Global Deployment

### Multi-Region Setup
```python
# config/regions.py
REGIONS = {
    'us-east-1': {
        'database': 'dynamodb-us-east-1',
        'redis': 'redis-us-east-1.amazonaws.com',
        'cdn': 'cloudfront-us-east-1'
    },
    'eu-west-1': {
        'database': 'dynamodb-eu-west-1', 
        'redis': 'redis-eu-west-1.amazonaws.com',
        'cdn': 'cloudfront-eu-west-1'
    }
}

def get_region_config():
    """Get configuration for current region"""
    region = os.getenv('AWS_REGION', 'us-east-1')
    return REGIONS.get(region, REGIONS['us-east-1'])
```

### CDN Configuration
```javascript
// cloudfront-config.js
{
  "Origins": [{
    "Id": "eii-api-origin",
    "DomainName": "api.your-domain.com",
    "CustomOriginConfig": {
      "HTTPPort": 80,
      "HTTPSPort": 443,
      "OriginProtocolPolicy": "https-only"
    }
  }],
  "DefaultCacheBehavior": {
    "TargetOriginId": "eii-api-origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "CachePolicyId": "custom-api-cache-policy",
    "TTL": 3600
  },
  "CacheBehaviors": [{
    "PathPattern": "/api/analyze*",
    "TTL": 86400,  // Cache analysis results for 24 hours
    "ForwardedHeaders": ["Authorization", "X-API-Key"]
  }]
}
```

---

## 🚀 Quick Start Hosted Deploy

### 1-Click Railway Deploy
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/your-template-id)

### Heroku Deploy Button
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/your-username/expertise-inflation-index)

### Environment Template
```env
# Copy to your hosting platform's environment variables
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
FLASK_ENV=production
SECRET_KEY=your_secure_random_secret
DATABASE_URL=your_database_url
REDIS_URL=your_redis_url
```

---

**🎯 Pro Tips:**
1. Start with a simple hosted solution (Railway/Heroku) for testing
2. Implement proper monitoring before scaling
3. Use managed services (RDS, ElastiCache) to reduce operational overhead
4. Set up proper backup and disaster recovery procedures
5. Monitor costs closely - LLM API calls can add up quickly!
