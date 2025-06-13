#!/usr/bin/env python3
"""
AppFactoryOrchestrator - 전체 AI App Factory 워크플로우 관리
모든 에이전트를 연결하고 전체 플로우를 조율하는 중앙 제어 시스템
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app_factory.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WorkflowStage(Enum):
    """워크플로우 단계 정의"""
    TREND_COLLECTION = "trend_collection"
    UX_ANALYSIS = "ux_analysis"
    DESIGN_SYSTEM = "design_system"
    PROTOTYPE_BUILD = "prototype_build"
    DEPLOYMENT = "deployment"
    REPORTING = "reporting"

class StageStatus(Enum):
    """단계별 상태 정의"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class StageResult:
    """각 단계의 실행 결과"""
    stage: WorkflowStage
    status: StageStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0

@dataclass
class WorkflowConfig:
    """워크플로우 설정"""
    trend_keyword: str
    category: Optional[str] = None
    output_dir: str = "./generated_apps"
    max_retries: int = 3
    retry_delay: int = 5
    save_to_supabase: bool = True
    generate_notion_report: bool = True
    enable_monitoring: bool = True

class AppFactoryOrchestrator:
    """AI App Factory의 전체 워크플로우를 관리하는 오케스트레이터"""
    
    def __init__(self, config: WorkflowConfig):
        self.config = config
        self.workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.stage_results: Dict[WorkflowStage, StageResult] = {}
        self.workflow_start_time = None
        self.workflow_end_time = None
        
        # Initialize agents
        self._initialize_agents()
        
        # Initialize storage clients
        self._initialize_storage()
        
        logger.info(f"AppFactoryOrchestrator initialized with workflow ID: {self.workflow_id}")
    
    def _initialize_agents(self):
        """AI 에이전트들을 초기화"""
        try:
            # Import agents dynamically to handle import errors gracefully
            self.agents = {}
            
            # TrendCollector
            try:
                from agents.trend_collector import TrendCollector
                self.agents['trend_collector'] = TrendCollector()
                logger.info("✅ TrendCollector initialized")
            except Exception as e:
                logger.warning(f"⚠️ TrendCollector initialization failed: {e}")
                self.agents['trend_collector'] = None
            
            # UXResearcher
            try:
                from agents.ux_researcher import UXResearcher
                self.agents['ux_researcher'] = UXResearcher()
                logger.info("✅ UXResearcher initialized")
            except Exception as e:
                logger.warning(f"⚠️ UXResearcher initialization failed: {e}")
                self.agents['ux_researcher'] = None
            
            # DesignSystemGenerator
            try:
                from agents.design_system_generator import DesignSystemGenerator
                self.agents['design_system_generator'] = DesignSystemGenerator()
                logger.info("✅ DesignSystemGenerator initialized")
            except Exception as e:
                logger.warning(f"⚠️ DesignSystemGenerator initialization failed: {e}")
                self.agents['design_system_generator'] = None
            
            # PrototypeBuilder
            try:
                from agents.prototype_builder import PrototypeBuilder
                self.agents['prototype_builder'] = PrototypeBuilder()
                logger.info("✅ PrototypeBuilder initialized")
            except Exception as e:
                logger.warning(f"⚠️ PrototypeBuilder initialization failed: {e}")
                self.agents['prototype_builder'] = None
                
        except Exception as e:
            logger.error(f"❌ Agent initialization failed: {e}")
            # Create mock agents for testing
            self._create_mock_agents()
    
    def _create_mock_agents(self):
        """테스트용 Mock 에이전트 생성"""
        logger.info("Creating mock agents for testing...")
        
        class MockAgent:
            def __init__(self, name):
                self.name = name
                self.enabled = True
        
        self.agents = {
            'trend_collector': MockAgent('TrendCollector'),
            'ux_researcher': MockAgent('UXResearcher'),  
            'design_system_generator': MockAgent('DesignSystemGenerator'),
            'prototype_builder': MockAgent('PrototypeBuilder')
        }
    
    def _initialize_storage(self):
        """저장소 클라이언트 초기화"""
        # Supabase client
        self.supabase_client = None
        if self.config.save_to_supabase:
            try:
                from supabase import create_client
                supabase_url = os.getenv('SUPABASE_URL')
                supabase_key = os.getenv('SUPABASE_KEY')
                
                if supabase_url and supabase_key:
                    self.supabase_client = create_client(supabase_url, supabase_key)
                    logger.info("✅ Supabase client initialized")
                else:
                    logger.warning("⚠️ Supabase credentials not found")
            except Exception as e:
                logger.warning(f"⚠️ Supabase initialization failed: {e}")
        
        # Notion client
        self.notion_client = None
        if self.config.generate_notion_report:
            try:
                import requests
                notion_token = os.getenv('NOTION_TOKEN')
                if notion_token:
                    self.notion_client = {
                        'token': notion_token,
                        'headers': {
                            'Authorization': f'Bearer {notion_token}',
                            'Content-Type': 'application/json',
                            'Notion-Version': '2022-06-28'
                        }
                    }
                    logger.info("✅ Notion client initialized")
                else:
                    logger.warning("⚠️ Notion token not found")
            except Exception as e:
                logger.warning(f"⚠️ Notion initialization failed: {e}")
    
    def execute_workflow(self) -> Dict[str, Any]:
        """전체 워크플로우 실행"""
        logger.info(f"🚀 Starting AI App Factory workflow for: {self.config.trend_keyword}")
        
        self.workflow_start_time = datetime.now()
        
        try:
            # Define workflow stages
            workflow_stages = [
                (WorkflowStage.TREND_COLLECTION, self._execute_trend_collection),
                (WorkflowStage.UX_ANALYSIS, self._execute_ux_analysis),
                (WorkflowStage.DESIGN_SYSTEM, self._execute_design_system),
                (WorkflowStage.PROTOTYPE_BUILD, self._execute_prototype_build),
                (WorkflowStage.DEPLOYMENT, self._execute_deployment),
                (WorkflowStage.REPORTING, self._execute_reporting)
            ]
            
            # Execute each stage
            for stage, execute_func in workflow_stages:
                if not self._execute_stage_with_retry(stage, execute_func):
                    logger.error(f"❌ Workflow failed at stage: {stage.value}")
                    break
            
            self.workflow_end_time = datetime.now()
            
            # Generate final result
            final_result = self._generate_final_result()
            
            # Save to storage
            if self.config.save_to_supabase:
                self._save_to_supabase(final_result)
            
            # Generate Notion report
            if self.config.generate_notion_report:
                self._generate_notion_report(final_result)
            
            logger.info("🎉 Workflow completed successfully!")
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Workflow execution failed: {e}")
            self.workflow_end_time = datetime.now()
            return self._generate_error_result(str(e))
    
    def _execute_stage_with_retry(self, stage: WorkflowStage, execute_func: Callable) -> bool:
        """단계 실행 (재시도 로직 포함)"""
        stage_result = StageResult(
            stage=stage,
            status=StageStatus.PENDING,
            start_time=datetime.now()
        )
        
        self.stage_results[stage] = stage_result
        
        for retry_count in range(self.config.max_retries + 1):
            try:
                logger.info(f"🔄 Executing stage: {stage.value} (attempt {retry_count + 1})")
                
                stage_result.status = StageStatus.IN_PROGRESS
                stage_result.retry_count = retry_count
                
                # Execute the stage
                result_data = execute_func()
                
                # Mark as completed
                stage_result.status = StageStatus.COMPLETED
                stage_result.end_time = datetime.now()
                stage_result.duration = (stage_result.end_time - stage_result.start_time).total_seconds()
                stage_result.result_data = result_data
                
                logger.info(f"✅ Stage {stage.value} completed successfully in {stage_result.duration:.2f}s")
                return True
                
            except Exception as e:
                logger.error(f"❌ Stage {stage.value} failed (attempt {retry_count + 1}): {e}")
                
                stage_result.error_message = str(e)
                
                if retry_count < self.config.max_retries:
                    stage_result.status = StageStatus.RETRYING
                    logger.info(f"⏳ Retrying in {self.config.retry_delay} seconds...")
                    time.sleep(self.config.retry_delay)
                else:
                    stage_result.status = StageStatus.FAILED
                    stage_result.end_time = datetime.now()
                    stage_result.duration = (stage_result.end_time - stage_result.start_time).total_seconds()
                    return False
        
        return False
    
    def _execute_trend_collection(self) -> Dict[str, Any]:
        """1단계: 트렌드 수집 실행"""
        logger.info("📊 Executing trend collection...")
        
        if self.agents['trend_collector'] and hasattr(self.agents['trend_collector'], 'collect_top_trends'):
            # Use real TrendCollector
            trends = self.agents['trend_collector'].collect_top_trends(limit=10)
            
            # Find the specified trend or use the top one
            selected_trend = None
            for trend in trends.get('trends', []):
                if self.config.trend_keyword.lower() in trend.get('keyword', '').lower():
                    selected_trend = trend
                    break
            
            if not selected_trend and trends.get('trends'):
                selected_trend = trends['trends'][0]
                logger.info(f"Using top trend instead: {selected_trend.get('keyword')}")
            
            return {
                'all_trends': trends,
                'selected_trend': selected_trend,
                'collection_method': 'api'
            }
        else:
            # Mock trend collection
            logger.info("Using mock trend collection...")
            return self._mock_trend_collection()
    
    def _mock_trend_collection(self) -> Dict[str, Any]:
        """Mock 트렌드 수집 (테스트용)"""
        return {
            'selected_trend': {
                'keyword': self.config.trend_keyword,
                'score': 87.5,
                'category': self.config.category or 'productivity',
                'data_sources': ['reddit', 'google_trends'],
                'related_images': [
                    f'https://images.unsplash.com/photo-{self.config.trend_keyword.replace(" ", "-")}',
                ],
                'trend_data': {
                    'reddit_mentions': 245,
                    'google_trend_score': 85,
                    'growth_rate': '23%'
                }
            },
            'collection_method': 'mock'
        }
    
    def _execute_ux_analysis(self) -> Dict[str, Any]:
        """2단계: UX 분석 실행"""
        logger.info("🎯 Executing UX analysis...")
        
        # Get trend data from previous stage
        trend_stage = self.stage_results.get(WorkflowStage.TREND_COLLECTION)
        if not trend_stage or not trend_stage.result_data:
            raise Exception("Trend collection data not available")
        
        selected_trend = trend_stage.result_data['selected_trend']
        
        if self.agents['ux_researcher'] and hasattr(self.agents['ux_researcher'], 'analyze_ux_for_trend'):
            # Use real UXResearcher
            return self.agents['ux_researcher'].analyze_ux_for_trend(
                selected_trend['keyword'],
                selected_trend['category']
            )
        else:
            # Mock UX analysis
            logger.info("Using mock UX analysis...")
            return self._mock_ux_analysis(selected_trend)
    
    def _mock_ux_analysis(self, trend: Dict[str, Any]) -> Dict[str, Any]:
        """Mock UX 분석 (테스트용)"""
        return {
            'trend_keyword': trend['keyword'],
            'category': trend['category'],
            'personas': [
                {
                    'name': '김현수 (바쁜 직장인)',
                    'age': 28,
                    'occupation': '마케팅 매니저',
                    'pain_points': ['업무 효율성 부족', '시간 관리 어려움'],
                    'motivations': ['생산성 향상', '업무-생활 균형'],
                    'tech_comfort': 'high',
                    'preferred_platforms': ['mobile', 'desktop']
                },
                {
                    'name': '박지영 (프리랜서)',
                    'age': 32,
                    'occupation': '그래픽 디자이너',
                    'pain_points': ['클라이언트 관리', '프로젝트 일정 관리'],
                    'motivations': ['업무 체계화', '수익 증대'],
                    'tech_comfort': 'medium',
                    'preferred_platforms': ['desktop', 'tablet']
                },
                {
                    'name': '이민준 (창업 준비생)',
                    'age': 25,
                    'occupation': '예비 창업자',
                    'pain_points': ['아이디어 정리 부족', '팀 협업 도구 부족'],
                    'motivations': ['성공적인 창업', '팀 효율성'],
                    'tech_comfort': 'high',
                    'preferred_platforms': ['mobile', 'web']
                }
            ],
            'jobs_to_be_done': {
                'functional_jobs': [
                    '업무 일정을 효율적으로 관리하고 싶다',
                    '반복 작업을 자동화하고 싶다',
                    '팀과 원활하게 소통하고 싶다'
                ],
                'emotional_jobs': [
                    '업무 성취감을 느끼고 싶다',
                    '스트레스를 줄이고 싶다'
                ],
                'social_jobs': [
                    '효율적인 팀원으로 인식되고 싶다',
                    '최신 도구를 사용하는 트렌디한 사람이 되고 싶다'
                ]
            },
            'strategies': [
                {
                    'name': 'AI-First Simplicity',
                    'description': 'AI가 복잡한 작업을 자동화하여 사용자는 간단한 인터페이스만 사용',
                    'key_principles': [
                        'AI 추천 기반 업무 우선순위',
                        '자동 일정 최적화',
                        '스마트 알림 시스템'
                    ],
                    'target_emotion': 'confidence'
                }
            ]
        }
    
    def _execute_design_system(self) -> Dict[str, Any]:
        """3단계: 디자인 시스템 생성"""
        logger.info("🎨 Executing design system generation...")
        
        # Get UX analysis data from previous stage
        ux_stage = self.stage_results.get(WorkflowStage.UX_ANALYSIS)
        if not ux_stage or not ux_stage.result_data:
            raise Exception("UX analysis data not available")
        
        ux_analysis = ux_stage.result_data
        
        if self.agents['design_system_generator'] and hasattr(self.agents['design_system_generator'], 'generate_complete_design_system'):
            # Use real DesignSystemGenerator
            return self.agents['design_system_generator'].generate_complete_design_system(ux_analysis)
        else:
            # Mock design system
            logger.info("Using mock design system generation...")
            return self._mock_design_system(ux_analysis)
    
    def _mock_design_system(self, ux_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Mock 디자인 시스템 (테스트용)"""
        app_name = f"{ux_analysis['trend_keyword'].title().replace(' ', '')}Pro"
        
        return {
            'app_concept': {
                'name': app_name,
                'tagline': f'{ux_analysis["trend_keyword"]}를 위한 스마트 솔루션',
                'category': ux_analysis['category']
            },
            'brand_identity': {
                'color_palette': {
                    'colors': {
                        'primary': {
                            '50': '#f0f9ff',
                            '500': '#0ea5e9',
                            '900': '#0c4a6e'
                        },
                        'secondary': {'500': '#8b5cf6'}
                    }
                },
                'typography_system': {
                    'font_families': {
                        'display': 'Inter',
                        'body': 'Inter'
                    }
                }
            },
            'component_system': {
                'components': {
                    'button': {'variants': ['primary', 'secondary', 'ghost']},
                    'input': {'variants': ['default', 'error']},
                    'card': {'variants': ['default', 'elevated']},
                    'avatar': {'sizes': ['sm', 'md', 'lg']}
                }
            }
        }
    
    def _execute_prototype_build(self) -> Dict[str, Any]:
        """4단계: 프로토타입 빌드"""
        logger.info("🏗️ Executing prototype build...")
        
        # Get design system and UX analysis data
        design_stage = self.stage_results.get(WorkflowStage.DESIGN_SYSTEM)
        ux_stage = self.stage_results.get(WorkflowStage.UX_ANALYSIS)
        
        if not design_stage or not ux_stage:
            raise Exception("Design system or UX analysis data not available")
        
        design_system = design_stage.result_data
        ux_strategy = ux_stage.result_data
        app_name = design_system['app_concept']['name']
        
        if self.agents['prototype_builder'] and hasattr(self.agents['prototype_builder'], 'build_complete_prototype'):
            # Use real PrototypeBuilder
            return self.agents['prototype_builder'].build_complete_prototype(
                design_system, ux_strategy, app_name
            )
        else:
            # Mock prototype build
            logger.info("Using mock prototype build...")
            return self._mock_prototype_build(design_system, app_name)
    
    def _mock_prototype_build(self, design_system: Dict[str, Any], app_name: str) -> Dict[str, Any]:
        """Mock 프로토타입 빌드 (테스트용)"""
        project_name = app_name.lower().replace(' ', '-')
        project_path = Path(self.config.output_dir) / project_name
        
        # Create basic project structure
        project_path.mkdir(parents=True, exist_ok=True)
        (project_path / 'src').mkdir(exist_ok=True)
        (project_path / 'public').mkdir(exist_ok=True)
        
        # Create basic files
        with open(project_path / 'package.json', 'w') as f:
            json.dump({
                'name': project_name,
                'version': '0.1.0',
                'dependencies': {
                    'react': '^18.2.0',
                    'react-dom': '^18.2.0'
                }
            }, f, indent=2)
        
        return {
            'project_info': {
                'app_name': app_name,
                'project_path': str(project_path),
                'generated_at': datetime.now().isoformat()
            },
            'generated_files': {
                'components': ['Button.jsx', 'Input.jsx', 'Card.jsx'],
                'screens': ['MainScreen.jsx', 'ProfileScreen.jsx'],
                'config': ['package.json', 'tailwind.config.js']
            },
            'deployment': {
                'vercel': {'ready': True},
                'netlify': {'ready': True}
            },
            'urls': {
                'local_dev': 'http://localhost:3000'
            }
        }
    
    def _execute_deployment(self) -> Dict[str, Any]:
        """5단계: 배포 설정"""
        logger.info("🚀 Executing deployment setup...")
        
        prototype_stage = self.stage_results.get(WorkflowStage.PROTOTYPE_BUILD)
        if not prototype_stage or not prototype_stage.result_data:
            raise Exception("Prototype data not available")
        
        prototype_data = prototype_stage.result_data
        project_path = Path(prototype_data['project_info']['project_path'])
        
        # Create deployment configurations
        deployment_configs = []
        
        # Vercel config
        vercel_config = {
            'version': 2,
            'builds': [{'src': 'package.json', 'use': '@vercel/static-build'}],
            'routes': [{'src': '/(.*)', 'dest': '/index.html'}]
        }
        
        vercel_path = project_path / 'vercel.json'
        with open(vercel_path, 'w') as f:
            json.dump(vercel_config, f, indent=2)
        deployment_configs.append('vercel.json')
        
        # Netlify config
        netlify_config = '''[build]
  publish = "build"
  command = "npm run build"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200'''
        
        netlify_path = project_path / 'netlify.toml'
        with open(netlify_path, 'w') as f:
            f.write(netlify_config)
        deployment_configs.append('netlify.toml')
        
        return {
            'deployment_configs': deployment_configs,
            'platforms': {
                'vercel': {
                    'config_file': str(vercel_path),
                    'deploy_command': 'vercel --prod',
                    'ready': True
                },
                'netlify': {
                    'config_file': str(netlify_path),
                    'deploy_command': 'netlify deploy --prod',
                    'ready': True
                }
            },
            'instructions': [
                f'cd {project_path}',
                'npm install',
                'npm run build',
                'Deploy using vercel --prod or netlify deploy --prod'
            ]
        }
    
    def _execute_reporting(self) -> Dict[str, Any]:
        """6단계: 보고서 생성"""
        logger.info("📄 Executing reporting...")
        
        # Generate comprehensive report
        report = {
            'workflow_summary': {
                'workflow_id': self.workflow_id,
                'trend_keyword': self.config.trend_keyword,
                'start_time': self.workflow_start_time.isoformat(),
                'total_duration': (datetime.now() - self.workflow_start_time).total_seconds(),
                'status': 'completed'
            },
            'stage_details': {},
            'final_outputs': {}
        }
        
        # Add stage details
        for stage, result in self.stage_results.items():
            report['stage_details'][stage.value] = {
                'status': result.status.value,
                'duration': result.duration,
                'retry_count': result.retry_count,
                'error_message': result.error_message
            }
        
        # Add final outputs
        if WorkflowStage.PROTOTYPE_BUILD in self.stage_results:
            prototype_result = self.stage_results[WorkflowStage.PROTOTYPE_BUILD].result_data
            if prototype_result:
                report['final_outputs']['app_name'] = prototype_result['project_info']['app_name']
                report['final_outputs']['project_path'] = prototype_result['project_info']['project_path']
        
        return report
    
    def _generate_final_result(self) -> Dict[str, Any]:
        """최종 결과 생성"""
        total_duration = (self.workflow_end_time - self.workflow_start_time).total_seconds()
        
        # Count successful stages
        successful_stages = sum(1 for result in self.stage_results.values() 
                              if result.status == StageStatus.COMPLETED)
        total_stages = len(self.stage_results)
        
        # Determine overall status
        overall_status = "completed" if successful_stages == total_stages else "partial"
        if successful_stages == 0:
            overall_status = "failed"
        
        final_result = {
            'workflow_info': {
                'workflow_id': self.workflow_id,
                'trend_keyword': self.config.trend_keyword,
                'category': self.config.category,
                'status': overall_status,
                'start_time': self.workflow_start_time.isoformat(),
                'end_time': self.workflow_end_time.isoformat(),
                'total_duration': total_duration,
                'successful_stages': f"{successful_stages}/{total_stages}"
            },
            'stage_results': {
                stage.value: {
                    'status': result.status.value,
                    'duration': result.duration,
                    'retry_count': result.retry_count,
                    'error_message': result.error_message,
                    'result_summary': self._summarize_stage_result(stage, result)
                }
                for stage, result in self.stage_results.items()
            },
            'generated_outputs': self._collect_generated_outputs(),
            'next_steps': self._generate_next_steps(),
            'performance_metrics': {
                'total_time': f"{total_duration:.2f} seconds",
                'average_stage_time': f"{total_duration / total_stages:.2f} seconds",
                'success_rate': f"{(successful_stages / total_stages) * 100:.1f}%"
            }
        }
        
        return final_result
    
    def _generate_error_result(self, error_message: str) -> Dict[str, Any]:
        """에러 결과 생성"""
        return {
            'workflow_info': {
                'workflow_id': self.workflow_id,
                'status': 'failed',
                'error_message': error_message,
                'start_time': self.workflow_start_time.isoformat() if self.workflow_start_time else None,
                'end_time': self.workflow_end_time.isoformat() if self.workflow_end_time else None
            },
            'stage_results': {
                stage.value: {
                    'status': result.status.value,
                    'error_message': result.error_message
                }
                for stage, result in self.stage_results.items()
            }
        }
    
    def _summarize_stage_result(self, stage: WorkflowStage, result: StageResult) -> str:
        """단계 결과 요약"""
        if result.status != StageStatus.COMPLETED or not result.result_data:
            return "No data available"
        
        data = result.result_data
        
        if stage == WorkflowStage.TREND_COLLECTION:
            trend = data.get('selected_trend', {})
            return f"Selected trend: {trend.get('keyword', 'N/A')} (Score: {trend.get('score', 'N/A')})"
        
        elif stage == WorkflowStage.UX_ANALYSIS:
            personas_count = len(data.get('personas', []))
            strategies_count = len(data.get('strategies', []))
            return f"Generated {personas_count} personas and {strategies_count} strategies"
        
        elif stage == WorkflowStage.DESIGN_SYSTEM:
            app_name = data.get('app_concept', {}).get('name', 'N/A')
            components_count = len(data.get('component_system', {}).get('components', {}))
            return f"Created design system for {app_name} with {components_count} components"
        
        elif stage == WorkflowStage.PROTOTYPE_BUILD:
            app_name = data.get('project_info', {}).get('app_name', 'N/A')
            files_count = len(data.get('generated_files', {}).get('components', [])) + \
                         len(data.get('generated_files', {}).get('screens', [])) + \
                         len(data.get('generated_files', {}).get('config', []))
            return f"Built React prototype for {app_name} with {files_count} files"
        
        elif stage == WorkflowStage.DEPLOYMENT:
            platforms_count = len(data.get('platforms', {}))
            return f"Configured deployment for {platforms_count} platforms"
        
        elif stage == WorkflowStage.REPORTING:
            return f"Generated comprehensive workflow report"
        
        return "Completed successfully"
    
    def _collect_generated_outputs(self) -> Dict[str, Any]:
        """생성된 결과물 수집"""
        outputs = {}
        
        for stage, result in self.stage_results.items():
            if result.status == StageStatus.COMPLETED and result.result_data:
                outputs[stage.value] = result.result_data
        
        return outputs
    
    def _generate_next_steps(self) -> List[str]:
        """다음 단계 가이드 생성"""
        next_steps = []
        
        # Check if prototype was built
        if WorkflowStage.PROTOTYPE_BUILD in self.stage_results:
            prototype_result = self.stage_results[WorkflowStage.PROTOTYPE_BUILD].result_data
            if prototype_result and prototype_result.get('project_info'):
                project_path = prototype_result['project_info']['project_path']
                next_steps.extend([
                    f"1. Navigate to project: cd {project_path}",
                    "2. Install dependencies: npm install",
                    "3. Start development: npm start",
                    "4. Open http://localhost:3000",
                    "5. Deploy using vercel --prod or netlify deploy --prod"
                ])
        
        if not next_steps:
            next_steps = [
                "1. Review the generated outputs above",
                "2. Check stage results for any errors",
                "3. Re-run failed stages if needed",
                "4. Configure missing API keys if required"
            ]
        
        return next_steps
    
    def _save_to_supabase(self, result: Dict[str, Any]) -> bool:
        """Supabase에 결과 저장"""
        if not self.supabase_client:
            logger.warning("⚠️ Supabase client not available, skipping save")
            return False
        
        try:
            # Prepare data for Supabase
            workflow_data = {
                'workflow_id': self.workflow_id,
                'trend_keyword': self.config.trend_keyword,
                'category': self.config.category,
                'status': result['workflow_info']['status'],
                'total_duration': result['workflow_info']['total_duration'],
                'successful_stages': result['workflow_info']['successful_stages'],
                'result_data': json.dumps(result),
                'created_at': self.workflow_start_time.isoformat()
            }
            
            # Insert into workflows table
            response = self.supabase_client.table('ai_app_workflows').insert(workflow_data).execute()
            
            logger.info(f"✅ Results saved to Supabase: {response.data[0]['id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save to Supabase: {e}")
            return False
    
    def _generate_notion_report(self, result: Dict[str, Any]) -> bool:
        """Notion 보고서 생성"""
        if not self.notion_client:
            logger.warning("⚠️ Notion client not available, skipping report generation")
            return False
        
        try:
            import requests
            
            # Get database ID from environment
            database_id = os.getenv('NOTION_DATABASE_ID')
            if not database_id:
                logger.warning("⚠️ Notion database ID not found")
                return False
            
            # Prepare Notion page data
            notion_data = {
                "parent": {"database_id": database_id},
                "properties": {
                    "Title": {
                        "title": [
                            {
                                "text": {
                                    "content": f"AI App Factory: {self.config.trend_keyword}"
                                }
                            }
                        ]
                    },
                    "Status": {
                        "select": {
                            "name": result['workflow_info']['status'].title()
                        }
                    },
                    "Trend Keyword": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": self.config.trend_keyword
                                }
                            }
                        ]
                    },
                    "Duration": {
                        "number": result['workflow_info']['total_duration']
                    },
                    "Success Rate": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": result['performance_metrics']['success_rate']
                                }
                            }
                        ]
                    }
                },
                "children": self._create_notion_content(result)
            }
            
            # Create Notion page
            response = requests.post(
                'https://api.notion.com/v1/pages',
                headers=self.notion_client['headers'],
                json=notion_data
            )
            
            if response.status_code == 200:
                page_data = response.json()
                page_url = page_data.get('url', 'N/A')
                logger.info(f"✅ Notion report created: {page_url}")
                return True
            else:
                logger.error(f"❌ Failed to create Notion page: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to generate Notion report: {e}")
            return False
    
    def _create_notion_content(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Notion 페이지 컨텐츠 생성"""
        content = []
        
        # Workflow Summary
        content.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "🏭 Workflow Summary"}}]
            }
        })
        
        summary_text = f"""
**Workflow ID**: {result['workflow_info']['workflow_id']}
**Trend Keyword**: {self.config.trend_keyword}
**Status**: {result['workflow_info']['status'].title()}
**Duration**: {result['performance_metrics']['total_time']}
**Success Rate**: {result['performance_metrics']['success_rate']}
        """.strip()
        
        content.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": summary_text}}]
            }
        })
        
        # Stage Results
        content.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "📊 Stage Results"}}]
            }
        })
        
        for stage_name, stage_data in result['stage_results'].items():
            status_emoji = "✅" if stage_data['status'] == 'completed' else "❌"
            stage_text = f"{status_emoji} **{stage_name.replace('_', ' ').title()}**: {stage_data['status']} ({stage_data.get('duration', 0):.2f}s)"
            
            content.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": stage_text}}]
                }
            })
        
        # Next Steps
        if result.get('next_steps'):
            content.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "🚀 Next Steps"}}]
                }
            })
            
            for step in result['next_steps']:
                content.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": step}}]
                    }
                })
        
        return content
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """현재 워크플로우 상태 조회"""
        return {
            'workflow_id': self.workflow_id,
            'config': asdict(self.config),
            'start_time': self.workflow_start_time.isoformat() if self.workflow_start_time else None,
            'current_stage': self._get_current_stage(),
            'stage_results': {
                stage.value: {
                    'status': result.status.value,
                    'duration': result.duration,
                    'retry_count': result.retry_count
                }
                for stage, result in self.stage_results.items()
            }
        }
    
    def _get_current_stage(self) -> Optional[str]:
        """현재 실행 중인 단계 확인"""
        for stage, result in self.stage_results.items():
            if result.status in [StageStatus.IN_PROGRESS, StageStatus.RETRYING]:
                return stage.value
        return None

# Factory function for easy instantiation
def create_orchestrator(trend_keyword: str, **kwargs) -> AppFactoryOrchestrator:
    """AppFactoryOrchestrator 생성 헬퍼 함수"""
    config = WorkflowConfig(
        trend_keyword=trend_keyword,
        **kwargs
    )
    return AppFactoryOrchestrator(config)