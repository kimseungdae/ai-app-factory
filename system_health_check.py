#!/usr/bin/env python3
"""
AI App Factory System Health Check
Verifies all components are working and properly integrated
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import importlib
import json
from datetime import datetime

def check_system_health():
    """Comprehensive system health check"""
    print("🏥 AI App Factory System Health Check")
    print("=" * 50)
    
    health_report = {
        'timestamp': datetime.now().isoformat(),
        'overall_status': 'healthy',
        'components': {},
        'integrations': {},
        'recommendations': []
    }
    
    # Check 1: Import all agents
    print("\n📦 Component Import Check:")
    print("-" * 30)
    
    components = [
        ('TrendCollector', 'agents.trend_collector', 'trend_collector'),
        ('UXResearcher', 'agents.ux_researcher', 'ux_researcher'),
        ('IdeaGenerator', 'agents.idea_generator', 'idea_generator'),
        ('DesignSystemGenerator', 'agents.design_system_generator', 'design_system_generator')
    ]
    
    for component_name, module_path, instance_name in components:
        try:
            module = importlib.import_module(module_path)
            instance = getattr(module, instance_name)
            enabled = getattr(instance, 'enabled', True)
            
            status = '✅ Available' if enabled else '⚠️  Disabled'
            print(f"   {component_name}: {status}")
            
            health_report['components'][component_name] = {
                'status': 'available' if enabled else 'disabled',
                'enabled': enabled,
                'module_path': module_path
            }
            
            if not enabled:
                health_report['recommendations'].append(f"Enable {component_name} in config/settings.yaml")
        
        except ImportError as e:
            print(f"   {component_name}: ❌ Import Error - {e}")
            health_report['components'][component_name] = {
                'status': 'error',
                'error': str(e)
            }
            health_report['overall_status'] = 'degraded'
        
        except Exception as e:
            print(f"   {component_name}: ❌ Unknown Error - {e}")
            health_report['components'][component_name] = {
                'status': 'error',
                'error': str(e)
            }
            health_report['overall_status'] = 'degraded'
    
    # Check 2: Configuration validation
    print(f"\n⚙️  Configuration Check:")
    print("-" * 30)
    
    config_issues = check_configuration()
    for issue in config_issues:
        print(f"   ⚠️  {issue}")
        health_report['recommendations'].append(issue)
    
    if not config_issues:
        print("   ✅ Configuration is valid")
    
    # Check 3: API Dependencies
    print(f"\n🌐 API Dependencies Check:")
    print("-" * 30)
    
    api_status = check_api_dependencies()
    health_report['api_dependencies'] = api_status
    
    for api_name, status in api_status.items():
        icon = '✅' if status['available'] else '❌'
        print(f"   {api_name}: {icon} {status['status']}")
        
        if not status['available'] and status['required']:
            health_report['overall_status'] = 'degraded'
            health_report['recommendations'].append(f"Configure {api_name} API key")
    
    # Check 4: Integration tests
    print(f"\n🔄 Integration Tests:")
    print("-" * 30)
    
    integration_results = run_integration_tests()
    health_report['integrations'] = integration_results
    
    for test_name, result in integration_results.items():
        icon = '✅' if result['passed'] else '❌'
        print(f"   {test_name}: {icon} {result['status']}")
        
        if not result['passed']:
            health_report['overall_status'] = 'degraded'
    
    # Check 5: File system permissions
    print(f"\n📁 File System Check:")
    print("-" * 30)
    
    fs_check = check_file_system()
    if fs_check['writable']:
        print("   ✅ Output directories are writable")
    else:
        print("   ❌ Cannot write to output directories")
        health_report['overall_status'] = 'error'
        health_report['recommendations'].append("Check file system permissions")
    
    # Generate final report
    print(f"\n📊 System Health Summary:")
    print("=" * 40)
    
    status_icon = {
        'healthy': '🟢',
        'degraded': '🟡', 
        'error': '🔴'
    }
    
    overall_status = health_report['overall_status']
    print(f"Overall Status: {status_icon[overall_status]} {overall_status.upper()}")
    
    enabled_components = sum(1 for comp in health_report['components'].values() if comp.get('enabled', False))
    total_components = len(health_report['components'])
    print(f"Components: {enabled_components}/{total_components} enabled")
    
    available_apis = sum(1 for api in health_report['api_dependencies'].values() if api['available'])
    total_apis = len(health_report['api_dependencies'])
    print(f"APIs: {available_apis}/{total_apis} available")
    
    passed_tests = sum(1 for test in health_report['integrations'].values() if test['passed'])
    total_tests = len(health_report['integrations'])
    print(f"Integration Tests: {passed_tests}/{total_tests} passed")
    
    # Recommendations
    if health_report['recommendations']:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(health_report['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    # Save health report
    report_filename = f"system_health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(health_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Health report saved to: {report_filename}")
    
    return health_report

def check_configuration():
    """Check configuration files and settings"""
    issues = []
    
    # Check if config files exist
    config_files = [
        'config/settings.yaml',
        '.env.example'
    ]
    
    for config_file in config_files:
        if not os.path.exists(config_file):
            issues.append(f"Missing configuration file: {config_file}")
    
    # Check Python dependencies
    required_packages = [
        'requests', 'pyyaml', 'python-dotenv', 'openai', 
        'praw', 'pytrends', 'beautifulsoup4', 'python-unsplash',
        'colorthief', 'webcolors', 'pillow'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        issues.append(f"Missing Python packages: {', '.join(missing_packages)}")
    
    return issues

def check_api_dependencies():
    """Check API key availability and configuration"""
    api_checks = {
        'OpenAI': {
            'env_var': 'OPENAI_API_KEY',
            'required': True,
            'service': 'AI text generation'
        },
        'Reddit': {
            'env_var': 'REDDIT_CLIENT_ID',
            'required': True,
            'service': 'Trend data collection'
        },
        'Unsplash': {
            'env_var': 'UNSPLASH_ACCESS_KEY',
            'required': False,
            'service': 'Image recommendations'
        },
        'Supabase': {
            'env_var': 'SUPABASE_URL',
            'required': False,
            'service': 'Data storage'
        }
    }
    
    results = {}
    
    for api_name, config in api_checks.items():
        env_var = config['env_var']
        api_key = os.getenv(env_var)
        
        if api_key and api_key != f'your_{env_var.lower()}_here':
            results[api_name] = {
                'available': True,
                'status': 'Configured',
                'required': config['required'],
                'service': config['service']
            }
        else:
            results[api_name] = {
                'available': False,
                'status': 'Not configured' if not api_key else 'Example value detected',
                'required': config['required'],
                'service': config['service']
            }
    
    return results

def run_integration_tests():
    """Run basic integration tests between components"""
    results = {}
    
    # Test 1: TrendCollector basic functionality
    try:
        from agents.trend_collector import trend_collector
        
        if trend_collector.enabled:
            # Test keyword extraction (without API calls)
            test_text = "AI productivity app for remote workers"
            keywords = trend_collector._extract_keywords_from_text(test_text)
            
            results['TrendCollector'] = {
                'passed': len(keywords) > 0,
                'status': f'Extracted {len(keywords)} keywords' if len(keywords) > 0 else 'No keywords extracted',
                'details': f'Sample keywords: {list(keywords)[:3]}'
            }
        else:
            results['TrendCollector'] = {
                'passed': True,
                'status': 'Disabled - test skipped',
                'details': 'Component is disabled in configuration'
            }
    except Exception as e:
        results['TrendCollector'] = {
            'passed': False,
            'status': f'Error: {e}',
            'details': 'Failed to test basic functionality'
        }
    
    # Test 2: UXResearcher fallback functionality
    try:
        from agents.ux_researcher import ux_researcher
        
        if ux_researcher.enabled:
            # Test fallback persona generation
            fallback_personas = ux_researcher._create_fallback_personas('test app', 'productivity')
            
            results['UXResearcher'] = {
                'passed': len(fallback_personas) == 3,
                'status': f'Generated {len(fallback_personas)} fallback personas',
                'details': f'Persona names: {[p["name"] for p in fallback_personas]}'
            }
        else:
            results['UXResearcher'] = {
                'passed': True,
                'status': 'Disabled - test skipped',
                'details': 'Component is disabled in configuration'
            }
    except Exception as e:
        results['UXResearcher'] = {
            'passed': False,
            'status': f'Error: {e}',
            'details': 'Failed to test fallback functionality'
        }
    
    # Test 3: DesignSystemGenerator color generation
    try:
        from agents.design_system_generator import design_system_generator
        
        if design_system_generator.enabled:
            # Test color palette generation
            color_palette = design_system_generator._create_fallback_color_palette('health')
            
            has_colors = 'colors' in color_palette and 'primary' in color_palette['colors']
            
            results['DesignSystemGenerator'] = {
                'passed': has_colors,
                'status': 'Generated color palette' if has_colors else 'Failed to generate colors',
                'details': f'Primary color: {color_palette.get("colors", {}).get("primary", {}).get("500", "N/A")}'
            }
        else:
            results['DesignSystemGenerator'] = {
                'passed': True,
                'status': 'Disabled - test skipped',
                'details': 'Component is disabled in configuration'
            }
    except Exception as e:
        results['DesignSystemGenerator'] = {
            'passed': False,
            'status': f'Error: {e}',
            'details': 'Failed to test color generation'
        }
    
    # Test 4: Complete workflow instantiation
    try:
        from complete_workflow import AIAppFactory
        
        factory = AIAppFactory()
        has_agents = len(factory.agents) == 4
        
        results['CompleteWorkflow'] = {
            'passed': has_agents,
            'status': f'Initialized with {len(factory.agents)} agents',
            'details': f'Available agents: {list(factory.agents.keys())}'
        }
    except Exception as e:
        results['CompleteWorkflow'] = {
            'passed': False,
            'status': f'Error: {e}',
            'details': 'Failed to initialize workflow'
        }
    
    return results

def check_file_system():
    """Check file system permissions and directory structure"""
    try:
        # Test write permissions
        test_file = 'health_check_test.tmp'
        with open(test_file, 'w') as f:
            f.write('test')
        
        # Clean up
        os.remove(test_file)
        
        return {
            'writable': True,
            'message': 'Can write to current directory'
        }
    except Exception as e:
        return {
            'writable': False,
            'message': f'Cannot write to current directory: {e}'
        }

def generate_setup_guide(health_report):
    """Generate a setup guide based on health report findings"""
    print(f"\n📋 Setup Guide:")
    print("=" * 30)
    
    if health_report['overall_status'] == 'healthy':
        print("✅ System is healthy! You're ready to go.")
        print(f"\n🚀 Quick Start:")
        print("   python complete_workflow.py")
        return
    
    print("🔧 Follow these steps to fix issues:")
    
    step = 1
    
    # Check for missing packages
    for component, details in health_report['components'].items():
        if details.get('status') == 'error' and 'ImportError' in str(details.get('error', '')):
            print(f"\n{step}. Install missing dependencies:")
            print("   pip install -r requirements.txt")
            step += 1
            break
    
    # Check for API configuration
    missing_apis = [
        api_name for api_name, details in health_report.get('api_dependencies', {}).items()
        if not details['available'] and details['required']
    ]
    
    if missing_apis:
        print(f"\n{step}. Configure required API keys:")
        print("   cp .env.example .env")
        print("   # Edit .env file with your API keys:")
        for api in missing_apis:
            if api == 'OpenAI':
                print("   # Get OpenAI key from: https://platform.openai.com/")
            elif api == 'Reddit':
                print("   # Get Reddit keys from: https://www.reddit.com/prefs/apps/")
        step += 1
    
    # Check for disabled components
    disabled_components = [
        comp for comp, details in health_report['components'].items()
        if details.get('enabled') == False
    ]
    
    if disabled_components:
        print(f"\n{step}. Enable disabled components:")
        print("   # Edit config/settings.yaml:")
        for comp in disabled_components:
            comp_key = comp.lower().replace('generator', '').replace('collector', '').replace('researcher', '')
            print(f"   # Set agents.{comp_key}.enabled: true")
        step += 1
    
    print(f"\n{step}. Run health check again:")
    print("   python system_health_check.py")

if __name__ == "__main__":
    print("🏥 Starting comprehensive system health check...")
    
    try:
        health_report = check_system_health()
        generate_setup_guide(health_report)
        
        print(f"\n🎯 Next Steps:")
        if health_report['overall_status'] == 'healthy':
            print("   • Run: python complete_workflow.py")
            print("   • Or test individual components:")
            print("     - python test_trend_collector.py")
            print("     - python test_ux_researcher.py") 
            print("     - python test_design_system.py")
            print("     - python test_trend_to_ux.py")
        else:
            print("   • Fix the issues mentioned above")
            print("   • Run this health check again")
            print("   • Check the documentation for detailed setup instructions")
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        print("💡 This might indicate a serious configuration issue.")
        print("   Please check your Python environment and file permissions.")
    
    print(f"\n✅ Health check complete!")