#!/usr/bin/env python3
"""
Test script for the EII n8n workflow.
Sends test URLs to the webhook and validates responses.
"""

import requests
import json
import time
from typing import Dict, Any

def test_workflow_endpoint(webhook_url: str, test_url: str) -> Dict[str, Any]:
    """
    Test the EII workflow with a given URL.
    
    Args:
        webhook_url: The n8n webhook URL
        test_url: Article URL to analyze
        
    Returns:
        Response from the workflow
    """
    payload = {"url": test_url}
    
    print(f"🔍 Testing: {test_url}")
    print(f"📡 Webhook: {webhook_url}")
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60  # Workflows can take a while
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            
            if result.get('success'):
                data = result.get('data', {})
                scores = data.get('scores', {})
                analysis = data.get('analysis', {})
                
                print(f"📰 Title: {data.get('title', 'N/A')}")
                print(f"🧠 EII Score: {data.get('eii_score', 'N/A')}/10")
                print(f"📈 Breakdown:")
                print(f"   Confidence: {scores.get('confidence', 'N/A')}/10")
                print(f"   Jargon: {scores.get('jargon_density', 'N/A')}/10") 
                print(f"   Self-Reference: {scores.get('self_reference', 'N/A')}/10")
                print(f"   Originality: {scores.get('originality', 'N/A')}/10")
                print(f"   Humor: {scores.get('humor_rating', 'N/A')}/10")
                print(f"🏷️  Type: {analysis.get('inflation_type', 'N/A')}")
                print(f"🤖 Model: {data.get('model_used', 'N/A')}")
                
                return result
            else:
                print(f"❌ Workflow returned error: {result}")
                return result
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (workflow may still be running)")
        return {"success": False, "error": "Timeout"}
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return {"success": False, "error": str(e)}
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}")
        return {"success": False, "error": "Invalid JSON response"}

def main():
    """Run workflow tests with sample URLs."""
    
    # Replace with your actual n8n webhook URL
    webhook_url = input("Enter your n8n webhook URL: ").strip()
    
    if not webhook_url:
        print("❌ No webhook URL provided")
        return
    
    # Test URLs - mix of different content types
    test_urls = [
        {
            "url": "https://openai.com/research/gpt-4",
            "description": "OpenAI GPT-4 Research (Technical but likely balanced)"
        },
        {
            "url": "https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback",
            "description": "Anthropic Research Paper (Academic tone)"
        },
        {
            "url": "https://news.ycombinator.com/item?id=35408872",
            "description": "HackerNews Discussion (Community-driven)"
        }
    ]
    
    print("🧠 EII n8n Workflow Tester")
    print("=" * 50)
    
    results = []
    
    for i, test_case in enumerate(test_urls, 1):
        print(f"\n🧪 Test {i}/{len(test_urls)}")
        print(f"📄 {test_case['description']}")
        print("-" * 30)
        
        result = test_workflow_endpoint(webhook_url, test_case['url'])
        results.append({
            "test_case": test_case,
            "result": result
        })
        
        # Be nice to APIs - wait between requests
        if i < len(test_urls):
            print("\n⏱️  Waiting 5 seconds before next test...")
            time.sleep(5)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    successful_tests = [r for r in results if r['result'].get('success')]
    failed_tests = [r for r in results if not r['result'].get('success')]
    
    print(f"✅ Successful: {len(successful_tests)}/{len(results)}")
    print(f"❌ Failed: {len(failed_tests)}/{len(results)}")
    
    if successful_tests:
        print("\n🎯 EII Scores:")
        for result in successful_tests:
            data = result['result'].get('data', {})
            print(f"   {data.get('eii_score', 'N/A')}/10 - {data.get('title', 'Unknown')[:50]}...")
    
    if failed_tests:
        print("\n❌ Failed Tests:")
        for result in failed_tests:
            error = result['result'].get('error', 'Unknown error')
            url = result['test_case']['url']
            print(f"   {error} - {url}")
    
    # Save detailed results
    with open('workflow_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to workflow_test_results.json")

if __name__ == "__main__":
    main() 