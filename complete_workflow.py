#!/usr/bin/env python3
"""
Complete AI App Factory Workflow
Demonstrates the full pipeline from trend collection to design system generation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.trend_collector import trend_collector
from agents.ux_researcher import ux_researcher
from agents.design_system_generator import design_system_generator
from agents.idea_generator import idea_generator
import json
from datetime import datetime
import time

class AIAppFactory:
    """Main orchestrator for the complete AI App Factory workflow"""
    
    def __init__(self):
        self.results = {}
        self.agents = {
            'trend_collector': trend_collector,
            'ux_researcher': ux_researcher,
            'idea_generator': idea_generator,
            'design_system_generator': design_system_generator
        }
    
    def generate_complete_app_concept(self, custom_trend: str = None, category: str = None) -> dict:
        """
        Complete workflow: Trends → UX Analysis → Ideas → Design System
        """
        print("🚀 Starting Complete AI App Factory Workflow...")
        print("=" * 60)
        
        workflow_start = time.time()
        
        try:
            # Step 1: Collect Trends (or use custom trend)
            if custom_trend:
                print(f"\n📊 Step 1: Using custom trend '{custom_trend}'")
                selected_trend = {
                    'keyword': custom_trend,
                    'category': category or 'general',
                    'score': 100,
                    'data_sources': ['custom']
                }
            else:
                print(f"\n📊 Step 1: Collecting trending keywords...")
                trends_data = trend_collector.collect_top_trends(limit=5)
                
                if 'error' in trends_data:
                    print(f"⚠️  Trend collection failed: {trends_data['error']}")
                    print("📱 Using sample trend for demo...")
                    selected_trend = {
                        'keyword': 'AI productivity',
                        'category': 'productivity',
                        'score': 85.0,
                        'data_sources': ['sample']
                    }
                else:
                    print(f"✅ Found {len(trends_data['trends'])} trends")
                    selected_trend = trends_data['trends'][0]  # Use top trend
                    print(f"🎯 Selected trend: {selected_trend['keyword']} (score: {selected_trend['score']})")
            
            self.results['step1_trends'] = selected_trend
            
            # Step 2: UX Research & Analysis
            print(f"\n🎯 Step 2: Analyzing UX for '{selected_trend['keyword']}'...")
            ux_analysis = ux_researcher.analyze_ux_for_trend(
                selected_trend['keyword'], 
                selected_trend['category']
            )
            
            if 'error' in ux_analysis:
                print(f"⚠️  UX analysis failed: {ux_analysis['error']}")
                return {'error': 'UX analysis failed', 'partial_results': self.results}
            
            print(f"✅ UX analysis completed")
            print(f"   👥 Generated {len(ux_analysis.get('personas', []))} personas")
            print(f"   🎨 Created {len(ux_analysis.get('ux_strategy', {}).get('strategies', []))} UX strategies")
            
            self.results['step2_ux_analysis'] = ux_analysis
            
            # Step 3: Generate App Ideas
            print(f"\n💡 Step 3: Generating app ideas...")
            market_data = {'trends': [selected_trend]}
            user_data = {
                'personas': ux_analysis.get('personas', []),
                'pain_points': ux_analysis.get('key_pain_points', [])
            }
            
            app_ideas = idea_generator.generate_app_ideas(market_data, user_data)
            
            if 'error' in app_ideas:
                print(f"⚠️  Idea generation failed: {app_ideas['error']}")
                return {'error': 'Idea generation failed', 'partial_results': self.results}
            
            print(f"✅ Generated {len(app_ideas.get('top_ideas', []))} app ideas")
            if app_ideas.get('top_ideas'):
                top_idea = app_ideas['top_ideas'][0]
                print(f"🏆 Top idea: {top_idea.get('title', 'Unknown')}")
                print(f"   📈 Ranking score: {top_idea.get('ranking_score', 'N/A')}")
            
            self.results['step3_app_ideas'] = app_ideas
            
            # Step 4: Generate Design System
            print(f"\n🎨 Step 4: Creating design system...")
            design_system = design_system_generator.generate_complete_design_system(ux_analysis)
            
            if 'error' in design_system:
                print(f"⚠️  Design system generation failed: {design_system['error']}")
                return {'error': 'Design system generation failed', 'partial_results': self.results}
            
            print(f"✅ Design system created")
            brand_identity = design_system.get('brand_identity', {})
            color_palette = brand_identity.get('color_palette', {})
            if color_palette:
                colors = color_palette.get('colors', {})
                primary = colors.get('primary', {})
                if isinstance(primary, dict):
                    print(f"   🎨 Primary color: {primary.get('500', 'N/A')}")
            
            typography = brand_identity.get('typography_system', {})
            if typography:
                fonts = typography.get('font_families', {})
                print(f"   ✍️  Fonts: {fonts.get('display', 'N/A')} / {fonts.get('body', 'N/A')}")
            
            self.results['step4_design_system'] = design_system
            
            # Step 5: Compile Final Results
            print(f"\n📋 Step 5: Compiling final app concept...")
            
            final_concept = self._compile_final_concept()
            
            workflow_duration = time.time() - workflow_start
            final_concept['workflow_metadata'] = {
                'duration_seconds': round(workflow_duration, 2),
                'completed_at': datetime.now().isoformat(),
                'pipeline_version': '1.0.0'
            }
            
            print(f"✅ Complete app concept generated in {workflow_duration:.1f} seconds!")
            
            return final_concept
            
        except Exception as e:
            print(f"❌ Workflow failed: {e}")
            return {'error': str(e), 'partial_results': self.results}
    
    def _compile_final_concept(self) -> dict:
        """Compile all results into a final app concept"""
        
        trend = self.results.get('step1_trends', {})
        ux_analysis = self.results.get('step2_ux_analysis', {})
        app_ideas = self.results.get('step3_app_ideas', {})
        design_system = self.results.get('step4_design_system', {})
        
        # Extract key information
        selected_idea = app_ideas.get('top_ideas', [{}])[0] if app_ideas.get('top_ideas') else {}
        primary_persona = ux_analysis.get('personas', [{}])[0] if ux_analysis.get('personas') else {}
        primary_strategy = ux_analysis.get('ux_strategy', {}).get('strategies', [{}])[0] if ux_analysis.get('ux_strategy', {}).get('strategies') else {}
        
        return {
            'app_concept': {
                'name': selected_idea.get('title', f"{trend.get('keyword', 'AI')} App"),
                'description': f"A {trend.get('category', 'productivity')} app focused on {trend.get('keyword', 'innovation')}",
                'category': trend.get('category', 'general'),
                'target_market': selected_idea.get('target_market', 'general users'),
                'unique_value_proposition': primary_strategy.get('differentiation', 'User-friendly and efficient solution'),
                'ranking_score': selected_idea.get('ranking_score', 0)
            },
            'market_opportunity': {
                'trending_keyword': trend.get('keyword', 'Unknown'),
                'trend_score': trend.get('score', 0),
                'trend_sources': trend.get('data_sources', []),
                'market_size': 'Medium to High' if trend.get('score', 0) > 70 else 'Medium',
                'competition_level': 'Moderate'
            },
            'target_users': {
                'primary_persona': {
                    'name': primary_persona.get('name', 'Target User'),
                    'age': primary_persona.get('age', 25),
                    'occupation': primary_persona.get('occupation', 'Professional'),
                    'pain_points': primary_persona.get('pain_points', [])[:3],
                    'motivations': primary_persona.get('motivations', [])[:3],
                    'tech_level': primary_persona.get('tech_savviness', 'Medium')
                },
                'total_personas': len(ux_analysis.get('personas', [])),
                'user_research_insights': ux_analysis.get('user_needs', {}).get('key_insights', [])[:3]
            },
            'product_strategy': {
                'ux_approach': primary_strategy.get('direction', 'User-centered design'),
                'core_features': primary_strategy.get('key_features', [])[:5],
                'user_flow': primary_strategy.get('user_flow', []),
                'success_metrics': primary_strategy.get('success_metrics', []),
                'implementation_priority': primary_strategy.get('implementation_priority', 'High')
            },
            'design_identity': {
                'color_palette': self._extract_key_colors(design_system),
                'typography': self._extract_typography_info(design_system),
                'design_principles': design_system.get('component_system', {}).get('design_principles', [])[:3],
                'brand_personality': design_system.get('brand_identity', {}).get('brand_personality', {})
            },
            'technical_specs': {
                'recommended_platform': self._recommend_platform(ux_analysis, app_ideas),
                'development_complexity': selected_idea.get('difficulty', 'Medium'),
                'estimated_timeline': selected_idea.get('estimated_development_time', '3-6 months'),
                'tech_stack_suggestions': self._suggest_tech_stack(trend.get('category', 'general'))
            },
            'business_model': {
                'monetization': self._suggest_monetization(trend.get('category', 'general')),
                'go_to_market': self._suggest_go_to_market_strategy(primary_persona),
                'success_probability': self._calculate_success_probability()
            },
            'next_steps': {
                'immediate_actions': [
                    'Validate concept with target users',
                    'Create detailed wireframes using design system',
                    'Build minimum viable product (MVP)',
                    'Set up analytics and user feedback systems'
                ],
                'development_phases': [
                    'Phase 1: Core MVP development (2-3 months)',
                    'Phase 2: User testing and iteration (1 month)', 
                    'Phase 3: Enhanced features and scaling (2-3 months)'
                ]
            },
            'resources': {
                'figma_templates': design_system.get('figma_resources', {}).get('recommended_templates', [])[:2],
                'design_system_files': [
                    'design_tokens.css',
                    'tailwind_config.json',
                    'component_specifications.json'
                ],
                'competitor_references': ux_analysis.get('competitor_analysis', {}).get('top_competitors', [])[:2]
            },
            'raw_data': {
                'trend_data': trend,
                'ux_analysis_summary': {
                    'personas_count': len(ux_analysis.get('personas', [])),
                    'strategies_count': len(ux_analysis.get('ux_strategy', {}).get('strategies', [])),
                    'pain_points_count': len(ux_analysis.get('key_pain_points', []))
                },
                'app_ideas_count': len(app_ideas.get('top_ideas', [])),
                'design_system_components': len(design_system.get('component_system', {}).get('components', {}))
            }
        }
    
    def _extract_key_colors(self, design_system: dict) -> dict:
        """Extract key colors from design system"""
        brand_identity = design_system.get('brand_identity', {})
        color_palette = brand_identity.get('color_palette', {})
        colors = color_palette.get('colors', {})
        
        return {
            'primary': colors.get('primary', {}).get('500', '#3B82F6') if isinstance(colors.get('primary'), dict) else colors.get('primary', '#3B82F6'),
            'secondary': colors.get('secondary', {}).get('analogous_warm', '#8B5CF6') if isinstance(colors.get('secondary'), dict) else '#8B5CF6',
            'success': colors.get('semantic', {}).get('success', '#10B981'),
            'warning': colors.get('semantic', {}).get('warning', '#F59E0B'),
            'error': colors.get('semantic', {}).get('error', '#EF4444')
        }
    
    def _extract_typography_info(self, design_system: dict) -> dict:
        """Extract typography information"""
        brand_identity = design_system.get('brand_identity', {})
        typography = brand_identity.get('typography_system', {})
        font_families = typography.get('font_families', {})
        
        return {
            'display_font': font_families.get('display', 'Inter'),
            'body_font': font_families.get('body', 'Inter'),
            'mono_font': font_families.get('mono', 'JetBrains Mono'),
            'google_fonts_import': typography.get('google_fonts_imports', {}).get('css_import', '')
        }
    
    def _recommend_platform(self, ux_analysis: dict, app_ideas: dict) -> str:
        """Recommend development platform based on analysis"""
        personas = ux_analysis.get('personas', [])
        if personas:
            primary_persona = personas[0]
            tech_level = primary_persona.get('tech_savviness', 'medium').lower()
            age = primary_persona.get('age', 25)
            
            if age < 30 and tech_level in ['high', 'advanced']:
                return 'Mobile-first (React Native or Flutter)'
            elif tech_level == 'low':
                return 'Web-based (Progressive Web App)'
            else:
                return 'Cross-platform (Web + Mobile)'
        
        return 'Cross-platform (Web + Mobile)'
    
    def _suggest_tech_stack(self, category: str) -> dict:
        """Suggest technology stack based on category"""
        stacks = {
            'productivity': {
                'frontend': 'React/Vue.js',
                'backend': 'Node.js/FastAPI',
                'database': 'PostgreSQL',
                'hosting': 'Vercel/Netlify'
            },
            'health': {
                'frontend': 'React Native/Flutter',
                'backend': 'Python/Django',
                'database': 'PostgreSQL',
                'hosting': 'AWS/Google Cloud'
            },
            'finance': {
                'frontend': 'React/Next.js',
                'backend': 'Node.js/Python',
                'database': 'PostgreSQL/MongoDB',
                'hosting': 'AWS/Azure'
            },
            'general': {
                'frontend': 'React/Vue.js',
                'backend': 'Node.js/Python',
                'database': 'PostgreSQL',
                'hosting': 'Vercel/Railway'
            }
        }
        
        return stacks.get(category, stacks['general'])
    
    def _suggest_monetization(self, category: str) -> dict:
        """Suggest monetization strategy"""
        strategies = {
            'productivity': {
                'primary': 'Freemium subscription',
                'secondary': 'Team/enterprise plans',
                'pricing': '$5-15/month'
            },
            'health': {
                'primary': 'Premium features subscription',
                'secondary': 'Personal coaching add-ons',
                'pricing': '$3-10/month'
            },
            'finance': {
                'primary': 'Tiered subscription',
                'secondary': 'Transaction fees',
                'pricing': '$10-30/month'
            },
            'general': {
                'primary': 'Freemium model',
                'secondary': 'Premium features',
                'pricing': '$5-15/month'
            }
        }
        
        return strategies.get(category, strategies['general'])
    
    def _suggest_go_to_market_strategy(self, persona: dict) -> list:
        """Suggest go-to-market strategy based on persona"""
        age = persona.get('age', 25)
        tech_level = persona.get('tech_savviness', 'medium').lower()
        
        strategies = ['Content marketing and SEO', 'Social media presence']
        
        if age < 30:
            strategies.extend(['TikTok/Instagram marketing', 'Influencer partnerships'])
        else:
            strategies.extend(['LinkedIn marketing', 'Industry publications'])
        
        if tech_level in ['high', 'advanced']:
            strategies.append('Product Hunt launch')
        
        strategies.append('Referral program')
        
        return strategies[:5]
    
    def _calculate_success_probability(self) -> str:
        """Calculate success probability based on collected data"""
        trend = self.results.get('step1_trends', {})
        ux_analysis = self.results.get('step2_ux_analysis', {})
        
        score = 50  # Base score
        
        # Trend strength
        trend_score = trend.get('score', 0)
        if trend_score > 80:
            score += 20
        elif trend_score > 60:
            score += 10
        
        # UX analysis quality
        personas_count = len(ux_analysis.get('personas', []))
        if personas_count >= 3:
            score += 15
        
        strategies_count = len(ux_analysis.get('ux_strategy', {}).get('strategies', []))
        if strategies_count >= 3:
            score += 10
        
        # Market factors
        pain_points_count = len(ux_analysis.get('key_pain_points', []))
        if pain_points_count >= 3:
            score += 5
        
        if score >= 80:
            return 'High (80%+)'
        elif score >= 65:
            return 'Medium-High (65-80%)'
        elif score >= 50:
            return 'Medium (50-65%)'
        else:
            return 'Low-Medium (<50%)'
    
    def save_complete_concept(self, concept: dict, filename: str = None) -> str:
        """Save the complete app concept to file"""
        if filename is None:
            app_name = concept.get('app_concept', {}).get('name', 'ai_app')
            safe_name = app_name.lower().replace(' ', '_').replace('-', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"complete_app_concept_{safe_name}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(concept, f, indent=2, ensure_ascii=False)
        
        return filename

def main_workflow_demo():
    """Demonstrate the complete workflow"""
    print("🏭 AI App Factory - Complete Workflow Demo")
    print("=" * 60)
    
    app_factory = AIAppFactory()
    
    # Option 1: Use trending keywords
    print("\n🎯 Option 1: Generate concept from trending keywords")
    concept1 = app_factory.generate_complete_app_concept()
    
    if 'error' not in concept1:
        print(f"\n🎉 Success! Generated concept for: {concept1['app_concept']['name']}")
        filename1 = app_factory.save_complete_concept(concept1)
        print(f"💾 Saved to: {filename1}")
        
        # Show key highlights
        show_concept_highlights(concept1)
    else:
        print(f"❌ Workflow failed: {concept1['error']}")
    
    print(f"\n" + "="*60)
    
    # Option 2: Use custom trend
    print("\n🎯 Option 2: Generate concept from custom trend")
    concept2 = app_factory.generate_complete_app_concept(
        custom_trend="AI language learning",
        category="education"
    )
    
    if 'error' not in concept2:
        print(f"\n🎉 Success! Generated concept for: {concept2['app_concept']['name']}")
        filename2 = app_factory.save_complete_concept(concept2)
        print(f"💾 Saved to: {filename2}")
        
        # Show comparison with first concept
        show_concept_comparison(concept1 if 'error' not in concept1 else None, concept2)
    else:
        print(f"❌ Workflow failed: {concept2['error']}")

def show_concept_highlights(concept: dict):
    """Show key highlights of the generated concept"""
    print(f"\n✨ Concept Highlights:")
    print("-" * 30)
    
    app_concept = concept.get('app_concept', {})
    print(f"📱 App: {app_concept.get('name', 'Unknown')}")
    print(f"🏷️  Category: {app_concept.get('category', 'Unknown')}")
    print(f"🎯 Target: {app_concept.get('target_market', 'Unknown')}")
    print(f"⭐ USP: {app_concept.get('unique_value_proposition', 'Unknown')}")
    
    target_users = concept.get('target_users', {})
    primary_persona = target_users.get('primary_persona', {})
    print(f"👤 Primary User: {primary_persona.get('name', 'Unknown')}")
    
    design_identity = concept.get('design_identity', {})
    print(f"🎨 Primary Color: {design_identity.get('color_palette', {}).get('primary', 'Unknown')}")
    print(f"✍️  Font: {design_identity.get('typography', {}).get('display_font', 'Unknown')}")
    
    business_model = concept.get('business_model', {})
    print(f"💰 Monetization: {business_model.get('monetization', {}).get('primary', 'Unknown')}")
    print(f"📈 Success Probability: {business_model.get('success_probability', 'Unknown')}")

def show_concept_comparison(concept1: dict, concept2: dict):
    """Compare two generated concepts"""
    print(f"\n🔍 Concept Comparison:")
    print("-" * 30)
    
    if concept1:
        app1 = concept1.get('app_concept', {})
        app2 = concept2.get('app_concept', {})
        
        print(f"Concept 1: {app1.get('name', 'Unknown')} ({app1.get('category', 'Unknown')})")
        print(f"Concept 2: {app2.get('name', 'Unknown')} ({app2.get('category', 'Unknown')})")
        
        # Compare success probabilities
        prob1 = concept1.get('business_model', {}).get('success_probability', 'Unknown')
        prob2 = concept2.get('business_model', {}).get('success_probability', 'Unknown')
        print(f"Success Probability: {prob1} vs {prob2}")
        
        # Compare target users
        user1 = concept1.get('target_users', {}).get('primary_persona', {}).get('name', 'Unknown')
        user2 = concept2.get('target_users', {}).get('primary_persona', {}).get('name', 'Unknown')
        print(f"Primary Users: {user1} vs {user2}")
    else:
        print("Only one concept available for comparison")

if __name__ == "__main__":
    main_workflow_demo()
    
    print(f"\n🎓 Workflow Summary:")
    print("=" * 40)
    print("✅ Complete AI App Factory system is now ready!")
    print("🔄 End-to-end pipeline: Trends → UX → Ideas → Design")
    print("📊 Data-driven insights from real market trends")
    print("🎨 Professional design systems with implementation code")
    print("💼 Business strategies and go-to-market plans")
    print("🚀 Ready-to-build app concepts with technical specs")
    
    print(f"\n📚 Integration Examples:")
    print("```python")
    print("from complete_workflow import AIAppFactory")
    print("")
    print("# Create factory instance")
    print("factory = AIAppFactory()")
    print("")
    print("# Generate from trending keywords")
    print("concept = factory.generate_complete_app_concept()")
    print("")
    print("# Or use custom trend")
    print("concept = factory.generate_complete_app_concept('AI fitness', 'health')")
    print("")
    print("# Save results")
    print("filename = factory.save_complete_concept(concept)")
    print("```")