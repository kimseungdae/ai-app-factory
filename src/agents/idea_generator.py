import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..utils.config import config
from ..utils.api_clients import api_manager

logger = logging.getLogger(__name__)

class IdeaGenerator:
    def __init__(self):
        self.enabled = config.is_agent_enabled('idea_generator')
        self.creativity_level = config.get('agents.idea_generator.creativity_level', 0.8)
        
        if not self.enabled:
            logger.info("Idea Generator agent is disabled")
            return
        
        self.openai_client = api_manager.get_client('openai')
        self.supabase_client = api_manager.get_client('supabase')
    
    def generate_app_ideas(self, market_data: Dict[str, Any], user_research: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "Idea Generator agent is disabled"}
        
        try:
            logger.info("Generating app ideas based on market data and user research...")
            
            market_insights = self._extract_market_insights(market_data)
            user_pain_points = self._extract_user_pain_points(user_research)
            
            app_ideas = []
            
            # Generate different types of ideas
            productivity_ideas = self._generate_productivity_ideas(market_insights, user_pain_points)
            social_ideas = self._generate_social_ideas(market_insights, user_pain_points)
            utility_ideas = self._generate_utility_ideas(market_insights, user_pain_points)
            
            app_ideas.extend(productivity_ideas)
            app_ideas.extend(social_ideas)
            app_ideas.extend(utility_ideas)
            
            # Rank and filter ideas
            ranked_ideas = self._rank_ideas(app_ideas, market_insights)
            
            return {
                'total_ideas_generated': len(app_ideas),
                'top_ideas': ranked_ideas[:10],
                'market_insights_used': market_insights,
                'user_pain_points_addressed': user_pain_points,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating app ideas: {e}")
            return {"error": str(e)}
    
    def generate_feature_ideas(self, app_concept: str, target_users: List[str]) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "Idea Generator agent is disabled"}
        
        try:
            logger.info(f"Generating feature ideas for app concept: {app_concept}")
            
            core_features = self._generate_core_features(app_concept, target_users)
            advanced_features = self._generate_advanced_features(app_concept, target_users)
            monetization_features = self._generate_monetization_features(app_concept)
            
            feature_roadmap = self._create_feature_roadmap(core_features, advanced_features)
            
            return {
                'app_concept': app_concept,
                'target_users': target_users,
                'core_features': core_features,
                'advanced_features': advanced_features,
                'monetization_features': monetization_features,
                'feature_roadmap': feature_roadmap,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating feature ideas: {e}")
            return {"error": str(e)}
    
    def generate_business_model_ideas(self, app_idea: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "Idea Generator agent is disabled"}
        
        try:
            logger.info("Generating business model ideas...")
            
            app_category = app_idea.get('category', 'general')
            target_market = app_idea.get('target_market', 'general')
            
            revenue_models = self._generate_revenue_models(app_category, target_market)
            pricing_strategies = self._generate_pricing_strategies(app_category)
            growth_strategies = self._generate_growth_strategies(target_market)
            
            return {
                'app_idea': app_idea.get('title', 'Unknown'),
                'revenue_models': revenue_models,
                'pricing_strategies': pricing_strategies,
                'growth_strategies': growth_strategies,
                'market_entry_strategy': self._generate_market_entry_strategy(app_category),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating business model ideas: {e}")
            return {"error": str(e)}
    
    def generate_creative_variations(self, base_idea: str, num_variations: int = 5) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "Idea Generator agent is disabled"}
        
        try:
            logger.info(f"Generating {num_variations} creative variations for: {base_idea}")
            
            variations = []
            
            for i in range(num_variations):
                variation_prompt = f"""
                Create a creative variation of this app idea: {base_idea}
                
                Make it unique by:
                - Changing the target audience
                - Adding an innovative twist
                - Combining with another concept
                - Using emerging technology
                
                Provide: Title, Description, Target Audience, Unique Selling Point
                """
                
                variation = self.openai_client.generate_text(
                    variation_prompt,
                    temperature=self.creativity_level
                )
                
                variations.append({
                    'variation_id': i + 1,
                    'content': variation,
                    'creativity_score': self.creativity_level
                })
            
            return {
                'base_idea': base_idea,
                'variations': variations,
                'total_variations': len(variations),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating creative variations: {e}")
            return {"error": str(e)}
    
    def _extract_market_insights(self, market_data: Dict[str, Any]) -> List[str]:
        insights = []
        
        if 'trends' in market_data:
            trends = market_data['trends']
            for trend in trends[:5]:
                if isinstance(trend, dict):
                    title = trend.get('title', trend.get('keyword', 'Unknown'))
                    insights.append(f"Trending: {title}")
        
        if 'emerging_opportunities' in market_data:
            insights.extend(market_data['emerging_opportunities'][:3])
        
        return insights
    
    def _extract_user_pain_points(self, user_research: Dict[str, Any]) -> List[str]:
        pain_points = []
        
        if 'pain_points' in user_research:
            for pain_point in user_research['pain_points'][:5]:
                if isinstance(pain_point, dict):
                    pain_points.append(pain_point.get('description', 'Unknown pain point'))
        
        if 'behavior_patterns' in user_research:
            for pattern in user_research['behavior_patterns'][:3]:
                if isinstance(pattern, dict):
                    pain_points.append(f"User behavior: {pattern.get('description', 'Unknown')}")
        
        return pain_points
    
    def _generate_productivity_ideas(self, market_insights: List[str], pain_points: List[str]) -> List[Dict[str, Any]]:
        ideas = []
        
        productivity_concepts = [
            "AI-powered task manager that learns from your behavior",
            "Voice-controlled workspace organizer for remote workers",
            "Habit tracker with social accountability features",
            "Focus timer with biometric feedback integration",
            "Personal productivity coach using machine learning"
        ]
        
        for i, concept in enumerate(productivity_concepts):
            ideas.append({
                'id': f'prod_{i+1}',
                'title': concept,
                'category': 'productivity',
                'target_market': 'professionals and students',
                'pain_points_addressed': pain_points[:2],
                'market_opportunity': market_insights[:2] if market_insights else ['General productivity market'],
                'difficulty': 'medium',
                'estimated_development_time': '3-6 months'
            })
        
        return ideas
    
    def _generate_social_ideas(self, market_insights: List[str], pain_points: List[str]) -> List[Dict[str, Any]]:
        ideas = []
        
        social_concepts = [
            "Interest-based community platform with AI matching",
            "Local skill-sharing network with gamification",
            "Anonymous peer support app for specific challenges",
            "Professional networking with video introduction cards",
            "Event planning app with collaborative features"
        ]
        
        for i, concept in enumerate(social_concepts):
            ideas.append({
                'id': f'social_{i+1}',
                'title': concept,
                'category': 'social',
                'target_market': 'millennials and gen-z',
                'pain_points_addressed': pain_points[:2],
                'market_opportunity': market_insights[:2] if market_insights else ['Social connectivity needs'],
                'difficulty': 'high',
                'estimated_development_time': '6-12 months'
            })
        
        return ideas
    
    def _generate_utility_ideas(self, market_insights: List[str], pain_points: List[str]) -> List[Dict[str, Any]]:
        ideas = []
        
        utility_concepts = [
            "Smart expense tracker with receipt scanning",
            "Personal finance advisor using open banking APIs",
            "Health symptom tracker with AI insights",
            "Home maintenance scheduler with vendor matching",
            "Travel planner with real-time price optimization"
        ]
        
        for i, concept in enumerate(utility_concepts):
            ideas.append({
                'id': f'utility_{i+1}',
                'title': concept,
                'category': 'utility',
                'target_market': 'general consumers',
                'pain_points_addressed': pain_points[:2],
                'market_opportunity': market_insights[:2] if market_insights else ['Daily life optimization'],
                'difficulty': 'low-medium',
                'estimated_development_time': '2-4 months'
            })
        
        return ideas
    
    def _rank_ideas(self, ideas: List[Dict[str, Any]], market_insights: List[str]) -> List[Dict[str, Any]]:
        for idea in ideas:
            score = 0
            
            # Score based on difficulty (easier = higher score)
            difficulty_scores = {'low': 3, 'low-medium': 2.5, 'medium': 2, 'high': 1}
            score += difficulty_scores.get(idea.get('difficulty', 'medium'), 2)
            
            # Score based on market opportunity
            if idea.get('market_opportunity'):
                score += len(idea['market_opportunity']) * 0.5
            
            # Score based on pain points addressed
            if idea.get('pain_points_addressed'):
                score += len(idea['pain_points_addressed']) * 0.3
            
            # Bonus for trending categories
            trending_keywords = ['ai', 'productivity', 'remote', 'health', 'finance']
            title_lower = idea.get('title', '').lower()
            for keyword in trending_keywords:
                if keyword in title_lower:
                    score += 1
            
            idea['ranking_score'] = round(score, 2)
        
        return sorted(ideas, key=lambda x: x.get('ranking_score', 0), reverse=True)
    
    def _generate_core_features(self, app_concept: str, target_users: List[str]) -> List[Dict[str, Any]]:
        features = [
            {
                'name': 'User Authentication',
                'description': 'Secure login and user management',
                'priority': 'high',
                'complexity': 'low'
            },
            {
                'name': 'Core Functionality',
                'description': f'Main features related to {app_concept}',
                'priority': 'high',
                'complexity': 'high'
            },
            {
                'name': 'User Dashboard',
                'description': 'Personalized user interface and navigation',
                'priority': 'high',
                'complexity': 'medium'
            },
            {
                'name': 'Settings & Preferences',
                'description': 'User customization options',
                'priority': 'medium',
                'complexity': 'low'
            }
        ]
        
        return features
    
    def _generate_advanced_features(self, app_concept: str, target_users: List[str]) -> List[Dict[str, Any]]:
        features = [
            {
                'name': 'AI-Powered Recommendations',
                'description': 'Personalized suggestions based on user behavior',
                'priority': 'medium',
                'complexity': 'high'
            },
            {
                'name': 'Social Integration',
                'description': 'Share and collaborate with other users',
                'priority': 'low',
                'complexity': 'medium'
            },
            {
                'name': 'Advanced Analytics',
                'description': 'Detailed insights and reporting',
                'priority': 'medium',
                'complexity': 'medium'
            },
            {
                'name': 'Mobile App',
                'description': 'Native mobile application',
                'priority': 'high',
                'complexity': 'high'
            }
        ]
        
        return features
    
    def _generate_monetization_features(self, app_concept: str) -> List[Dict[str, Any]]:
        features = [
            {
                'name': 'Premium Subscription',
                'description': 'Advanced features for paying users',
                'revenue_potential': 'high',
                'implementation_effort': 'medium'
            },
            {
                'name': 'In-App Purchases',
                'description': 'One-time purchases for specific features',
                'revenue_potential': 'medium',
                'implementation_effort': 'low'
            },
            {
                'name': 'Freemium Model',
                'description': 'Basic free tier with paid upgrades',
                'revenue_potential': 'high',
                'implementation_effort': 'high'
            }
        ]
        
        return features
    
    def _create_feature_roadmap(self, core_features: List[Dict], advanced_features: List[Dict]) -> Dict[str, List[str]]:
        roadmap = {
            'Phase 1 (MVP)': [f['name'] for f in core_features if f['priority'] == 'high'],
            'Phase 2 (Enhancement)': [f['name'] for f in core_features if f['priority'] == 'medium'] + 
                                   [f['name'] for f in advanced_features if f['priority'] == 'high'],
            'Phase 3 (Growth)': [f['name'] for f in advanced_features if f['priority'] in ['medium', 'low']]
        }
        
        return roadmap
    
    def _generate_revenue_models(self, app_category: str, target_market: str) -> List[Dict[str, Any]]:
        models = [
            {
                'model': 'Freemium',
                'description': 'Free basic version with premium features',
                'pros': ['Low barrier to entry', 'Large user base potential'],
                'cons': ['Low conversion rates', 'High support costs'],
                'suitability': 'High' if app_category in ['productivity', 'utility'] else 'Medium'
            },
            {
                'model': 'Subscription',
                'description': 'Monthly or yearly recurring payments',
                'pros': ['Predictable revenue', 'Customer retention'],
                'cons': ['User acquisition challenges', 'Churn management'],
                'suitability': 'High' if target_market == 'professionals' else 'Medium'
            },
            {
                'model': 'One-time Purchase',
                'description': 'Single upfront payment for full access',
                'pros': ['Simple pricing', 'No ongoing billing'],
                'cons': ['Limited revenue growth', 'No recurring income'],
                'suitability': 'Medium'
            }
        ]
        
        return models
    
    def _generate_pricing_strategies(self, app_category: str) -> List[Dict[str, Any]]:
        strategies = [
            {
                'strategy': 'Value-based Pricing',
                'description': 'Price based on value delivered to users',
                'recommended_for': ['productivity', 'business'],
                'price_range': '$5-50/month'
            },
            {
                'strategy': 'Competitive Pricing',
                'description': 'Price similar to existing competitors',
                'recommended_for': ['social', 'entertainment'],
                'price_range': '$1-10/month'
            },
            {
                'strategy': 'Penetration Pricing',
                'description': 'Low initial price to gain market share',
                'recommended_for': ['new markets', 'utility'],
                'price_range': '$0.99-5/month'
            }
        ]
        
        return [s for s in strategies if app_category in s['recommended_for'] or 'all' in s['recommended_for']]
    
    def _generate_growth_strategies(self, target_market: str) -> List[str]:
        strategies = [
            "Content marketing and SEO optimization",
            "Social media community building",
            "Referral and viral sharing mechanisms",
            "Partnership with complementary services",
            "App store optimization (ASO)",
            "Influencer and blogger outreach",
            "Free trial and freemium conversion optimization"
        ]
        
        return strategies[:5]
    
    def _generate_market_entry_strategy(self, app_category: str) -> Dict[str, Any]:
        return {
            'target_segment': 'Early adopters and tech-savvy users',
            'launch_channels': ['Product Hunt', 'Reddit communities', 'Tech blogs'],
            'initial_features': 'Core MVP with essential functionality',
            'success_metrics': ['User acquisition rate', 'User engagement', 'Feature usage'],
            'timeline': '3-6 months for initial market validation'
        }

idea_generator = IdeaGenerator()