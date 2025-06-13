#!/usr/bin/env python3
"""
Integration test: TrendCollector → UXResearcher workflow
Shows the complete pipeline from trend collection to UX analysis
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.trend_collector import trend_collector
from agents.ux_researcher import ux_researcher
import json
from datetime import datetime

def test_trend_to_ux_pipeline():
    """Test the complete pipeline from trend collection to UX analysis"""
    print("🚀 Testing Complete Trend → UX Analysis Pipeline")
    print("=" * 60)
    
    # Step 1: Collect trending keywords
    print("\n📈 Step 1: Collecting trending keywords...")
    trends = trend_collector.collect_top_trends(limit=5)
    
    if 'error' in trends:
        print(f"❌ Error collecting trends: {trends['error']}")
        print("💡 Using sample trend for demo...")
        
        # Use sample trend for demo
        sample_trends = [
            {"keyword": "AI fitness", "category": "health", "score": 85.3},
            {"keyword": "productivity app", "category": "productivity", "score": 78.2},
            {"keyword": "crypto portfolio", "category": "finance", "score": 72.1}
        ]
        
        for i, trend in enumerate(sample_trends[:2], 1):
            print(f"\n🎯 Analyzing Trend {i}: {trend['keyword']}")
            print(f"   Category: {trend['category']}")
            print(f"   Score: {trend['score']}")
            
            # Step 2: Analyze UX for this trend
            print(f"\n📊 Step 2: Performing UX analysis...")
            ux_analysis = ux_researcher.analyze_ux_for_trend(
                trend['keyword'], 
                trend['category']
            )
            
            if 'error' not in ux_analysis:
                print(f"   ✅ UX analysis completed!")
                
                # Show key insights
                show_ux_insights(trend['keyword'], ux_analysis)
                
                # Save combined results
                combined_result = {
                    'trend_data': trend,
                    'ux_analysis': ux_analysis,
                    'pipeline_completed_at': datetime.now().isoformat()
                }
                
                filename = f"trend_ux_analysis_{trend['keyword'].replace(' ', '_')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(combined_result, f, indent=2, ensure_ascii=False)
                
                print(f"   💾 결과가 {filename}에 저장되었습니다.")
            else:
                print(f"   ❌ UX analysis failed: {ux_analysis['error']}")
        
        return
    
    print(f"✅ Found {len(trends['trends'])} trending keywords!")
    
    # Step 2: Analyze UX for top 2 trends
    for i, trend in enumerate(trends['trends'][:2], 1):
        print(f"\n🎯 Analyzing Trend {i}: {trend['keyword']}")
        print(f"   Category: {trend['category']}")
        print(f"   Score: {trend['score']}")
        print(f"   Sources: {', '.join(trend['data_sources'])}")
        
        # Perform UX analysis
        print(f"\n📊 Step 2: Performing UX analysis...")
        ux_analysis = ux_researcher.analyze_ux_for_trend(
            trend['keyword'], 
            trend['category']
        )
        
        if 'error' not in ux_analysis:
            print(f"   ✅ UX analysis completed!")
            
            # Show key insights
            show_ux_insights(trend['keyword'], ux_analysis)
            
            # Save combined results
            combined_result = {
                'trend_data': trend,
                'ux_analysis': ux_analysis,
                'pipeline_completed_at': datetime.now().isoformat()
            }
            
            filename = f"trend_ux_analysis_{trend['keyword'].replace(' ', '_')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(combined_result, f, indent=2, ensure_ascii=False)
            
            print(f"   💾 결과가 {filename}에 저장되었습니다.")
        else:
            print(f"   ❌ UX analysis failed: {ux_analysis['error']}")

def show_ux_insights(keyword, ux_analysis):
    """Display key UX insights in a compact format"""
    print(f"\n🔍 Key UX Insights for '{keyword}':")
    print("-" * 45)
    
    # Primary persona
    if ux_analysis.get('personas'):
        primary_persona = ux_analysis['personas'][0]
        print(f"🎯 Primary Persona: {primary_persona['name']}")
        print(f"   주요 고충: {', '.join(primary_persona['pain_points'][:2])}")
    
    # Recommended strategy
    if ux_analysis.get('ux_strategy', {}).get('recommended_strategy'):
        rec = ux_analysis['ux_strategy']['recommended_strategy']
        strategies = ux_analysis['ux_strategy']['strategies']
        if rec['strategy_index'] < len(strategies):
            recommended = strategies[rec['strategy_index']]
            print(f"⭐ 추천 전략: {recommended['direction']}")
            print(f"   핵심: {recommended['core_concept']}")
            print(f"   차별화: {recommended['differentiation']}")
    
    # Key pain points
    if ux_analysis.get('key_pain_points'):
        top_pain = ux_analysis['key_pain_points'][0]
        print(f"⚠️  주요 Pain Point: {top_pain['description']}")
        print(f"   심각도: {top_pain['severity']}/10")
    
    # Market gap
    if ux_analysis.get('competitor_analysis', {}).get('market_gaps'):
        top_gap = ux_analysis['competitor_analysis']['market_gaps'][0]
        print(f"🎯 시장 기회: {top_gap}")

def demonstrate_business_insights():
    """Show how the combined data can generate business insights"""
    print(f"\n💼 Business Insights Generation:")
    print("-" * 45)
    
    sample_insights = [
        {
            "trend": "AI fitness",
            "opportunity": "간편한 AI 운동 추천 앱",
            "target": "바쁜 직장인 (20-30대)",
            "key_feature": "5초 온보딩 + 원터치 운동 시작",
            "market_size": "높음 (건강 의식 증가 트렌드)",
            "competition": "중간 (복잡한 기존 앱들이 주류)",
            "success_probability": "85%"
        },
        {
            "trend": "productivity app",
            "opportunity": "게임화된 할일 관리 앱",
            "target": "MZ세대 학생/직장인",
            "key_feature": "포인트 시스템 + 소셜 경쟁",
            "market_size": "중간 (포화된 시장)",
            "competition": "높음 (많은 경쟁 앱들)",
            "success_probability": "65%"
        }
    ]
    
    for insight in sample_insights:
        print(f"\n📱 App Opportunity: {insight['opportunity']}")
        print(f"   🎯 Target: {insight['target']}")
        print(f"   ⭐ Key Feature: {insight['key_feature']}")
        print(f"   📊 Market Size: {insight['market_size']}")
        print(f"   🏆 Competition: {insight['competition']}")
        print(f"   📈 Success Probability: {insight['success_probability']}")

def show_next_steps():
    """Show what developers can do with this data"""
    print(f"\n🛠️  Next Steps for Developers:")
    print("-" * 45)
    
    steps = [
        "1. 📋 Use personas to create user stories",
        "2. 🎨 Design wireframes based on UX strategy", 
        "3. 🔧 Build MVP focusing on key features",
        "4. 📊 Set up metrics based on success indicators",
        "5. 🚀 Launch and validate with target users"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print(f"\n📚 Integration with other tools:")
    print(f"   • IdeaGenerator: Generate specific features")
    print(f"   • DesignGenerator: Create wireframes and components")
    print(f"   • Business model analysis: Revenue strategies")

if __name__ == "__main__":
    print("🎯 Complete Trend-to-UX Analysis Pipeline")
    print("=" * 60)
    
    # Check configuration
    print("\n⚙️  Configuration Check:")
    print(f"   TrendCollector enabled: {trend_collector.enabled}")
    print(f"   UXResearcher enabled: {ux_researcher.enabled}")
    
    if trend_collector.enabled or ux_researcher.enabled:
        try:
            test_trend_to_ux_pipeline()
            demonstrate_business_insights()
            show_next_steps()
        except Exception as e:
            print(f"❌ Pipeline test failed: {e}")
            print("💡 Check your API keys and configuration")
    else:
        print("⚠️  Both agents are disabled. Check config/settings.yaml")
        demonstrate_business_insights()
        show_next_steps()
    
    print("\n✅ Pipeline test complete!")
    print(f"\n🎉 You now have a complete system for:")
    print(f"   📈 Collecting real-time trends")
    print(f"   🎯 Analyzing UX opportunities") 
    print(f"   💡 Generating actionable insights")
    print(f"   🚀 Building data-driven apps!")