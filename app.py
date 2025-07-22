#!/usr/bin/env python3
"""
EII Web Dashboard Launcher
Launches the Expertise Inflation Index web dashboard from the organized src/ directory.
"""

import os
import sys
import subprocess

def main():
    """Launch the EII web dashboard"""
    # Change to the repository root directory
    repo_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(repo_root)
    
    # Run the web dashboard from src/
    dashboard_path = os.path.join('src', 'web_dashboard.py')
    
    if not os.path.exists(dashboard_path):
        print("❌ Error: web_dashboard.py not found in src/ directory")
        sys.exit(1)
    
    # Pass through any command line arguments
    cmd = [sys.executable, dashboard_path] + sys.argv[1:]
    
    print("🚀 Starting EII Web Dashboard...")
    print(f"📂 Working directory: {repo_root}")
    print(f"💻 Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 EII Dashboard stopped")
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 