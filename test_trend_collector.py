#!/usr/bin/env python3
"""
Test script for TrendCollector
Shows how to use the new TrendCollector to get top trends
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.trend_collector import trend_collector
import json

def test_trend_collection():
    """Test the trend collection functionality"""
    print("🚀 Testing TrendCollector...")
    print("=" * 50)
    
    # Test 1: Get top 10 trends
    print("\n📈 Collecting top 10 trends...")
    trends = trend_collector.collect_top_trends(limit=10)
    
    if 'error' in trends:
        print(f"❌ Error: {trends['error']}")
        return
    
    print(f"✅ Successfully collected {len(trends['trends'])} trends")
    print(f"📊 Total keywords analyzed: {trends['total_keywords_analyzed']}")
    print(f"📡 Data sources: {', '.join(trends['data_sources_used'])}")
    print(f"🎯 Target subreddits: {', '.join(trends['target_subreddits'])}")
    
    # Display top 5 trends in detail
    print("\n🏆 Top 5 Trends:")
    print("-" * 40)
    
    for i, trend in enumerate(trends['trends'][:5], 1):
        print(f"\n{i}. {trend['keyword'].title()}")
        print(f"   Score: {trend['score']}")
        print(f"   Category: {trend['category']}")
        print(f"   Sources: {', '.join(trend['data_sources'])}")
        
        if trend['related_images']:
            print(f"   Images: {len(trend['related_images'])} found")
            for img in trend['related_images']:
                print(f"     - {img['description'][:50]}..." if img['description'] else "     - (No description)")
        
        if trend['contexts']:
            print(f"   Context: {trend['contexts'][0]['title'][:60]}...")
    
    # Test 2: Get trends by category
    print(f"\n🏷️  Technology category trends...")
    tech_trends = trend_collector.get_trends_by_category('technology', limit=3)
    
    if 'error' not in tech_trends:
        print(f"✅ Found {tech_trends['total_found']} technology trends")
        for trend in tech_trends['trends']:
            print(f"   • {trend['keyword']} (score: {trend['score']})")
    
    # Test 3: Get simple keywords list
    print(f"\n📝 Simple keywords list...")
    keywords = trend_collector.get_trending_keywords_only(limit=10)
    print(f"✅ Keywords: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}")
    
    # Save results to file
    output_file = 'trend_test_results.json'
    with open(output_file, 'w') as f:
        json.dump(trends, f, indent=2)
    print(f"\n💾 Full results saved to {output_file}")

def show_example_output():
    """Show what the expected output format looks like"""
    print("\n📋 Expected Output Format:")
    print("-" * 30)
    
    example = {
        "trends": [
            {
                "keyword": "AI fitness",
                "score": 85.3,
                "category": "health",
                "data_sources": ["reddit", "google_trends"],
                "related_images": [
                    {
                        "url": "https://images.unsplash.com/photo-example1",
                        "thumb_url": "https://images.unsplash.com/photo-example1?w=200",
                        "description": "Person using AI fitness app",
                        "photographer": "John Doe",
                        "likes": 142
                    }
                ],
                "contexts": [
                    {
                        "title": "New AI-powered fitness app recommendations",
                        "score": 324,
                        "subreddit": "entrepreneur"
                    }
                ],
                "source_breakdown": {
                    "reddit_mentions": 3,
                    "google_trends": True,
                    "base_score": 45.0,
                    "bonus_points": 40.3
                }
            }
        ],
        "total_keywords_analyzed": 87,
        "data_sources_used": ["reddit", "google_trends", "unsplash"],
        "target_subreddits": ["entrepreneur", "SideProject", "startups", "apps"],
        "collected_at": "2024-01-01T12:00:00"
    }
    
    print(json.dumps(example, indent=2))

if __name__ == "__main__":
    print("🎯 TrendCollector Test Suite")
    print("=" * 50)
    
    # Check if we're running with actual API keys
    print("\n⚙️  Configuration Check:")
    print(f"   TrendCollector enabled: {trend_collector.enabled}")
    
    if trend_collector.enabled:
        try:
            test_trend_collection()
        except Exception as e:
            print(f"❌ Test failed: {e}")
            print("💡 Make sure you have set up API keys in .env file")
    else:
        print("⚠️  TrendCollector is disabled. Check config/settings.yaml")
        print("💡 Showing example output format instead...")
        show_example_output()
    
    print("\n✅ Test complete!")
    print("\n📚 Usage in your code:")
    print("```python")
    print("from agents.trend_collector import trend_collector")
    print("")
    print("# Get top 10 trends with images")
    print("trends = trend_collector.collect_top_trends(limit=10)")
    print("")
    print("# Get trends by category")
    print("tech_trends = trend_collector.get_trends_by_category('technology')")
    print("")
    print("# Get simple keywords list")
    print("keywords = trend_collector.get_trending_keywords_only()")
    print("```")