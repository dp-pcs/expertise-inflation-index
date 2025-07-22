#!/usr/bin/env python3
"""
Trilogy AI Team EII Analysis
============================

Competitive analysis of all 4 authors from trilogyai.substack.com
Creates EII leaderboards, author rankings, and fun competitive stats.

Usage:
    python trilogy_team_analysis.py --mode api    # Use n8n webhook
    python trilogy_team_analysis.py --mode direct # Direct LLM calls
    python trilogy_team_analysis.py --mode discovered # Use discovered articles
"""

import json
import requests
import time
import statistics
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse
from pathlib import Path

class TrilogyAIClient:
    """Mock client for Trilogy AI Substack API"""
    
    def __init__(self):
        self.articles_cache = []
    
    def load_discovered_articles(self, filename: str = "discovered_articles.json") -> List[Dict]:
        """Load articles from content discovery system"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Filter for Trilogy AI articles only
            trilogy_articles = [
                article for article in data.get('articles', [])
                if article.get('source') == 'Trilogy AI CoE'
            ]
            
            print(f"📚 Loaded {len(trilogy_articles)} Trilogy AI articles from {filename}")
            return trilogy_articles
            
        except FileNotFoundError:
            print(f"❌ {filename} not found. Run: python content_discovery.py --source trilogy")
            return []
        except Exception as e:
            print(f"❌ Error loading discovered articles: {e}")
            return []
    
    def list_articles(self, author: str = None, limit: int = 20) -> List[Dict]:
        """Mock method - returns sample articles for testing"""
        # Sample articles for testing when no real data available
        sample_articles = [
            {
                "id": "grok-4-vs-kimi-k2",
                "title": "Grok 4 vs. Kimi K2: Clash of the Titans",
                "author": "Leonardo Gonzalez",
                "url": "https://trilogyai.substack.com/p/grok-4-vs-kimi-k2"
            },
            {
                "id": "deepagent-value-check",
                "title": "DeepAgent Value Check: Revolutionary Multi-Agent Framework",
                "author": "Stanislav Huseletov",
                "url": "https://trilogyai.substack.com/p/deepagent-value-check"
            }
        ]
        
        if author:
            return [a for a in sample_articles if a['author'] == author][:limit]
        return sample_articles[:limit]
    
    def get_article_content(self, article_id: str) -> str:
        """Mock method - returns sample content"""
        sample_content = {
            "grok-4-vs-kimi-k2": """
            The AI landscape is witnessing an unprecedented paradigm shift with the emergence of two revolutionary 
            Large Language Models: Grok 4 and Kimi K2. These groundbreaking systems represent the pinnacle of 
            artificial intelligence engineering, leveraging state-of-the-art transformer architectures and 
            next-generation neural optimization protocols.
            
            Our comprehensive analysis reveals that Grok 4's multi-modal reasoning capabilities exceed industry 
            benchmarks by 340%, while Kimi K2's contextual understanding framework demonstrates superior 
            performance in complex reasoning tasks. The implications for enterprise AI deployment are nothing 
            short of revolutionary.
            """,
            "deepagent-value-check": """
            DeepAgent represents a quantum leap in autonomous AI agent orchestration. This cutting-edge framework 
            combines reinforcement learning with advanced neural architecture search to create self-optimizing 
            agent ecosystems. Our proprietary evaluation methodology demonstrates significant improvements across 
            all key performance indicators.
            
            The multi-agent coordination protocols we've developed enable seamless integration with existing 
            enterprise infrastructure while maintaining unprecedented levels of autonomy and decision-making 
            capability. Early adopters report efficiency gains of up to 400% in automated workflow processing.
            """
        }
        
        return sample_content.get(article_id, "Sample article content for EII analysis.")

class EIIAnalyzer:
    """EII Analysis system supporting multiple modes"""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
    
    def analyze_article_via_webhook(self, article_url: str) -> Optional[Dict]:
        """Analyze article via n8n webhook"""
        if not self.webhook_url:
            print("❌ No webhook URL configured")
            return None
        
        try:
            response = requests.post(
                self.webhook_url,
                json={'url': article_url},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Webhook failed with status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error calling webhook: {e}")
            return None
    
    def analyze_article_direct(self, title: str, content: str, author: str) -> Dict:
        """Direct EII analysis with mock scoring (for demo)"""
        
        # Mock scoring based on content characteristics
        confidence_score = self._calculate_confidence(title, content)
        jargon_score = self._calculate_jargon(title, content)
        self_reference_score = self._calculate_self_reference(title, content, author)
        originality_score = self._calculate_originality(title, content)
        humor_score = self._calculate_humor(title, content)
        
        overall_eii = (confidence_score + jargon_score + self_reference_score + originality_score) / 4
        
        return {
            "scores": {
                "confidence": confidence_score,
                "jargon_density": jargon_score,
                "self_reference": self_reference_score,
                "originality": originality_score,
                "humor_rating": humor_score
            },
            "analysis": {
                "overall_eii_score": round(overall_eii, 2),
                "tone_summary": f"Analysis of {title} by {author}",
                "inflation_type": self._determine_inflation_type(confidence_score, jargon_score),
                "key_phrases": self._extract_key_phrases(title, content)
            }
        }
    
    def _calculate_confidence(self, title: str, content: str) -> int:
        """Calculate confidence inflation score"""
        text = (title + " " + content).lower()
        confidence_words = ['revolutionary', 'groundbreaking', 'unprecedented', 'breakthrough', 
                           'cutting-edge', 'paradigm shift', 'quantum leap', 'game-changing']
        
        score = 3  # Base score
        for word in confidence_words:
            if word in text:
                score += 1
        
        return min(score, 10)
    
    def _calculate_jargon(self, title: str, content: str) -> int:
        """Calculate jargon density score"""
        text = (title + " " + content).lower()
        jargon_words = ['optimization', 'orchestration', 'framework', 'architecture', 
                       'methodology', 'protocols', 'infrastructure', 'ecosystem']
        
        score = 2  # Base score
        for word in jargon_words:
            if word in text:
                score += 0.8
        
        return min(int(score), 10)
    
    def _calculate_self_reference(self, title: str, content: str, author: str) -> int:
        """Calculate self-reference score"""
        text = (title + " " + content).lower()
        self_ref_words = ['our', 'we', 'my', 'i', 'proprietary', 'exclusive']
        
        score = 2  # Base score
        for word in self_ref_words:
            if word in text:
                score += 0.7
        
        return min(int(score), 10)
    
    def _calculate_originality(self, title: str, content: str) -> int:
        """Calculate originality claims score"""
        text = (title + " " + content).lower()
        originality_words = ['first', 'novel', 'innovative', 'pioneering', 'unique', 
                           'exclusive', 'revolutionary', 'breakthrough']
        
        score = 3  # Base score
        for word in originality_words:
            if word in text:
                score += 0.9
        
        return min(int(score), 10)
    
    def _calculate_humor(self, title: str, content: str) -> int:
        """Calculate humor/self-awareness score"""
        text = (title + " " + content).lower()
        humor_indicators = ['admit', 'confess', 'honestly', 'probably', 'might be wrong',
                          'disclaimer', 'caveat', 'grain of salt']
        
        score = 2  # Base score (most are serious)
        for indicator in humor_indicators:
            if indicator in text:
                score += 2
        
        return min(score, 10)
    
    def _determine_inflation_type(self, confidence: int, jargon: int) -> str:
        """Determine the type of expertise inflation"""
        if confidence >= 8 and jargon >= 7:
            return "Technical Guru"
        elif confidence >= 7:
            return "Breakthrough Claimer"
        elif jargon >= 8:
            return "Jargon Bomber"
        elif confidence >= 6:
            return "Thought Leader"
        else:
            return "Balanced"
    
    def _extract_key_phrases(self, title: str, content: str) -> List[str]:
        """Extract key inflated phrases"""
        phrases = []
        text = title + " " + content
        
        if "revolutionary" in text.lower():
            phrases.append("revolutionary")
        if "paradigm shift" in text.lower():
            phrases.append("paradigm shift")
        if "cutting-edge" in text.lower():
            phrases.append("cutting-edge")
        if "unprecedented" in text.lower():
            phrases.append("unprecedented")
        
        return phrases[:5]

class TrilogyTeamDashboard:
    """Team competition dashboard and analytics"""
    
    def __init__(self):
        self.analyses = []
        self.author_stats = defaultdict(list)
    
    def add_analysis(self, author: str, article_title: str, article_url: str, eii_data: Dict):
        """Add an EII analysis result"""
        analysis = {
            'author': author,
            'article_title': article_title,
            'article_url': article_url,
            'eii_data': eii_data,
            'timestamp': datetime.now().isoformat()
        }
        
        self.analyses.append(analysis)
        self.author_stats[author].append(eii_data)
    
    def calculate_author_stats(self) -> Dict[str, Dict]:
        """Calculate comprehensive stats for each author"""
        stats = {}
        
        for author, analyses in self.author_stats.items():
            if not analyses:
                continue
            
            eii_scores = [a['analysis']['overall_eii_score'] for a in analyses]
            confidence_scores = [a['scores']['confidence'] for a in analyses]
            jargon_scores = [a['scores']['jargon_density'] for a in analyses]
            
            # Find most and least inflated articles
            max_eii_idx = eii_scores.index(max(eii_scores))
            min_eii_idx = eii_scores.index(min(eii_scores))
            
            stats[author] = {
                'article_count': len(analyses),
                'avg_eii_score': statistics.mean(eii_scores),
                'max_eii_score': max(eii_scores),
                'min_eii_score': min(eii_scores),
                'avg_confidence': statistics.mean(confidence_scores),
                'avg_jargon': statistics.mean(jargon_scores),
                'most_inflated_article': self.analyses[max_eii_idx]['article_title'],
                'humblest_article': self.analyses[min_eii_idx]['article_title']
            }
        
        return stats
    
    def generate_leaderboard(self) -> Dict[str, List[str]]:
        """Generate competitive rankings"""
        stats = self.calculate_author_stats()
        
        # Sort authors by different criteria
        by_avg_eii = sorted(stats.items(), key=lambda x: x[1]['avg_eii_score'], reverse=True)
        by_confidence = sorted(stats.items(), key=lambda x: x[1]['avg_confidence'], reverse=True)
        by_jargon = sorted(stats.items(), key=lambda x: x[1]['avg_jargon'], reverse=True)
        by_humility = sorted(stats.items(), key=lambda x: x[1]['avg_eii_score'])
        by_humor = sorted(stats.items(), key=lambda x: x[1].get('avg_humor', 3))
        
        return {
            'highest_avg_eii': [author for author, _ in by_avg_eii],
            'most_confident': [author for author, _ in by_confidence],
            'biggest_jargon_bomber': [author for author, _ in by_jargon],
            'most_humble': [author for author, _ in by_humility],
            'funniest': [author for author, _ in by_humor]
        }
    
    def print_dashboard(self):
        """Print the complete competitive dashboard"""
        stats = self.calculate_author_stats()
        rankings = self.generate_leaderboard()
        
        total_articles = sum(len(analyses) for analyses in self.author_stats.values())
        team_avg_eii = statistics.mean([
            stat['avg_eii_score'] for stat in stats.values()
        ]) if stats else 0
        
        print("=" * 60)
        print("🏆 TRILOGY AI EII CHAMPIONSHIP 🏆")
        print("=" * 60)
        
        print(f"📊 Team Summary:")
        print(f"   Total Articles Analyzed: {total_articles}")
        print(f"   Team Average EII Score: {team_avg_eii:.2f}/10")
        
        if stats:
            most_productive = max(stats.items(), key=lambda x: x[1]['article_count'])
            print(f"   Most Productive Author: {most_productive[0]}")
        
        print(f"\n🥇 COMPETITIVE RANKINGS:")
        print("-" * 40)
        
        # Highest EII
        print("🔥 Highest Average EII (Most Inflated):")
        for i, author in enumerate(rankings['highest_avg_eii']):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
            score = stats[author]['avg_eii_score']
            print(f"   {medal} {author}: {score:.2f}/10")
        
        # Most Humble
        print("\n😇 Most Humble (Lowest EII):")
        for i, author in enumerate(rankings['most_humble']):
            medal = ["👼", "🕊️", "🌸"][i] if i < 3 else f"{i+1}."
            score = stats[author]['avg_eii_score']
            print(f"   {medal} {author}: {score:.2f}/10")
        
        # Most Confident
        print("\n💪 Most Confident:")
        for i, author in enumerate(rankings['most_confident']):
            medal = ["💪", "🦁", "⚡"][i] if i < 3 else f"{i+1}."
            score = stats[author]['avg_confidence']
            print(f"   {medal} {author}: {score:.0f}/10")
        
        # Biggest Jargon Bomber
        print("\n💣 Biggest Jargon Bomber:")
        for i, author in enumerate(rankings['biggest_jargon_bomber']):
            medal = ["💣", "🤖", "📚"][i] if i < 3 else f"{i+1}."
            score = stats[author]['avg_jargon']
            print(f"   {medal} {author}: {score:.0f}/10")
        
        # Funniest
        print("\n😂 Funniest Author:")
        for i, author in enumerate(rankings['funniest']):
            medal = ["😂", "🎭", "🤡"][i] if i < 3 else f"{i+1}."
            humor_score = 3  # Default since we don't track this yet
            print(f"   {medal} {author}: {humor_score}/10")
        
        # Individual Details
        print(f"\n📋 INDIVIDUAL AUTHOR DETAILS:")
        print("-" * 40)
        
        for author, stat in stats.items():
            print(f"\n👤 {author}:")
            print(f"   📈 Articles: {stat['article_count']}")
            print(f"   🎯 Avg EII: {stat['avg_eii_score']:.2f}/10")
            print(f"   📊 Range: {stat['min_eii_score']:.1f} - {stat['max_eii_score']:.1f}")
            print(f"   🔥 Most Inflated: \"{stat['most_inflated_article']}\"")
            print(f"   😇 Most Humble: \"{stat['humblest_article']}\"")
        
        # Show authors with no articles
        all_authors = ["David Proctor", "Stanislav Huseletov", "Leonardo Gonzalez", "Praveen Koka"]
        analyzed_authors = set(stats.keys())
        missing_authors = set(all_authors) - analyzed_authors
        
        for author in missing_authors:
            print(f"\n❌ {author}: No articles analyzed")
    
    def save_results(self, filename: str = "trilogy_eii_results.json"):
        """Save detailed results to JSON"""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "total_articles": len(self.analyses),
            "author_stats": self.calculate_author_stats(),
            "rankings": self.generate_leaderboard(),
            "detailed_analyses": self.analyses
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {filename}")

def main():
    parser = argparse.ArgumentParser(description="Analyze Trilogy AI team for EII scores")
    parser.add_argument("--mode", choices=["api", "direct", "discovered"], default="discovered",
                      help="Analysis mode: 'api' uses n8n webhook, 'direct' uses LLM APIs, 'discovered' uses discovered articles")
    parser.add_argument("--webhook-url", 
                      help="n8n webhook URL (required for api mode)")
    parser.add_argument("--limit", type=int, default=20,
                      help="Number of articles to analyze per author")
    
    args = parser.parse_args()
    
    if args.mode == "api" and not args.webhook_url:
        print("❌ Webhook URL required for API mode")
        print("Usage: python trilogy_team_analysis.py --mode api --webhook-url https://your-n8n.app/webhook/eii-analyze")
        return
    
    print("🧠 Starting Trilogy AI Team EII Analysis...")
    print(f"📊 Mode: {args.mode}")
    print(f"📄 Max articles per author: {args.limit}")
    print("=" * 50)
    
    # Initialize components
    client = TrilogyAIClient()
    analyzer = EIIAnalyzer(args.webhook_url)
    dashboard = TrilogyTeamDashboard()
    
    authors = ["David Proctor", "Stanislav Huseletov", "Leonardo Gonzalez", "Praveen Koka"]
    
    if args.mode == "discovered":
        # Use discovered articles mode
        print("📚 Using discovered articles from content discovery...")
        discovered_articles = client.load_discovered_articles()
        
        if not discovered_articles:
            print("❌ No discovered articles found. Run: python content_discovery.py --source trilogy")
            return
        
        # Group articles by author
        articles_by_author = defaultdict(list)
        for article in discovered_articles:
            author = article.get('author')
            if author and author in authors:
                articles_by_author[author].append(article)
        
        # Analyze each author's articles
        total_analyzed = 0
        for author in authors:
            author_articles = articles_by_author[author][:args.limit]
            
            if not author_articles:
                print(f"\n👤 {author}: No articles found")
                continue
            
            print(f"\n👤 Analyzing {author} ({len(author_articles)} articles)...")
            
            for i, article in enumerate(author_articles, 1):
                print(f"   📄 {i}/{len(author_articles)}: {article['title']}")
                
                # Use direct analysis with article content
                eii_result = analyzer.analyze_article_direct(
                    article['title'], 
                    article.get('excerpt', ''), 
                    author
                )
                
                dashboard.add_analysis(
                    author, 
                    article['title'],
                    article['url'], 
                    eii_result
                )
                total_analyzed += 1
        
        print(f"\n✅ Analysis complete! {total_analyzed} articles analyzed.")
    
    else:
        # Original mode (direct or api)
        print("📚 Fetching articles from Trilogy AI Substack...")
        
        for author in authors:
            articles = client.list_articles(author, args.limit)
            
            if not articles:
                print(f"\n👤 {author}: No articles found")
                continue
            
            print(f"\n👤 Analyzing {author} ({len(articles)} articles)...")
            
            for i, article in enumerate(articles, 1):
                print(f"   📄 {i}/{len(articles)}: {article['title']}")
                
                if args.mode == "api":
                    # Use webhook
                    eii_result = analyzer.analyze_article_via_webhook(article['url'])
                    if not eii_result:
                        continue
                else:
                    # Use direct analysis
                    content = client.get_article_content(article['id'])
                    eii_result = analyzer.analyze_article_direct(article['title'], content, author)
                
                dashboard.add_analysis(author, article['title'], article['url'], eii_result)
        
        print(f"\n✅ Analysis complete! {len(dashboard.analyses)} articles analyzed.")
    
    # Generate and display results
    dashboard.print_dashboard()
    dashboard.save_results()

if __name__ == "__main__":
    main() 