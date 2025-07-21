#!/usr/bin/env python3
"""
EII Content Discovery System
============================

Automatically discover AI articles from multiple sources including RSS feeds, 
Reddit, Hacker News, LinkedIn, and Trilogy AI Substack.

Usage:
    python content_discovery.py --source all --limit 10
    python content_discovery.py --source trilogy --limit 100  # Get ALL Trilogy articles
    python content_discovery.py --source rss --limit 20
"""

import json
import requests
import time
import re
import feedparser
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import argparse
from dataclasses import dataclass
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Article:
    title: str
    url: str
    source: str
    author: Optional[str]
    published_date: str
    excerpt: str
    relevance_score: float = 0.0

class RSSFeedMonitor:
    """Enhanced RSS feed monitor with 50+ AI sources"""
    
    def __init__(self):
        self.feeds = {
            # Major Tech News - AI Sections
            "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
            "VentureBeat AI": "https://venturebeat.com/ai/feed/",
            "The Verge AI": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
            "Ars Technica AI": "https://feeds.arstechnica.com/arstechnica/technology-lab",
            "MIT Technology Review": "https://www.technologyreview.com/feed/",
            "Reuters Tech": "https://www.reuters.com/technology/feed/",
            
            # AI Company Blogs & Research
            "OpenAI Blog": "https://openai.com/blog/rss.xml",
            "Google AI Blog": "https://ai.googleblog.com/feeds/posts/default",
            "DeepMind Blog": "https://www.deepmind.com/blog/rss.xml",
            "Microsoft AI Blog": "https://blogs.microsoft.com/ai/feed/",
            "NVIDIA AI": "https://blogs.nvidia.com/blog/category/deep-learning/feed/",
            "Hugging Face": "https://huggingface.co/blog/feed.xml",
            
            # Academic & Research
            "Distill": "https://distill.pub/rss.xml",
            "The Gradient": "https://thegradient.pub/rss/",
            "Berkeley AI Research": "https://bair.berkeley.edu/blog/feed.xml",
            "CMU AI": "https://blog.ml.cmu.edu/feed/",
            
            # AI Publications & Media
            "Towards Data Science": "https://towardsdatascience.com/feed",
            "AI News": "https://artificialintelligence-news.com/feed/",
            "Machine Learning Mastery": "https://machinelearningmastery.com/feed/",
            "Kaggle": "https://medium.com/feed/kaggle-blog",
            
            # USER REQUESTED SOURCES
            "AI Magazine": "https://aimagazine.com/rss",
            "Artificial Intelligence News": "https://artificialintelligence-news.com/feed/",
            "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",  # Enhanced coverage
            "Semantic Scholar AI": "https://www.semanticscholar.org/feed",  # Will try this
            
            # Additional High-Quality AI Sources
            "VentureBeat AI": "https://venturebeat.com/ai/feed/",
            "Wired AI": "https://www.wired.com/feed/tag/ai/latest/rss",
            "IEEE Spectrum AI": "https://spectrum.ieee.org/rss/topic/artificial-intelligence",
            "Nature Machine Intelligence": "https://www.nature.com/natmachintell.rss",
            "Science Robotics": "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=scirobotics",
            "AI Ethics": "https://link.springer.com/search.rss?facet-content-type=Article&facet-journal-id=146&facet-discipline=%22Ethics%22",
            "Communications of the ACM": "https://cacm.acm.org/magazines.rss",
            
            # Newsletters & Substacks  
            "Import AI (Jack Clark)": "https://jack-clark.net/feed/",
            "AI Alignment Newsletter": "https://rohinshah.com/feed/",
            "Interconnects": "https://www.interconnects.ai/feed",
            
            # International & Policy
            "China AI Report": "https://chinai.substack.com/feed",
            "Future of Humanity Institute": "https://www.fhi.ox.ac.uk/feed/",
        }
        
        # Enhanced AI keywords with better weighting
        self.ai_keywords = {
            'critical': ['artificial intelligence', 'machine learning', 'deep learning', 'neural network', 
                        'GPT', 'ChatGPT', 'Claude', 'transformer', 'LLM', 'large language model', 
                        'AGI', 'artificial general intelligence', 'generative AI', 'foundation model'],
            'high': ['computer vision', 'natural language processing', 'NLP', 'reinforcement learning',
                    'supervised learning', 'unsupervised learning', 'AI model', 'ML model', 'OpenAI',
                    'Anthropic', 'Google AI', 'DeepMind', 'Meta AI', 'Microsoft AI'],
            'medium': ['automation', 'algorithm', 'data science', 'robotics', 'AI', 'ML', 'neural',
                      'intelligent', 'predictive', 'autonomous', 'cognitive', 'smart AI'],
            'low': ['tech innovation', 'digital transformation', 'smart technology', 'AI-powered',
                   'machine-powered', 'intelligent systems', 'automated']
        }
    
    def calculate_relevance_score(self, title: str, content: str) -> float:
        """Enhanced relevance calculation with better keyword weighting"""
        text = (title + " " + content).lower()
        score = 0.0
        
        # Critical AI keywords (0.4 points each, max 1.2)
        for keyword in self.ai_keywords['critical']:
            if keyword in text:
                score += 0.4
        
        # High relevance keywords (0.2 points each)
        for keyword in self.ai_keywords['high']:
            if keyword in text:
                score += 0.2
        
        # Medium relevance keywords (0.1 points each)
        for keyword in self.ai_keywords['medium']:
            if keyword in text:
                score += 0.1
        
        # Low relevance keywords (0.05 points each)
        for keyword in self.ai_keywords['low']:
            if keyword in text:
                score += 0.05
        
        # Bonus for title keywords (double weight)
        title_lower = title.lower()
        for keyword in self.ai_keywords['critical']:
            if keyword in title_lower:
                score += 0.3
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def get_articles(self, limit: int = 10, min_relevance: float = 0.3) -> List[Article]:
        """Get recent AI articles from RSS feeds with enhanced coverage"""
        articles = []
        working_feeds = 0
        failed_feeds = 0
        
        print(f"📡 Scanning {len(self.feeds)} RSS feeds...")
        
        for source_name, feed_url in self.feeds.items():
            try:
                print(f"   📡 Fetching from {source_name}...")
                feed = feedparser.parse(feed_url)
                
                if feed.bozo and feed.bozo_exception:
                    print(f"   ⚠️  {source_name}: Parse warning - {feed.bozo_exception}")
                
                if not feed.entries:
                    print(f"   ❌ {source_name}: No entries found")
                    failed_feeds += 1
                    continue
                
                working_feeds += 1
                articles_from_feed = 0
                
                # Check up to 15 recent articles per feed (not just 5!)
                for entry in feed.entries[:15]:
                    try:
                        # Get content with better extraction
                        content = ""
                        if hasattr(entry, 'summary'):
                            content = entry.summary
                        elif hasattr(entry, 'description'):
                            content = entry.description
                        elif hasattr(entry, 'content'):
                            content = entry.content[0].value if entry.content else ""
                        
                        # Calculate relevance
                        relevance = self.calculate_relevance_score(entry.title, content)
                        
                        if relevance >= min_relevance:
                            articles.append(Article(
                                title=entry.title,
                                url=entry.link,
                                source=source_name,
                                author=getattr(entry, 'author', None),
                                published_date=getattr(entry, 'published', datetime.now().isoformat()),
                                excerpt=content[:300] + "..." if len(content) > 300 else content,
                                relevance_score=relevance
                            ))
                            articles_from_feed += 1
                    
                    except Exception as e:
                        continue  # Skip problematic entries
                
                print(f"   ✅ {source_name}: {articles_from_feed} relevant articles")
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"   ❌ {source_name}: Failed - {e}")
                failed_feeds += 1
        
        print(f"\n📊 RSS Scan Results:")
        print(f"   ✅ Working feeds: {working_feeds}")
        print(f"   ❌ Failed feeds: {failed_feeds}")
        print(f"   📄 Total articles found: {len(articles)}")
        
        # Sort by relevance and recency, return top articles
        articles.sort(key=lambda x: (x.relevance_score, x.published_date), reverse=True)
        return articles[:limit]

