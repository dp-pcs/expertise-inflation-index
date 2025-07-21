#!/usr/bin/env python3
"""
Trilogy AI Team Discovery & Analysis Command
==========================================

One-click command to discover all Trilogy AI articles and generate 
the complete team EII leaderboard for presentation.

Usage:
    python trilogy_discovery_command.py
    
This will:
1. Discover ALL articles from trilogyai.substack.com
2. Analyze them for EII scores  
3. Generate team leaderboard
4. Save results for web dashboard
5. Open web dashboard automatically

Perfect for team presentations and competitions!
"""

import subprocess
import sys
import time
import webbrowser
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and show progress"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed!")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error in {description}: {e}")
        return False

def main():
    print("🏆 TRILOGY AI TEAM EII CHAMPIONSHIP")
    print("=" * 50)
    print("🎯 Discovering all Trilogy AI articles and generating team leaderboard...")
    print()
    
    # Step 1: Discover all Trilogy AI articles
    success = run_command(
        "python content_discovery.py --source trilogy",
        "Discovering ALL Trilogy AI articles"
    )
    if not success:
        print("❌ Discovery failed. Please check your setup and try again.")
        return
    
    print()
    
    # Step 2: Analyze articles and generate team leaderboard
    success = run_command(
        "python trilogy_team_analysis.py --mode discovered",
        "Analyzing articles and generating team leaderboard"
    )
    if not success:
        print("❌ Analysis failed. Please check the discovered articles.")
        return
    
    print()
    
    # Step 3: Start web dashboard (if not running)
    print("🌐 Starting web dashboard...")
    try:
        # Check if dashboard is already running
        test_result = subprocess.run(
            "curl -s http://localhost:8080 > /dev/null", 
            shell=True, 
            capture_output=True
        )
        
        if test_result.returncode != 0:
            # Dashboard not running, start it
            print("🚀 Starting web dashboard on port 8080...")
            subprocess.Popen(
                "python web_dashboard.py --port 8080", 
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(3)  # Give it time to start
        else:
            print("✅ Web dashboard already running!")
            
    except Exception as e:
        print(f"⚠️  Could not start web dashboard: {e}")
        print("💡 You can manually start it with: python web_dashboard.py --port 8080")
    
    print()
    print("🎉 TRILOGY AI TEAM CHAMPIONSHIP READY!")
    print("=" * 50)
    print("📊 Results available at:")
    print("   🏆 Team Championship: http://localhost:8080/team-championship")
    print("   🔍 Trilogy Articles: http://localhost:8080/discovery-report?source=trilogy")
    print("   📄 Individual Analysis: http://localhost:8080/article-analysis")
    print()
    print("📁 Files generated:")
    
    # Check what files were created
    files_to_check = [
        ("discovered_articles.json", "📚 Discovered articles"),
        ("trilogy_eii_results.json", "🏆 Team leaderboard results")
    ]
    
    for filename, description in files_to_check:
        if Path(filename).exists():
            print(f"   ✅ {description}: {filename}")
        else:
            print(f"   ❌ {description}: {filename} (not found)")
    
    print()
    print("💡 Pro Tips:")
    print("   • Click 'Trilogy AI CoE' filter to see only your team's articles")
    print("   • Use team championship page for presentation screenshots")
    print("   • Individual author pages show detailed EII breakdowns")
    print("   • Perfect for team meetings and competitive analysis!")
    
    # Optionally open browser
    try:
        print()
        response = input("🌐 Open team championship in browser? (y/n): ").lower().strip()
        if response in ['y', 'yes', '']:
            webbrowser.open('http://localhost:8080/team-championship')
            print("🎯 Opened team championship page!")
    except (KeyboardInterrupt, EOFError):
        print()
        print("👋 Championship ready! Open http://localhost:8080/team-championship when ready.")

if __name__ == "__main__":
    main() 