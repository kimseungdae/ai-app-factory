#!/usr/bin/env python3
"""
Test script for UXResearcher
Shows how to use the new UXResearcher to analyze UX for trends
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.ux_researcher import ux_researcher
import json

def test_ux_analysis():
    """Test the UX analysis functionality"""
    print("🎯 Testing UXResearcher...")
    print("=" * 50)
    
    # Test with a sample trend keyword
    trend_keyword = "AI fitness"
    category = "health"
    
    print(f"\n📊 Analyzing UX for trend: '{trend_keyword}'")
    print(f"📂 Category: {category}")
    
    # Perform comprehensive UX analysis
    analysis = ux_researcher.analyze_ux_for_trend(trend_keyword, category)
    
    if 'error' in analysis:
        print(f"❌ Error: {analysis['error']}")
        return
    
    print(f"\n✅ UX Analysis completed!")
    print(f"🎯 Trend: {analysis['trend_keyword']}")
    print(f"📅 Analyzed at: {analysis['analyzed_at']}")
    
    # Display personas
    print(f"\n👥 User Personas ({len(analysis['personas'])} generated):")
    print("-" * 40)
    
    for i, persona in enumerate(analysis['personas'][:3], 1):
        print(f"\n{i}. {persona['name']} ({persona['age']}세)")
        print(f"   직업: {persona['occupation']}")
        print(f"   배경: {persona['background']}")
        print(f"   기술 숙련도: {persona['tech_savviness']}")
        print(f"   주요 고충: {', '.join(persona['pain_points'][:2])}...")
        print(f"   동기: {', '.join(persona['motivations'][:2])}...")
    
    # Display JTBD analysis
    if 'user_needs' in analysis and analysis['user_needs']:
        print(f"\n🎯 Jobs-to-be-Done 분석:")
        print("-" * 40)
        
        user_needs = analysis['user_needs']
        
        if 'functional_jobs' in user_needs:
            print(f"\n기능적 Job:")
            for job in user_needs['functional_jobs'][:2]:
                print(f"   • {job['job']}")
                print(f"     현재 만족도: {job['satisfaction_level']}")
                print(f"     개선 기회: {job['improvement_opportunity']}")
        
        if 'emotional_jobs' in user_needs:
            print(f"\n감정적 Job:")
            for job in user_needs['emotional_jobs'][:1]:
                print(f"   • {job['job']}")
                print(f"     현재 Gap: {job['current_gap']}")
    
    # Display competitor analysis
    if 'competitor_analysis' in analysis and analysis['competitor_analysis']:
        print(f"\n🏆 경쟁사 분석:")
        print("-" * 40)
        
        competitor = analysis['competitor_analysis']
        
        if 'top_competitors' in competitor:
            for comp in competitor['top_competitors'][:2]:
                print(f"\n📱 {comp['app_name']}")
                print(f"   강점: {', '.join(comp['strengths'])}")
                print(f"   약점: {', '.join(comp['weaknesses'])}")
                print(f"   평점: {comp['user_rating']}")
        
        if 'market_gaps' in competitor:
            print(f"\n🎯 시장 Gap:")
            for gap in competitor['market_gaps'][:2]:
                print(f"   • {gap}")
    
    # Display UX strategy
    if 'ux_strategy' in analysis and analysis['ux_strategy']:
        print(f"\n🎨 UX 전략:")
        print("-" * 40)
        
        strategy = analysis['ux_strategy']
        
        if 'strategies' in strategy:
            for i, strat in enumerate(strategy['strategies'][:2], 1):
                print(f"\n전략 {i}: {strat['direction']}")
                print(f"   핵심 컨셉: {strat['core_concept']}")
                print(f"   타겟: {strat['target_persona']}")
                print(f"   차별화: {strat['differentiation']}")
                print(f"   우선순위: {strat['implementation_priority']}")
        
        if 'recommended_strategy' in strategy:
            rec = strategy['recommended_strategy']
            rec_strategy = strategy['strategies'][rec['strategy_index']]
            print(f"\n⭐ 추천 전략: {rec_strategy['direction']}")
            print(f"   이유: {rec['reason']}")
            print(f"   기대 효과: {rec['expected_outcome']}")
    
    # Display pain points
    if 'key_pain_points' in analysis and analysis['key_pain_points']:
        print(f"\n⚠️  주요 Pain Points:")
        print("-" * 40)
        
        for pain in analysis['key_pain_points'][:3]:
            print(f"\n📌 {pain['category']}: {pain['description']}")
            print(f"   빈도: {pain['frequency']}, 심각도: {pain['severity']}/10")
            if pain.get('user_quotes'):
                print(f"   사용자 의견: \"{pain['user_quotes'][0]}\"")
    
    # Save results to file
    output_file = 'ux_analysis_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    print(f"\n💾 전체 분석 결과가 {output_file}에 저장되었습니다.")

def show_example_output():
    """Show what the expected output format looks like"""
    print("\n📋 Expected Output Format:")
    print("-" * 30)
    
    example = {
        "trend_keyword": "AI fitness",
        "category": "health",
        "personas": [
            {
                "name": "바쁜 직장인 김현수",
                "age": 28,
                "occupation": "마케팅 담당자",
                "background": "운동에 관심이 많지만 시간이 부족한 직장인",
                "pain_points": ["시간 부족", "복잡한 운동 계획", "동기 부족"],
                "motivations": ["건강 개선", "효율성", "성취감"],
                "tech_savviness": "중급",
                "daily_challenges": ["업무와 운동 균형", "꾸준한 실행"],
                "preferred_features": ["간단한 운동", "짧은 시간", "자동 추천"]
            }
        ],
        "user_needs": {
            "functional_jobs": [
                {
                    "job": "효율적으로 운동 계획 세우고 실행하기",
                    "current_solution": "유튜브 영상이나 피트니스 앱",
                    "satisfaction_level": "6/10",
                    "improvement_opportunity": "개인화된 AI 추천과 간편한 실행"
                }
            ],
            "emotional_jobs": [
                {
                    "job": "건강해지는 성취감 느끼기",
                    "current_gap": "복잡한 계획으로 인한 스트레스",
                    "desired_outcome": "간단하고 꾸준한 성취감"
                }
            ],
            "key_insights": [
                "사용자들은 간편함을 최우선으로 생각함",
                "AI의 개인화 추천을 신뢰함",
                "짧은 시간 투자로 최대 효과를 원함"
            ]
        },
        "ux_strategy": {
            "strategies": [
                {
                    "direction": "원터치 간편 사용",
                    "core_concept": "5초 내 운동 시작 가능한 초간단 UI",
                    "target_persona": "바쁜 직장인",
                    "key_features": ["5초 온보딩", "원터치 운동 시작", "자동 진행"],
                    "differentiation": "기존 앱 대비 80% 더 간단한 시작 과정",
                    "user_flow": ["앱 열기", "운동 시작", "자동 완료"],
                    "success_metrics": ["첫 운동까지 소요 시간", "재사용률"],
                    "implementation_priority": "높음"
                }
            ],
            "recommended_strategy": {
                "strategy_index": 0,
                "reason": "바쁜 사용자들의 가장 큰 니즈인 간편함에 집중",
                "expected_outcome": "높은 초기 사용률과 지속 사용률"
            }
        }
    }
    
    print(json.dumps(example, indent=2, ensure_ascii=False))

def test_quick_analysis():
    """Test with different categories"""
    print("\n🚀 Quick Tests for Different Categories:")
    print("-" * 50)
    
    test_cases = [
        ("productivity app", "productivity"),
        ("crypto trading", "finance"),
        ("online learning", "education")
    ]
    
    for keyword, category in test_cases:
        print(f"\n📊 Testing: {keyword} ({category})")
        
        if ux_researcher.enabled:
            # Just test persona generation for speed
            personas = ux_researcher._generate_user_personas(keyword, category)
            if personas:
                print(f"   ✅ Generated {len(personas)} personas")
                print(f"   👤 First persona: {personas[0]['name']}")
            else:
                print(f"   ⚠️  Using fallback personas")
        else:
            print(f"   ⚠️  UXResearcher disabled - would use fallback data")

if __name__ == "__main__":
    print("🎯 UXResearcher Test Suite")
    print("=" * 50)
    
    # Check if we're running with actual API keys
    print("\n⚙️  Configuration Check:")
    print(f"   UXResearcher enabled: {ux_researcher.enabled}")
    
    if ux_researcher.enabled:
        try:
            test_ux_analysis()
            test_quick_analysis()
        except Exception as e:
            print(f"❌ Test failed: {e}")
            print("💡 Make sure you have set up API keys in .env file")
    else:
        print("⚠️  UXResearcher is disabled. Check config/settings.yaml")
        print("💡 Showing example output format instead...")
        show_example_output()
    
    print("\n✅ Test complete!")
    print("\n📚 Usage in your code:")
    print("```python")
    print("from agents.ux_researcher import ux_researcher")
    print("")
    print("# Complete UX analysis for a trend")
    print("analysis = ux_researcher.analyze_ux_for_trend('AI fitness', 'health')")
    print("")
    print("# Access specific parts")
    print("personas = analysis['personas']")
    print("strategy = analysis['ux_strategy']")
    print("competitors = analysis['competitor_analysis']")
    print("```")