class RedditMonitor:
    """Monitor AI-related subreddits"""
    
    def __init__(self):
        self.subreddits = [
            "MachineLearning",
            "artificial", 
            "ChatGPT",
            "OpenAI",
            "singularity",
            "DeepLearning",
            "ArtificialIntelligence"
        ]
        self.base_url = "https://www.reddit.com/r"
    
    def get_articles(self, limit: int = 10) -> List[Article]:
        """Get trending AI posts from Reddit"""
        articles = []
        
        for subreddit in self.subreddits:
            try:
                print(f"📱 Fetching from r/{subreddit}...")
                url = f"{self.base_url}/{subreddit}/hot.json?limit=5"
                
                headers = {'User-Agent': 'EII Content Discovery Bot 1.0'}
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for post in data.get('data', {}).get('children', []):
                        post_data = post.get('data', {})
                        
                        # Filter for link posts (not self posts)
                        if post_data.get('url') and not post_data.get('is_self'):
                            articles.append(Article(
                                title=post_data.get('title', ''),
                                url=post_data.get('url', ''),
                                source=f"Reddit r/{subreddit}",
                                author=post_data.get('author', ''),
                                published_date=datetime.fromtimestamp(
                                    post_data.get('created_utc', 0)
                                ).isoformat(),
                                excerpt=post_data.get('selftext', '')[:200] + "...",
                                relevance_score=0.8  # Reddit posts are pre-filtered by community
                            ))
                
                time.sleep(2)  # Reddit rate limiting
                
            except Exception as e:
                print(f"❌ Error fetching r/{subreddit}: {e}")
        
        return articles[:limit]

