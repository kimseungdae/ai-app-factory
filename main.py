#!/usr/bin/env python3
"""
AI App Factory Main Entry Point
Complete orchestration of the AI App Factory workflow
"""

import os
import sys
import argparse
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from orchestrator.app_factory_orchestrator import AppFactoryOrchestrator, WorkflowConfig

def setup_logging():
    """로깅 설정"""
    import logging
    
    # Create logs directory
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    log_filename = logs_dir / f"ai_app_factory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def print_banner():
    """AI App Factory 배너 출력"""
    banner = """
🏭 ═════════════════════════════════════════════════════════
   ██████╗ ██╗    ██████╗ ██████╗ ██████╗     ███████╗ █████╗  ██████╗████████╗ ██████╗ ██████╗ ██╗   ██╗
  ██╔══██╗██║   ██╔══██╗██╔══██╗██╔══██╗    ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝
  ██████╔╝██║   ██████╔╝██████╔╝██████╔╝    █████╗  ███████║██║        ██║   ██║   ██║██████╔╝ ╚████╔╝ 
  ██╔══██╗██║   ██╔══██╗██╔═══╝ ██╔═══╝     ██╔══╝  ██╔══██║██║        ██║   ██║   ██║██╔══██╗  ╚██╔╝  
  ██║  ██║██║   ██║  ██║██║     ██║         ██║     ██║  ██║╚██████╗   ██║   ╚██████╔╝██║  ██║   ██║   
  ╚═╝  ╚═╝╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝         ╚═╝     ╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
                                                                                                            
   🚀 Complete AI-Powered App Development Automation
   📊 Trend Collection → 🎯 UX Analysis → 🎨 Design System → 🏗️ Prototype → 🚀 Deployment
🏭 ═════════════════════════════════════════════════════════
"""
    print(banner)

def validate_environment():
    """환경 설정 검증"""
    logger = setup_logging()
    
    logger.info("🔍 Validating environment configuration...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8+ required")
        return False
    
    # Check required environment variables
    required_env_vars = {
        'OPENAI_API_KEY': 'OpenAI API (for UX analysis)',
        'REDDIT_CLIENT_ID': 'Reddit API (for trend collection)',
        'REDDIT_CLIENT_SECRET': 'Reddit API (for trend collection)',
        'REDDIT_REFRESH_TOKEN': 'Reddit API (for trend collection)'
    }
    
    missing_vars = []
    for var, description in required_env_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    # Check optional environment variables
    optional_env_vars = {
        'UNSPLASH_ACCESS_KEY': 'Unsplash API (for images)',
        'SUPABASE_URL': 'Supabase (for data storage)',
        'SUPABASE_KEY': 'Supabase (for data storage)',
        'NOTION_TOKEN': 'Notion API (for reporting)',
        'NOTION_DATABASE_ID': 'Notion Database (for reporting)',
        'FIGMA_ACCESS_TOKEN': 'Figma API (for design integration)',
        'VERCEL_TOKEN': 'Vercel API (for deployment)'
    }
    
    optional_missing = []
    for var, description in optional_env_vars.items():
        if not os.getenv(var):
            optional_missing.append(f"{var} ({description})")
    
    # Report results
    if missing_vars:
        logger.warning("⚠️  Missing required environment variables:")
        for var in missing_vars:
            logger.warning(f"   • {var}")
        logger.warning("⚠️  Some features may not work properly")
    else:
        logger.info("✅ All required environment variables found")
    
    if optional_missing:
        logger.info("ℹ️  Optional features available with additional setup:")
        for var in optional_missing:
            logger.info(f"   • {var}")
    
    return True

