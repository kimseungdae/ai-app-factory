#!/usr/bin/env python3
"""
AI App Factory - Main Application
Automated system for generating AI-powered application ideas and designs
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config import config
from utils.api_clients import api_manager, APIClientError
from agents.ux_researcher import ux_researcher
from agents.trend_collector import trend_collector
from agents.idea_generator import idea_generator
from agents.design_generator import design_generator

# Configure logging
def setup_logging():
    """Configure logging for the application"""
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    log_format = config.log_format
    
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_dir / 'app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set library loggers to WARNING to reduce noise
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)

class AIAppFactory:
    """Main application class for AI App Factory"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing {config.app_name}")
        
        # Initialize agents
        self.agents = {
            'ux_researcher': ux_researcher,
            'trend_collector': trend_collector,
            'idea_generator': idea_generator,
            'design_generator': design_generator
        }
        
        self.results = {}
    
    def generate_complete_app_concept(self, topic: str, industry: str = 'general') -> Dict[str, Any]:
        """
        Generate a complete app concept including market research, ideas, and design
        
        Args:
            topic: The main topic or problem area to focus on
            industry: The industry context (e.g., 'fintech', 'healthtech', 'edtech')
        
        Returns:
            Dictionary containing all generated results
        """
        try:
            self.logger.info(f"Starting complete app concept generation for topic: {topic}, industry: {industry}")
            
            # Step 1: Collect market trends
            self.logger.info("Step 1: Collecting market trends...")
            market_trends = trend_collector.collect_market_trends(industry)
            tech_trends = trend_collector.collect_tech_trends()
            
            # Step 2: Research user pain points
            self.logger.info("Step 2: Researching user pain points...")
            user_research = ux_researcher.research_user_pain_points(topic)
            user_behavior = ux_researcher.analyze_user_behavior(industry)
            
            # Step 3: Generate app ideas
            self.logger.info("Step 3: Generating app ideas...")
            app_ideas = idea_generator.generate_app_ideas(
                {**market_trends, **tech_trends},
                {**user_research, **user_behavior}
            )
            
            # Step 4: Select best idea and generate features
            if app_ideas.get('top_ideas'):
                best_idea = app_ideas['top_ideas'][0]
                self.logger.info(f"Step 4: Generating features for best idea: {best_idea.get('title', 'Unknown')}")
                
                feature_ideas = idea_generator.generate_feature_ideas(
                    best_idea.get('title', 'Unknown App'),
                    [best_idea.get('target_market', 'general users')]
                )
                
                business_model = idea_generator.generate_business_model_ideas(best_idea)
                
                # Step 5: Generate design concepts
                self.logger.info("Step 5: Generating design concepts...")
                design_concept = design_generator.generate_ui_wireframes(
                    {**best_idea, **feature_ideas}
                )
                
                ux_flow = design_generator.generate_user_experience_flow(
                    feature_ideas.get('core_features', [])
                )
                
                visual_design = design_generator.generate_visual_design_concepts(best_idea)
                
                # Compile results
                complete_concept = {
                    'project_info': {
                        'topic': topic,
                        'industry': industry,
                        'generated_at': datetime.now().isoformat(),
                        'app_factory_version': config.get('app.version', '1.0.0')
                    },
                    'market_research': {
                        'market_trends': market_trends,
                        'tech_trends': tech_trends,
                        'user_research': user_research,
                        'user_behavior': user_behavior
                    },
                    'app_concept': {
                        'selected_idea': best_idea,
                        'all_ideas': app_ideas,
                        'features': feature_ideas,
                        'business_model': business_model
                    },
                    'design_concepts': {
                        'ui_wireframes': design_concept,
                        'ux_flow': ux_flow,
                        'visual_design': visual_design
                    }
                }
                
                self.results = complete_concept
                self.logger.info("Complete app concept generation finished successfully")
                return complete_concept
            
            else:
                self.logger.error("No app ideas were generated")
                return {"error": "Failed to generate app ideas"}
            
        except Exception as e:
            self.logger.error(f"Error in complete app concept generation: {e}")
            return {"error": str(e)}
    
    def generate_market_analysis(self, industry: str = 'general') -> Dict[str, Any]:
        """Generate market analysis for a specific industry"""
        try:
            self.logger.info(f"Generating market analysis for industry: {industry}")
            
            market_trends = trend_collector.collect_market_trends(industry)
            tech_trends = trend_collector.collect_tech_trends()
            social_trends = trend_collector.collect_social_trends()
            
            trend_summary = trend_collector.get_trend_summary()
            
            return {
                'industry': industry,
                'market_trends': market_trends,
                'tech_trends': tech_trends,
                'social_trends': social_trends,
                'trend_summary': trend_summary,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating market analysis: {e}")
            return {"error": str(e)}
    
    def generate_user_research(self, topic: str, app_category: str = 'general') -> Dict[str, Any]:
        """Generate user research for a specific topic and app category"""
        try:
            self.logger.info(f"Generating user research for topic: {topic}, category: {app_category}")
            
            pain_points = ux_researcher.research_user_pain_points(topic)
            user_behavior = ux_researcher.analyze_user_behavior(app_category)
            market_trends = ux_researcher.research_market_trends([topic])
            
            return {
                'topic': topic,
                'app_category': app_category,
                'pain_points': pain_points,
                'user_behavior': user_behavior,
                'market_trends': market_trends,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating user research: {e}")
            return {"error": str(e)}
    
    def generate_app_ideas_only(self, market_data: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate app ideas based on provided market and user data"""
        try:
            self.logger.info("Generating app ideas from provided data")
            
            app_ideas = idea_generator.generate_app_ideas(market_data, user_data)
            
            return app_ideas
            
        except Exception as e:
            self.logger.error(f"Error generating app ideas: {e}")
            return {"error": str(e)}
    
    def generate_design_only(self, app_idea: Dict[str, Any]) -> Dict[str, Any]:
        """Generate design concepts for a specific app idea"""
        try:
            self.logger.info(f"Generating design for app: {app_idea.get('title', 'Unknown')}")
            
            wireframes = design_generator.generate_ui_wireframes(app_idea)
            ux_flow = design_generator.generate_user_experience_flow(
                app_idea.get('core_features', [])
            )
            visual_design = design_generator.generate_visual_design_concepts(app_idea)
            
            return {
                'wireframes': wireframes,
                'ux_flow': ux_flow,
                'visual_design': visual_design,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating design: {e}")
            return {"error": str(e)}
    
    def save_results(self, results: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save results to a file"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"app_concept_{timestamp}.json"
            
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / filename
            
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Results saved to: {output_file}")
            return str(output_file)
            
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")
            return ""
    
    def check_agent_status(self) -> Dict[str, Any]:
        """Check the status of all agents"""
        agent_status = {}
        
        for agent_name, agent in self.agents.items():
            try:
                if hasattr(agent, 'enabled'):
                    agent_status[agent_name] = {
                        'enabled': agent.enabled,
                        'status': 'ready' if agent.enabled else 'disabled'
                    }
                else:
                    agent_status[agent_name] = {
                        'enabled': True,
                        'status': 'ready'
                    }
            except Exception as e:
                agent_status[agent_name] = {
                    'enabled': False,
                    'status': f'error: {str(e)}'
                }
        
        return agent_status

def main():
    """Main entry point for the application"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    parser = argparse.ArgumentParser(description='AI App Factory - Generate AI-powered app concepts')
    parser.add_argument('--topic', type=str, help='Main topic or problem area')
    parser.add_argument('--industry', type=str, default='general', 
                       help='Industry context (fintech, healthtech, edtech, etc.)')
    parser.add_argument('--mode', type=str, default='complete',
                       choices=['complete', 'market', 'research', 'ideas', 'design'],
                       help='Generation mode')
    parser.add_argument('--output', type=str, help='Output filename')
    parser.add_argument('--status', action='store_true', help='Check agent status')
    
    args = parser.parse_args()
    
    try:
        app_factory = AIAppFactory()
        
        if args.status:
            status = app_factory.check_agent_status()
            print("\n=== Agent Status ===")
            for agent_name, info in status.items():
                print(f"{agent_name}: {info['status']}")
            return
        
        if not args.topic and args.mode not in ['market']:
            print("Error: --topic is required for most modes")
            parser.print_help()
            return
        
        results = {}
        
        if args.mode == 'complete':
            results = app_factory.generate_complete_app_concept(args.topic, args.industry)
        elif args.mode == 'market':
            results = app_factory.generate_market_analysis(args.industry)
        elif args.mode == 'research':
            results = app_factory.generate_user_research(args.topic, args.industry)
        else:
            print(f"Mode '{args.mode}' not fully implemented yet")
            return
        
        if results and 'error' not in results:
            print(f"\n=== Generated Results ===")
            
            # Save results
            output_file = app_factory.save_results(results, args.output)
            if output_file:
                print(f"Results saved to: {output_file}")
            
            # Print summary
            if args.mode == 'complete':
                app_concept = results.get('app_concept', {})
                selected_idea = app_concept.get('selected_idea', {})
                print(f"\nBest App Idea: {selected_idea.get('title', 'Unknown')}")
                print(f"Category: {selected_idea.get('category', 'Unknown')}")
                print(f"Target Market: {selected_idea.get('target_market', 'Unknown')}")
                print(f"Ranking Score: {selected_idea.get('ranking_score', 'N/A')}")
            
            elif args.mode == 'market':
                print(f"\nMarket Analysis for: {args.industry}")
                if 'trend_summary' in results:
                    summary = results['trend_summary']
                    print(f"Top Tech Trends: {len(summary.get('technology', []))}")
                    print(f"Top Market Trends: {len(summary.get('market', []))}")
                    print(f"Top Social Trends: {len(summary.get('social', []))}")
            
            elif args.mode == 'research':
                print(f"\nUser Research for: {args.topic}")
                pain_points = results.get('pain_points', {})
                print(f"Pain Points Found: {len(pain_points.get('pain_points', []))}")
                user_behavior = results.get('user_behavior', {})
                print(f"Behavior Patterns: {len(user_behavior.get('behavior_patterns', []))}")
        
        else:
            print(f"Error: {results.get('error', 'Unknown error occurred')}")
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()