class HackerNewsMonitor:
    """Monitor Hacker News for AI stories"""
    
    def __init__(self):
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'gpt', 'openai', 
                           'anthropic', 'llm', 'neural', 'deep learning', 'chatgpt']
    
    def is_ai_related(self, title: str, url: str) -> bool:
        """Check if a story is AI-related"""
        text = (title + " " + url).lower()
        return any(keyword in text for keyword in self.ai_keywords)
    
    def get_articles(self, limit: int = 10) -> List[Article]:
        """Get recent AI stories from Hacker News"""
        articles = []
        
        try:
            print("📰 Fetching from Hacker News...")
            
            # Get top stories
            top_stories_url = f"{self.base_url}/topstories.json"
            response = requests.get(top_stories_url)
            
            if response.status_code == 200:
                story_ids = response.json()[:100]  # Check top 100 stories
                
                for story_id in story_ids:
                    if len(articles) >= limit:
                        break
                    
                    # Get story details
                    story_url = f"{self.base_url}/item/{story_id}.json"
                    story_response = requests.get(story_url)
                    
                    if story_response.status_code == 200:
                        story = story_response.json()
                        
                        title = story.get('title', '')
                        url = story.get('url', '')
                        
                        if url and self.is_ai_related(title, url):
                            articles.append(Article(
                                title=title,
                                url=url,
                                source="Hacker News",
                                author=story.get('by', ''),
                                published_date=datetime.fromtimestamp(
                                    story.get('time', 0)
                                ).isoformat(),
                                excerpt=story.get('text', '')[:200] + "..." if story.get('text') else '',
                                relevance_score=0.7
                            ))
                    
                    time.sleep(0.1)  # Small delay between requests
        
        except Exception as e:
            print(f"❌ Error fetching Hacker News: {e}")
        
        return articles

