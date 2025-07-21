# 🚀 Quick Setup Guide

Get the Expertise Inflation Index running in under 10 minutes!

## 📋 Prerequisites

- **Python 3.8+** (check with `python --version`)
- **Git** for cloning the repository
- **Text editor** or IDE of your choice

## 🏃‍♂️ 5-Minute Demo Setup

### 1. Clone and Install
```bash
# Clone the repository
git clone https://github.com/dp-pcs/expertise-inflation-index.git
cd expertise-inflation-index

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Start the Web Dashboard
```bash
# Launch the interactive dashboard
python web_dashboard.py --port 8080
```

### 3. Explore the Demo
Open your browser and visit:
- **Main Dashboard**: http://localhost:8080
- **Interactive Demo**: http://localhost:8080/demo
- **Team Championship**: http://localhost:8080/team-championship
- **Discovery Reports**: http://localhost:8080/discovery-report

🎉 **That's it!** You now have a fully functional EII system with sample data.

## 🔧 Full Setup (with API Keys)

For live analysis of new articles, you'll need API keys:

### 1. Get API Keys
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Firecrawl**: https://firecrawl.dev/app/api-keys (optional for live scraping)

### 2. Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit with your API keys
nano .env  # or use your preferred editor
```

Required variables:
```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
FIRECRAWL_API_KEY=your_firecrawl_key_here  # Optional
```

### 3. Test the AI Analysis
```bash
# Run the prompt test suite
python test_prompt.py
```

This validates your API keys and shows sample EII scores.

### 4. Test Content Discovery
```bash
# Discover articles from various sources
python content_discovery.py --source trilogy --limit 5

# Test with multiple sources
python content_discovery.py --source all --limit 10
```

### 5. Run Team Analysis
```bash
# Analyze the Trilogy AI team (sample data)
python trilogy_team_analysis.py
```

## 🌐 Production Setup (Optional)

For production use with real-time analysis:

### Database Setup (Choose One)

#### Option A: DynamoDB (Recommended - Cost Effective)
```bash
# Install AWS CLI and configure credentials
pip install awscli
aws configure

# Create DynamoDB table
python aws/create_table.py
```

#### Option B: Supabase (Legacy)
1. Sign up at https://supabase.com
2. Create a new project
3. Import `supabase/schema.sql`
4. Add Supabase credentials to `.env`

### Automation Setup (n8n)

#### Option A: n8n Cloud (Easiest)
1. Sign up at https://n8n.io
2. Import `n8n/eii_workflow_dynamodb.json`
3. Configure your API keys in n8n

#### Option B: Self-Hosted n8n
```bash
# Install n8n globally
npm install n8n -g

# Start n8n
n8n start

# Visit http://localhost:5678
# Import n8n/eii_workflow_dynamodb.json
```

## 🧪 Verification Steps

### Test the Complete Pipeline
```bash
# Run end-to-end test
python test_workflow.py
```

### Test Individual Components
```bash
# Test prompt only
python test_prompt.py

# Test content discovery
python content_discovery.py --source trilogy --limit 3

# Test web dashboard
python web_dashboard.py --port 8080
```

### Expected Results
- ✅ Web dashboard loads without errors
- ✅ Demo presentation runs smoothly
- ✅ Content discovery finds articles
- ✅ AI analysis returns structured scores
- ✅ Team championship displays results

## 🎯 Quick Feature Tour

### Interactive Demo (`/demo`)
- Step-by-step presentation of how EII works
- Simulated article discovery and analysis
- Shows the AI development process
- Links to team championship results

### Team Championship (`/team-championship`)
- Compare authors across multiple articles
- View aggregate statistics and anomalies
- See individual article breakdowns
- Rankings and leaderboards

### Discovery Reports (`/discovery-report`)
- Browse articles from different sources
- Filter by content type (RSS, Reddit, Hacker News, etc.)
- Submit articles for analysis
- View source-specific statistics

### Real-time Analysis
- Submit any article URL for instant scoring
- Dual-LLM analysis (OpenAI + Anthropic)
- Structured JSON results
- Integrated with web dashboard

## 🐛 Troubleshooting

### Common Issues

**"Module not found" errors**:
```bash
# Make sure you're in the right directory
cd expertise-inflation-index

# Reinstall dependencies
pip install -r requirements.txt
```

**"Permission denied" errors**:
```bash
# On macOS/Linux, you might need:
python3 web_dashboard.py --port 8080
```

**Port already in use**:
```bash
# Try a different port
python web_dashboard.py --port 8081
```

**API key errors**:
- Double-check your `.env` file formatting
- Ensure no extra spaces around the `=` sign
- Verify API keys are active and have sufficient credits

### Getting Help

1. **Check the logs**: The web dashboard shows error messages in the terminal
2. **Review documentation**: Each feature has detailed guides in `docs/`
3. **Test components individually**: Use the test scripts to isolate issues
4. **Submit an issue**: https://github.com/dp-pcs/expertise-inflation-index/issues

## 📚 Next Steps

Once you have the basic system running:

1. **Explore the Code**: Start with `web_dashboard.py` and `content_discovery.py`
2. **Customize Prompts**: Edit files in the `prompts/` directory
3. **Add Content Sources**: Extend `content_discovery.py` with new APIs
4. **Build Integrations**: Use the n8n workflows as a starting point
5. **Deploy to Production**: Follow the infrastructure guides in `docs/`

## 🎪 Demo Scenarios

### Scenario 1: Content Analysis Team
- Use `/discovery-report` to find articles
- Analyze individual articles for quality control
- Build content guidelines based on EII scores

### Scenario 2: Research Team
- Import academic papers via content discovery
- Compare writing styles across authors
- Identify accessibility issues in technical writing

### Scenario 3: Marketing Team
- Analyze competitor content for tone and positioning
- Monitor brand voice consistency
- Track industry expertise inflation trends

### Scenario 4: Educational Use
- Score student essays for clarity and confidence
- Identify overuse of jargon in course materials
- Provide feedback on academic writing

## 🔗 Additional Resources

- **[Full Documentation](docs/)** - Complete setup guides for each component
- **[Replication Guide](REPLICATION_GUIDE.md)** - Step-by-step deployment instructions
- **[Example Articles](examples/)** - Sample content for testing different scenarios
- **[API Documentation](docs/api_guide.md)** - For building custom integrations

---

**🎯 Pro Tip**: Start with the interactive demo (`/demo`) to understand how all the pieces fit together, then dive into the specific components you want to customize! 