def parse_arguments():
    """명령행 인수 파싱"""
    parser = argparse.ArgumentParser(
        description='AI App Factory - Complete automated app development pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --trend "AI fitness" --output-dir "./my_apps"
  %(prog)s --trend "meditation apps" --category health --no-supabase
  %(prog)s --trend "productivity tools" --max-retries 5 --notion-report
  %(prog)s --status workflow_20231201_120000
        """
    )
    
    # Main workflow arguments
    parser.add_argument(
        '--trend', 
        type=str, 
        help='Trend keyword to analyze and build app for (e.g., "AI fitness", "meditation apps")'
    )
    
    parser.add_argument(
        '--category',
        type=str,
        choices=['health', 'productivity', 'finance', 'education', 'entertainment', 'social', 'business'],
        help='App category (auto-detected if not specified)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./generated_apps',
        help='Output directory for generated apps (default: ./generated_apps)'
    )
    
    # Workflow control arguments
    parser.add_argument(
        '--max-retries',
        type=int,
        default=3,
        help='Maximum number of retries per stage (default: 3)'
    )
    
    parser.add_argument(
        '--retry-delay',
        type=int,
        default=5,
        help='Delay between retries in seconds (default: 5)'
    )
    
    # Storage and reporting arguments
    parser.add_argument(
        '--no-supabase',
        action='store_true',
        help='Disable Supabase storage'
    )
    
    parser.add_argument(
        '--notion-report',
        action='store_true',
        help='Generate Notion report (requires NOTION_TOKEN and NOTION_DATABASE_ID)'
    )
    
    parser.add_argument(
        '--no-monitoring',
        action='store_true',
        help='Disable workflow monitoring'
    )
    
    # Utility arguments
    parser.add_argument(
        '--status',
        type=str,
        metavar='WORKFLOW_ID',
        help='Check status of existing workflow'
    )
    
    parser.add_argument(
        '--list-workflows',
        action='store_true',
        help='List recent workflows'
    )
    
    parser.add_argument(
        '--validate-env',
        action='store_true',
        help='Validate environment configuration and exit'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate workflow without executing (for testing)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()

def configure_logging_level(verbose: bool):
    """로깅 레벨 설정"""
    import logging
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('orchestrator').setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

def list_recent_workflows():
    """최근 워크플로우 목록 출력"""
    logger = setup_logging()
    
    # Look for workflow result files
    result_files = list(Path('.').glob('*workflow_result_*.json'))
    result_files.extend(list(Path('.').glob('ai_app_factory_complete_result_*.json')))
    
    if not result_files:
        logger.info("📭 No recent workflows found")
        return
    
    logger.info("📋 Recent Workflows:")
    logger.info("-" * 60)
    
    for file_path in sorted(result_files, key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            workflow_info = data.get('workflow_info', data.get('generated_app', {}))
            trend = workflow_info.get('trend_keyword', workflow_info.get('name', 'Unknown'))
            status = workflow_info.get('status', 'Unknown')
            timestamp = workflow_info.get('start_time', workflow_info.get('timestamp', 'Unknown'))
            
            if timestamp != 'Unknown' and 'T' in timestamp:
                timestamp = timestamp.split('T')[0]
            
            logger.info(f"  📱 {trend} | {status} | {timestamp}")
            
        except Exception as e:
            logger.warning(f"⚠️  Could not read {file_path}: {e}")

def check_workflow_status(workflow_id: str):
    """워크플로우 상태 확인"""
    logger = setup_logging()
    
    # Look for workflow result file
    result_files = list(Path('.').glob(f'*{workflow_id}*.json'))
    
    if not result_files:
        logger.error(f"❌ Workflow {workflow_id} not found")
        return
    
    result_file = result_files[0]
    
    try:
        with open(result_file, 'r') as f:
            data = json.load(f)
        
        logger.info(f"📊 Workflow Status: {workflow_id}")
        logger.info("-" * 50)
        
        # Workflow info
        workflow_info = data.get('workflow_info', {})
        logger.info(f"🎯 Trend: {workflow_info.get('trend_keyword', 'N/A')}")
        logger.info(f"📈 Status: {workflow_info.get('status', 'N/A')}")
        logger.info(f"⏱️  Duration: {workflow_info.get('total_duration', 'N/A')}")
        
        # Stage results
        stage_results = data.get('stage_results', {})
        if stage_results:
            logger.info("\n📋 Stage Results:")
            for stage, result in stage_results.items():
                status_emoji = "✅" if result.get('status') == 'completed' else "❌"
                logger.info(f"  {status_emoji} {stage}: {result.get('status', 'N/A')}")
        
        # Generated outputs
        generated_outputs = data.get('generated_outputs', data.get('generated_app', {}))
        if generated_outputs:
            logger.info("\n🎯 Generated Outputs:")
            if 'project_path' in generated_outputs:
                logger.info(f"  📁 Project: {generated_outputs['project_path']}")
            if 'name' in generated_outputs:
                logger.info(f"  📱 App: {generated_outputs['name']}")
        
    except Exception as e:
        logger.error(f"❌ Error reading workflow status: {e}")

def run_workflow(args):
    """메인 워크플로우 실행"""
    logger = setup_logging()
    configure_logging_level(args.verbose)
    
    if not args.trend:
        logger.error("❌ Trend keyword is required. Use --trend 'your keyword'")
        return False
    
    logger.info(f"🚀 Starting AI App Factory workflow for: {args.trend}")
    
    # Create workflow configuration
    config = WorkflowConfig(
        trend_keyword=args.trend,
        category=args.category,
        output_dir=args.output_dir,
        max_retries=args.max_retries,
        retry_delay=args.retry_delay,
        save_to_supabase=not args.no_supabase,
        generate_notion_report=args.notion_report,
        enable_monitoring=not args.no_monitoring
    )
    
    if args.dry_run:
        logger.info("🧪 DRY RUN MODE - Simulating workflow...")
        logger.info(f"   Trend: {config.trend_keyword}")
        logger.info(f"   Category: {config.category}")
        logger.info(f"   Output: {config.output_dir}")
        logger.info(f"   Max Retries: {config.max_retries}")
        logger.info(f"   Supabase: {config.save_to_supabase}")
        logger.info(f"   Notion: {config.generate_notion_report}")
        logger.info("✅ Configuration validated - workflow would execute successfully")
        return True
    
    try:
        # Create and execute orchestrator
        orchestrator = AppFactoryOrchestrator(config)
        
        # Execute workflow
        start_time = datetime.now()
        result = orchestrator.execute_workflow()
        end_time = datetime.now()
        
        # Save result to file
        result_filename = f"workflow_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Print summary
        logger.info("\n" + "="*60)
        logger.info("🎉 AI App Factory Workflow Completed!")
        logger.info("="*60)
        
        workflow_info = result.get('workflow_info', {})
        logger.info(f"📊 Status: {workflow_info.get('status', 'Unknown')}")
        logger.info(f"⏱️  Total Duration: {workflow_info.get('total_duration', 'N/A')} seconds")
        logger.info(f"📈 Success Rate: {result.get('performance_metrics', {}).get('success_rate', 'N/A')}")
        
        # Show generated outputs
        generated_outputs = result.get('generated_outputs', {})
        if 'prototype_build' in generated_outputs:
            prototype_info = generated_outputs['prototype_build'].get('project_info', {})
            if prototype_info:
                logger.info(f"\n🎯 Generated App:")
                logger.info(f"   📱 Name: {prototype_info.get('app_name', 'N/A')}")
                logger.info(f"   📁 Location: {prototype_info.get('project_path', 'N/A')}")
        
        # Show next steps
        next_steps = result.get('next_steps', [])
        if next_steps:
            logger.info(f"\n🚀 Next Steps:")
            for i, step in enumerate(next_steps[:5], 1):
                logger.info(f"   {i}. {step}")
        
        logger.info(f"\n💾 Full results saved to: {result_filename}")
        
        return workflow_info.get('status') == 'completed'
        
    except Exception as e:
        logger.error(f"❌ Workflow execution failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return False

def main():
    """메인 함수"""
    try:
        args = parse_arguments()
        
        # Print banner
        print_banner()
        
        # Handle utility commands
        if args.validate_env:
            return validate_environment()
        
        if args.list_workflows:
            list_recent_workflows()
            return True
        
        if args.status:
            check_workflow_status(args.status)
            return True
        
        # Validate environment
        if not validate_environment():
            print("\n⚠️  Environment validation failed. Some features may not work properly.")
            print("💡 Run with --validate-env for detailed information.")
        
        # Run main workflow
        success = run_workflow(args)
        
        if success:
            print("\n🎉 AI App Factory completed successfully!")
            print("💡 Run --list-workflows to see all workflows")
        else:
            print("\n❌ AI App Factory execution failed")
            print("💡 Check the logs for detailed error information")
        
        return success
        
    except KeyboardInterrupt:
        print("\n⏹️  Workflow interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)