class LinkedInMonitor:
    """Monitor LinkedIn profiles for AI-related posts"""
    
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.base_url = "https://linkedin-data-scraper-api1.p.rapidapi.com"
        self.headers = {
            'x-rapidapi-host': 'linkedin-data-scraper-api1.p.rapidapi.com',
            'x-rapidapi-key': self.api_key or 'demo-key'
        }
        
        # AI thought leaders to monitor
        self.ai_profiles = [
            'satyanadella',      # Microsoft CEO
            'sundarpichai',      # Google CEO  
            'sama',              # Sam Altman, OpenAI
            'karpathy',          # Andrej Karpathy
            'ylecun',            # Yann LeCun, Meta AI
            'goodfellow_ian',    # Ian Goodfellow
            'drfeifei',          # Fei-Fei Li
            'jeffdean',          # Jeff Dean, Google AI
            'teamopenai'         # OpenAI official
        ]
    
    def is_ai_related(self, text: str) -> bool:
        """Check if a post is AI-related"""
        if not text:
            return False
            
        content = text.lower()
        ai_keywords = [
            'artificial intelligence', 'machine learning', 'deep learning', 'ai',
            'neural network', 'llm', 'large language model', 'gpt', 'claude', 
            'openai', 'anthropic', 'google ai', 'meta ai', 'microsoft ai',
            'transformer', 'bert', 'attention mechanism', 'chatbot', 'ai model',
            'generative ai', 'foundation model', 'prompt engineering', 'fine-tuning',
            'computer vision', 'natural language processing', 'nlp', 'reinforcement learning'
        ]
        return any(keyword in content for keyword in ai_keywords)
    
    def calculate_relevance_score(self, post: dict) -> float:
        """Calculate AI relevance score for a LinkedIn post"""
        text = post.get('text', '').lower()
        
        # High-value AI keywords (higher weight)
        high_value_keywords = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'large language model', 'neural network', 'transformer',
            'generative ai', 'foundation model', 'ai breakthrough',
            'ai revolution', 'future of ai', 'ai innovation'
        ]
        
        # Medium-value AI keywords  
        medium_value_keywords = [
            'ai', 'chatbot', 'automation', 'intelligent', 'algorithm',
            'data science', 'computer vision', 'nlp', 'ai tool'
        ]
        
        score = 0.0
        
        # Count high-value keywords (0.3 each)
        for keyword in high_value_keywords:
            if keyword in text:
                score += 0.3
        
        # Count medium-value keywords (0.1 each)  
        for keyword in medium_value_keywords:
            if keyword in text:
                score += 0.1
        
        # Bonus for engagement metrics
        likes = post.get('likes', 0)
        comments = post.get('comments', 0)
        
        if likes > 100:
            score += 0.1
        if comments > 10:
            score += 0.1
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def get_profile_posts(self, username: str, limit: int = 5) -> List[Article]:
        """Get posts from a specific LinkedIn profile"""
        if not self.api_key or self.api_key == 'demo-key':
            print("⚠️  RAPIDAPI_KEY not found in environment variables")
            print("   Add RAPIDAPI_KEY=your_key to .env file")
            return []
        
        articles = []
        page = 1
        
        try:
            while len(articles) < limit and page <= 3:  # Max 3 pages
                url = f"{self.base_url}/profile/posts"
                params = {
                    'username': username,
                    'page_number': page
                }
                
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                
                if response.status_code != 200:
                    print(f"⚠️  LinkedIn API error for {username}: {response.status_code}")
                    break
                
                data = response.json()
                posts = data.get('posts', [])
                
                if not posts:
                    break
                
                for post in posts:
                    if len(articles) >= limit:
                        break
                    
                    post_text = post.get('text', '')
                    
                    if self.is_ai_related(post_text):
                        relevance = self.calculate_relevance_score(post)
                        
                        # Only include posts with decent relevance
                        if relevance >= 0.3:
                            article = Article(
                                title=post_text[:100] + "..." if len(post_text) > 100 else post_text,
                                url=post.get('post_url', f"https://linkedin.com/in/{username}"),
                                source=f"LinkedIn (@{username})",
                                author=post.get('author_name', username),
                                published_date=post.get('published_date', datetime.now().isoformat()),
                                excerpt=post_text[:300] + "..." if len(post_text) > 300 else post_text,
                                relevance_score=relevance
                            )
                            articles.append(article)
                
                page += 1
                time.sleep(1)  # Rate limiting
        
        except Exception as e:
            print(f"❌ Error fetching LinkedIn posts for {username}: {e}")
        
        return articles
    
    def get_articles(self, limit: int = 10) -> List[Article]:
        """Get AI-related articles from monitored LinkedIn profiles"""
        all_articles = []
        posts_per_profile = max(2, limit // len(self.ai_profiles))
        
        print(f"🔗 Scanning {len(self.ai_profiles)} LinkedIn AI profiles...")
        
        for username in self.ai_profiles:
            if len(all_articles) >= limit:
                break
                
            print(f"   📱 Checking @{username}...")
            profile_articles = self.get_profile_posts(username, posts_per_profile)
            all_articles.extend(profile_articles)
            
            time.sleep(0.5)  # Be nice to the API
        
        # Sort by relevance score and return top results
        all_articles.sort(key=lambda x: x.relevance_score, reverse=True)
        return all_articles[:limit]

class TrilogyAIMonitor:
    """Monitor Trilogy AI Center of Excellence Substack for team competition"""
    
    def __init__(self):
        self.substack_rss = "https://trilogyai.substack.com/feed"
        self.base_url = "https://trilogyai.substack.com"
        
        # Initialize Firecrawl for comprehensive site crawling
        try:
            from firecrawl import FirecrawlApp
            self.firecrawl = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))
            self.use_firecrawl = True
            print("🔥 Firecrawl initialized - will crawl entire website")
        except (ImportError, Exception) as e:
            print(f"⚠️  Firecrawl not available ({e}), falling back to RSS")
            self.firecrawl = None
            self.use_firecrawl = False
        
        # Trilogy AI team members for enhanced author detection
        self.team_members = [
            "Leonardo Gonzalez",
            "Stanislav Huseletov", 
            "Praveen Koka",
            "David Proctor"
        ]
    
    def is_trilogy_article(self, title: str, content: str, author: str = None) -> bool:
        """Check if article is from Trilogy AI team"""
        # All articles from trilogyai.substack.com are Trilogy articles
        return True
    
    def calculate_relevance_score(self, title: str, content: str, author: str = None) -> float:
        """Calculate relevance for Trilogy AI articles (always high)"""
        score = 0.9  # Base score for Trilogy articles
        
        # Boost for AI-related content
        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'gpt', 'claude', 
                      'llm', 'model', 'algorithm', 'automation', 'neural', 'deep learning']
        
        text = (title + " " + content).lower()
        for keyword in ai_keywords:
            if keyword in text:
                score += 0.02
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def extract_author_from_content(self, title: str, content: str) -> Optional[str]:
        """Extract author from title or content"""
        # Check if any team member name is in the title or content
        for member in self.team_members:
            if member.lower() in title.lower() or member.lower() in content.lower():
                return member
    
    def crawl_entire_website(self) -> List[Article]:
        """Use Firecrawl to crawl the entire Trilogy AI website and get ALL articles"""
        if not self.use_firecrawl:
            print("🔄 Firecrawl not available, falling back to RSS")
            return self.get_articles_from_rss()
        
        print("🔥 Using Firecrawl to crawl entire Trilogy AI website...")
        articles = []
        
        try:
            # First check the current Firecrawl API by testing with a simple crawl
            print(f"🔥 Starting Firecrawl crawl of {self.base_url}...")
            
            # Use the map function first to see what pages are available
            try:
                map_response = self.firecrawl.map_url(self.base_url)
                
                # Handle different response types
                if hasattr(map_response, 'links'):
                    links = map_response.links
                elif isinstance(map_response, dict):
                    links = map_response.get('links', [])
                else:
                    links = getattr(map_response, 'data', {}).get('links', []) if hasattr(map_response, 'data') else []
                
                print(f"🗺️  Found {len(links)} total links")
                
                # Filter for article links (contain '/p/')
                article_links = [link for link in links 
                               if '/p/' in link and not any(exclude in link for exclude in ['tag/', 'archive/', 'about', 'subscribe'])]
                
                print(f"📄 Found {len(article_links)} article links")
                
                # Scrape each article individually for better control
                for i, link in enumerate(article_links[:50]):  # Limit to first 50 to avoid hitting API limits
                    try:
                        print(f"🔥 Scraping article {i+1}/{min(len(article_links), 50)}: {link}")
                        
                        scrape_response = self.firecrawl.scrape_url(
                            link,
                            formats=['markdown'],
                            onlyMainContent=True
                        )
                        
                        # Handle the new Firecrawl response format
                        if hasattr(scrape_response, 'data'):
                            page_data = scrape_response.data
                        elif hasattr(scrape_response, 'get'):
                            page_data = scrape_response.get('data', {})
                        else:
                            page_data = scrape_response  # Direct response
                        
                        if page_data:
                            # Handle both dict and object response formats
                            if hasattr(page_data, 'metadata'):
                                metadata = page_data.metadata
                                title = getattr(metadata, 'title', 'Untitled') if metadata else 'Untitled'
                                url = getattr(metadata, 'sourceURL', link) if metadata else link
                                content = getattr(page_data, 'markdown', '')
                                published_time = getattr(metadata, 'publishedTime', datetime.now().isoformat()) if metadata else datetime.now().isoformat()
                            else:
                                # Fallback to dict format
                                metadata = page_data.get('metadata', {}) if hasattr(page_data, 'get') else {}
                                title = metadata.get('title', 'Untitled') if metadata else 'Untitled'
                                url = metadata.get('sourceURL', link) if metadata else link
                                content = page_data.get('markdown', '') if hasattr(page_data, 'get') else ''
                                published_time = metadata.get('publishedTime', datetime.now().isoformat()) if metadata else datetime.now().isoformat()
                            
                            # If title is still "Untitled" or empty, try to extract from URL
                            if not title or title.strip() == 'Untitled' or title.strip() == '':
                                url_parts = url.split('/')
                                if '/p/' in url and len(url_parts) > 0:
                                    # Extract slug from URL (e.g., "enhancing-llm-evaluation-with-g-eval")
                                    slug = url_parts[-1] if url_parts[-1] else url_parts[-2]
                                    # Convert slug to title format
                                    title = slug.replace('-', ' ').title()
                                    if len(title) < 5:  # If slug is too short, try another approach
                                        title = f"Trilogy AI Article - {slug}"
                                else:
                                    title = "Trilogy AI Article"
                            
                            # Try to extract title from content if still generic
                            if title in ['Untitled', 'Trilogy AI Article'] and content:
                                # Look for title in first few lines of content
                                content_lines = content.split('\n')[:5]
                                for line in content_lines:
                                    line = line.strip()
                                    if len(line) > 10 and len(line) < 100 and not line.startswith('![') and not line.startswith('[!['):
                                        # This looks like a title
                                        title = line.replace('#', '').strip()
                                        break
                            
                            # Skip if not a proper article
                            if len(content) < 100:
                                continue
                            
                            # Extract author from content
                            author = self.extract_author_from_content(title, content)
                            if not author:
                                author = "Trilogy AI Team"
                            
                            # Create excerpt
                            excerpt = content[:300] + "..." if len(content) > 300 else content
                            excerpt = excerpt.replace('\n', ' ').strip()
                            
                            # Calculate relevance score
                            relevance = self.calculate_relevance_score(title, content, author)
                            
                            article = Article(
                                title=title,
                                url=url,
                                source="Trilogy AI CoE",
                                author=author,
                                published_date=published_time,
                                excerpt=excerpt,
                                relevance_score=relevance
                            )
                            
                            articles.append(article)
                        
                        time.sleep(0.5)
                        
                    except Exception as e:
                        print(f"⚠️  Error scraping {link}: {e}")
                        continue
                
                print(f"🔥 Firecrawl successfully extracted {len(articles)} articles")
                 
            except Exception as e:
                print(f"❌ Firecrawl map error: {e}")
                print("🔄 Trying basic crawl as fallback...")
                # Don't try crawl here, let it fall through to RSS
            
            # Sort by published date (newest first)
            articles.sort(key=lambda x: x.published_date, reverse=True)
            
            return articles
            
        except Exception as e:
            print(f"❌ Firecrawl error: {e}")
            print("🔄 Falling back to RSS feed...")
            return self.get_articles_from_rss()
        
        # Look for "by [Name]" patterns
        patterns = [
            r'by\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'written\s+by\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'author:\s*([A-Z][a-z]+\s+[A-Z][a-z]+)'
        ]
        
        text = title + " " + content
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                author_name = match.group(1)
                # Check if it's one of our team members
                for member in self.team_members:
                    if member.lower() == author_name.lower():
                        return member
                return author_name
        
        return None
    
    def get_articles(self, limit: int = None) -> List[Article]:
        """Get ALL articles from Trilogy AI Substack - uses Firecrawl for comprehensive crawling"""
        print(f"📡 Fetching ALL articles from Trilogy AI Center of Excellence...")
        
        # Try Firecrawl first for comprehensive crawling
        if self.use_firecrawl:
            articles = self.crawl_entire_website()
            if articles:
                if limit and len(articles) > limit:
                    articles = articles[:limit]
                return articles
        
        # Fallback to RSS if Firecrawl fails or isn't available
        return self.get_articles_from_rss(limit)
    
    def get_articles_from_rss(self, limit: int = None) -> List[Article]:
        """Fallback method using RSS feeds (limited to recent articles)"""
        articles = []
        
        print(f"📡 Using RSS feed (fallback method)...")
        print(f"🔗 Source: {self.substack_rss}")
        
        try:
            # Parse the RSS feed
            feed = feedparser.parse(self.substack_rss)
            
            if feed.bozo and feed.bozo_exception:
                print(f"⚠️  RSS Parse warning: {feed.bozo_exception}")
            
            if not feed.entries:
                print("❌ No articles found in Trilogy AI feed")
                return []
            
            print(f"📚 Found {len(feed.entries)} total articles in RSS feed")
            
            # Process all entries (or limit if specified)
            entries_to_process = feed.entries[:limit] if limit else feed.entries
            
            for entry in entries_to_process:
                try:
                    # Extract content
                    content = ""
                    if hasattr(entry, 'summary'):
                        content = entry.summary
                    elif hasattr(entry, 'description'):
                        content = entry.description
                    elif hasattr(entry, 'content'):
                        content = entry.content[0].value if entry.content else ""
                    
                    # Try to extract author
                    author = getattr(entry, 'author', None)
                    if not author:
                        author = self.extract_author_from_content(entry.title, content)
                    
                    # Calculate relevance
                    relevance = self.calculate_relevance_score(entry.title, content, author)
                    
                    # Create article
                    article = Article(
                        title=entry.title,
                        url=entry.link,
                        source="Trilogy AI CoE",
                        author=author,
                        published_date=getattr(entry, 'published', datetime.now().isoformat()),
                        excerpt=content[:400] + "..." if len(content) > 400 else content,
                        relevance_score=relevance
                    )
                    
                    articles.append(article)
                    
                except Exception as e:
                    print(f"⚠️  Error processing Trilogy article: {e}")
                    continue
            
            print(f"✅ Successfully processed {len(articles)} Trilogy AI articles")
            print(f"👥 Team members detected: {len([a for a in articles if a.author in self.team_members])}")
            
            # Sort by publication date (newest first)
            articles.sort(key=lambda x: x.published_date, reverse=True)
            
            return articles
            
        except Exception as e:
            print(f"❌ Error fetching Trilogy AI articles: {e}")
            return []

class SemanticScholarMonitor:
    """Monitor Semantic Scholar for latest AI research papers"""
    
    def __init__(self):
        self.base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        self.headers = {
            'User-Agent': 'EII-Discovery-Bot/1.0'
        }
    
    def get_articles(self, limit: int = 10) -> List[Article]:
        """Get latest AI research papers from Semantic Scholar"""
        articles = []
        
        try:
            # Search for recent AI papers
            queries = [
                "artificial intelligence",
                "machine learning", 
                "deep learning",
                "neural networks",
                "large language models",
                "generative ai"
            ]
            
            for query in queries[:2]:  # Limit to 2 queries to avoid rate limits
                params = {
                    'query': query,
                    'limit': limit // 2,  # Split limit across queries
                    'fields': 'title,abstract,authors,year,url,venue,publicationDate',
                    'year': '2024-',  # Only recent papers
                    'sort': 'publicationDate:desc'
                }
                
                response = requests.get(self.base_url, params=params, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for paper in data.get('data', []):
                        try:
                            # Extract paper information
                            title = paper.get('title', 'Untitled')
                            abstract = paper.get('abstract', '')
                            authors = paper.get('authors', [])
                            author_names = [a.get('name', 'Unknown') for a in authors[:3]]  # First 3 authors
                            author_str = ', '.join(author_names)
                            
                            url = paper.get('url') or f"https://www.semanticscholar.org/paper/{paper.get('paperId', '')}"
                            venue = paper.get('venue', 'Semantic Scholar')
                            pub_date = paper.get('publicationDate', '')
                            
                            # Create excerpt from abstract
                            excerpt = abstract[:300] + "..." if len(abstract) > 300 else abstract
                            
                            # Calculate relevance based on AI keywords
                            relevance = self.calculate_relevance_score(title, abstract)
                            
                            article = Article(
                                title=title,
                                url=url,
                                source=f"Semantic Scholar ({venue})",
                                author=author_str or "Unknown",
                                published_date=pub_date or "2024",
                                excerpt=excerpt,
                                relevance_score=relevance
                            )
                            
                            articles.append(article)
                            
                        except Exception as e:
                            print(f"⚠️  Error processing Semantic Scholar paper: {e}")
                            continue
                
                # Be nice to the API
                time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error fetching Semantic Scholar articles: {e}")
        
        return articles
    
    def calculate_relevance_score(self, title: str, abstract: str) -> float:
        """Calculate relevance based on AI research keywords"""
        text = (title + " " + abstract).lower()
        
        # High-value AI research keywords
        ai_keywords = {
            'artificial intelligence': 0.3,
            'machine learning': 0.25,
            'deep learning': 0.25,
            'neural network': 0.2,
            'transformer': 0.2,
            'large language model': 0.3,
            'llm': 0.25,
            'generative': 0.2,
            'multimodal': 0.2,
            'reinforcement learning': 0.2,
            'computer vision': 0.15,
            'natural language processing': 0.2,
            'nlp': 0.2
        }
        
        score = 0.7  # Base score for academic papers
        for keyword, weight in ai_keywords.items():
            if keyword in text:
                score += weight
        
        return min(score, 1.0)

class ContentDiscoverySystem:
    """Main content discovery orchestrator"""
    
    def __init__(self):
        self.rss_monitor = RSSFeedMonitor()
        self.reddit_monitor = RedditMonitor()
        self.hackernews_monitor = HackerNewsMonitor()
        self.linkedin_monitor = LinkedInMonitor()
        self.trilogy_monitor = TrilogyAIMonitor()  # NEW
        self.semantic_scholar_monitor = SemanticScholarMonitor() # NEW
    
    def discover_articles(self, sources: List[str], limit_per_source: int = 10) -> List[Article]:
        """Discover articles from specified sources"""
        all_articles = []
        
        print(f"🔍 EII Content Discovery System")
        print(f"📡 Sources: {', '.join(sources)}")
        print(f"📊 Limit per source: {limit_per_source}")
        print("=" * 50)
        
        # RSS Feeds
        if 'rss' in sources or 'all' in sources:
            print("🔍 Discovering from RSS feeds...")
            rss_articles = self.rss_monitor.get_articles(limit_per_source)
            all_articles.extend(rss_articles)
            print(f"   Found {len(rss_articles)} RSS articles")
        
        # Reddit
        if 'reddit' in sources or 'all' in sources:
            print("🔍 Discovering from Reddit...")
            reddit_articles = self.reddit_monitor.get_articles(limit_per_source)
            all_articles.extend(reddit_articles)
            print(f"   Found {len(reddit_articles)} Reddit articles")
        
        # Hacker News
        if 'hackernews' in sources or 'all' in sources:
            print("🔍 Discovering from Hacker News...")
            hn_articles = self.hackernews_monitor.get_articles(limit_per_source)
            all_articles.extend(hn_articles)
            print(f"   Found {len(hn_articles)} Hacker News articles")
        
        # LinkedIn
        if 'linkedin' in sources or 'all' in sources:
            print("🔍 Discovering from LinkedIn...")
            if not os.getenv('RAPIDAPI_KEY'):
                print("   ⚠️  RAPIDAPI_KEY not found in environment variables")
                print("   💡 Add your RapidAPI key to .env to enable LinkedIn discovery")
                linkedin_articles = []
            else:
                linkedin_articles = self.linkedin_monitor.get_articles(limit_per_source)
                all_articles.extend(linkedin_articles)
            print(f"   Found {len(linkedin_articles)} LinkedIn articles")
        
        # Trilogy AI Center of Excellence (NEW!)
        if 'trilogy' in sources:
            print("🔍 Discovering from Trilogy AI Center of Excellence...")
            # For trilogy, ignore the limit and get ALL articles for team competition
            trilogy_limit = None if 'trilogy' in sources else limit_per_source
            trilogy_articles = self.trilogy_monitor.get_articles(trilogy_limit)
            all_articles.extend(trilogy_articles)
            print(f"   Found {len(trilogy_articles)} Trilogy AI articles")
        
        # Semantic Scholar (NEW!)
        if 'semantic_scholar' in sources:
            print("🔍 Discovering from Semantic Scholar...")
            semantic_scholar_articles = self.semantic_scholar_monitor.get_articles(limit_per_source)
            all_articles.extend(semantic_scholar_articles)
            print(f"   Found {len(semantic_scholar_articles)} Semantic Scholar articles")
        
        # Remove duplicates and sort by relevance
        unique_articles = self._deduplicate_articles(all_articles)
        unique_articles.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return unique_articles
    
    def _deduplicate_articles(self, articles: List[Article]) -> List[Article]:
        """Remove duplicate articles based on URL"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)
        
        return unique_articles
    
    def export_articles(self, articles: List[Article], filename: str = "discovered_articles.json"):
        """Export articles to JSON"""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "total_articles": len(articles),
            "discovery_method": "Multi-source Discovery System",
            "articles": [
                {
                    "title": article.title,
                    "url": article.url,
                    "source": article.source,
                    "author": article.author,
                    "published_date": article.published_date,
                    "excerpt": article.excerpt,
                    "relevance_score": article.relevance_score
                }
                for article in articles
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\n💾 Exported {len(articles)} articles to {filename}")
        return filename
    
    def print_discovery_report(self, articles: List[Article]):
        """Print detailed discovery report"""
        print(f"\n🔍 CONTENT DISCOVERY REPORT")
        print("=" * 60)
        print(f"📊 Total Articles Found: {len(articles)}")
        
        # Group by source
        by_source = {}
        for article in articles:
            if article.source not in by_source:
                by_source[article.source] = []
            by_source[article.source].append(article)
        
        print(f"📈 Sources: {len(by_source)}")
        for source, source_articles in sorted(by_source.items(), key=lambda x: len(x[1]), reverse=True):
            avg_relevance = sum(a.relevance_score for a in source_articles) / len(source_articles)
            print(f"   • {source}: {len(source_articles)} articles (avg relevance: {avg_relevance:.2f})")
        
        # High relevance count
        high_relevance = [a for a in articles if a.relevance_score >= 0.7]
        print(f"🎯 High relevance articles: {len(high_relevance)}")
        
        # Top articles
        print(f"\n🎯 TOP ARTICLES BY RELEVANCE:")
        print("-" * 40)
        for i, article in enumerate(articles[:10], 1):
            print(f"{i}. 📄 {article.title}")
            print(f"   🔗 {article.url}")
            print(f"   📊 Relevance: {article.relevance_score:.2f} | Source: {article.source}")
            if article.author:
                print(f"   ✍️  Author: {article.author}")
            print()

def main():
    parser = argparse.ArgumentParser(description="Discover AI articles from multiple sources")
    parser.add_argument("--source", choices=["all", "rss", "reddit", "hackernews", "linkedin", "trilogy", "semantic_scholar"], 
                       default="all", help="Source to discover from")
    parser.add_argument("--limit", type=int, default=10, help="Limit per source (ignored for trilogy)")
    parser.add_argument("--min-relevance", type=float, default=0.3, help="Minimum relevance score")
    parser.add_argument("--export", default="discovered_articles.json", help="Export filename")
    parser.add_argument("--analyze", action="store_true", help="Send discovered articles to EII analysis webhook")
    parser.add_argument("--webhook-url", help="n8n webhook URL for analysis")
    
    args = parser.parse_args()
    
    # Validate webhook URL if analysis is requested
    if args.analyze and not args.webhook_url:
        webhook_url = os.getenv('EII_WEBHOOK_URL')
        if not webhook_url:
            print("❌ Analysis requested but no webhook URL provided!")
            print("Either use --webhook-url or set EII_WEBHOOK_URL in your .env file")
            return
        args.webhook_url = webhook_url
    
    # Run discovery
    discovery = ContentDiscoverySystem()
    sources = [args.source] if args.source != "all" else ["rss", "reddit", "hackernews", "linkedin", "trilogy", "semantic_scholar"]
    articles = discovery.discover_articles(sources, args.limit)
    
    # Filter by relevance
    filtered_articles = [a for a in articles if a.relevance_score >= args.min_relevance]
    
    # Generate report
    discovery.print_discovery_report(filtered_articles)
    
    # Export results
    discovery.export_articles(filtered_articles, args.export)
    
    # Analyze articles if requested
    if args.analyze:
        print(f"\n🧠 Analyzing {len(filtered_articles)} articles...")
        analyzed_count = 0
        for article in filtered_articles:
            try:
                response = requests.post(
                    args.webhook_url,
                    json={'url': article.url},
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                if response.status_code == 200:
                    analyzed_count += 1
                    print(f"   ✅ Analyzed: {article.title[:50]}...")
                else:
                    print(f"   ❌ Failed: {article.title[:50]}...")
                time.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"   ❌ Error analyzing {article.title[:50]}...: {e}")
        
        print(f"\n🎉 Analysis complete! {analyzed_count}/{len(filtered_articles)} articles analyzed")
    
    # Special handling for Trilogy AI team competition
    if args.source == "trilogy":
        print(f"\n🏆 TRILOGY AI TEAM COMPETITION READY!")
        print(f"📊 {len(filtered_articles)} articles discovered from Trilogy AI CoE")
        print(f"👥 Team members found: {len([a for a in filtered_articles if a.author])}")
        print(f"💡 Next step: Run team analysis to generate leaderboard!")
        print(f"Command: python trilogy_team_analysis.py --mode direct --limit {len(filtered_articles)}")

if __name__ == "__main__":
    main() 