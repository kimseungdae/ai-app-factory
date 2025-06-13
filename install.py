#!/usr/bin/env python3
"""
AI App Factory 설치 및 초기 설정 스크립트
원클릭으로 모든 설정을 완료할 수 있는 설치 프로그램
"""

import os
import sys
import subprocess
import urllib.request
import webbrowser
from pathlib import Path
from typing import List, Dict

class AIAppFactoryInstaller:
    """AI App Factory 설치 프로그램"""
    
    def __init__(self):
        self.project_dir = Path('.')
        self.requirements_file = self.project_dir / 'requirements.txt'
        self.env_file = self.project_dir / '.env'
        
    def run_installation(self):
        """전체 설치 프로세스 실행"""
        self.print_welcome()
        
        print("🚀 AI App Factory 설치를 시작합니다...")
        print("=" * 60)
        
        # 1. 시스템 요구사항 확인
        if not self.check_system_requirements():
            return False
        
        # 2. Python 패키지 설치
        if not self.install_dependencies():
            return False
        
        # 3. API 키 설정 안내
        self.guide_api_setup()
        
        # 4. 설정 완료 및 테스트
        self.final_setup()
        
        return True
    
    def print_welcome(self):
        """환영 메시지"""
        welcome = """
🏭 ══════════════════════════════════════════════════════════════
   █████╗ ██╗    ██████╗ ██████╗ ██████╗     ███████╗ █████╗  ██████╗████████╗ ██████╗ ██████╗ ██╗   ██╗
  ██╔══██╗██║   ██╔══██╗██╔══██╗██╔══██╗    ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝
  ███████║██║   ███████║██████╔╝██████╔╝    █████╗  ███████║██║        ██║   ██║   ██║██████╔╝ ╚████╔╝ 
  ██╔══██║██║   ██╔══██║██╔═══╝ ██╔═══╝     ██╔══╝  ██╔══██║██║        ██║   ██║   ██║██╔══██╗  ╚██╔╝  
  ██║  ██║██║   ██║  ██║██║     ██║         ██║     ██║  ██║╚██████╗   ██║   ╚██████╔╝██║  ██║   ██║   
  ╚═╝  ╚═╝╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝         ╚═╝     ╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
                                                                                                        
   🚀 Complete AI-Powered App Development Automation
   💡 30분 만에 아이디어에서 앱 프로토타입까지!
🏭 ══════════════════════════════════════════════════════════════

환영합니다! AI App Factory 설치 프로그램입니다.
이 프로그램은 필요한 모든 구성 요소를 자동으로 설치하고 설정합니다.
"""
        print(welcome)
        
        input("계속하려면 Enter를 누르세요...")
    
    def check_system_requirements(self) -> bool:
        """시스템 요구사항 확인"""
        print("\n🔍 1단계: 시스템 요구사항 확인")
        print("-" * 40)
        
        checks = []
        
        # Python 버전 확인
        python_version = sys.version_info
        if python_version >= (3, 8):
            print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} (요구사항: 3.8+)")
            checks.append(True)
        else:
            print(f"❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (요구사항: 3.8+)")
            print("   Python 3.8 이상이 필요합니다.")
            checks.append(False)
        
        # pip 확인
        try:
            subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                         check=True, capture_output=True)
            print("✅ pip 설치됨")
            checks.append(True)
        except subprocess.CalledProcessError:
            print("❌ pip이 설치되지 않음")
            checks.append(False)
        
        # git 확인 (선택사항)
        try:
            subprocess.run(['git', '--version'], 
                         check=True, capture_output=True)
            print("✅ Git 설치됨")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ Git 미설치 (선택사항)")
        
        # 인터넷 연결 확인
        try:
            urllib.request.urlopen('https://www.google.com', timeout=3)
            print("✅ 인터넷 연결 확인")
            checks.append(True)
        except:
            print("❌ 인터넷 연결 실패")
            checks.append(False)
        
        success = all(checks)
        if success:
            print("\n🎉 시스템 요구사항 확인 완료!")
        else:
            print("\n❌ 시스템 요구사항을 만족하지 않습니다.")
            print("위의 문제를 해결한 후 다시 실행해주세요.")
        
        return success
    
    def install_dependencies(self) -> bool:
        """Python 의존성 설치"""
        print("\n📦 2단계: Python 패키지 설치")
        print("-" * 40)
        
        if not self.requirements_file.exists():
            print("❌ requirements.txt 파일을 찾을 수 없습니다.")
            return False
        
        try:
            print("📥 패키지를 다운로드하고 설치 중...")
            print("   (네트워크 상황에 따라 몇 분 소요될 수 있습니다)")
            
            # 패키지 설치
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 
                str(self.requirements_file), '--upgrade'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 모든 패키지가 성공적으로 설치되었습니다!")
                
                # 설치된 패키지 목록 표시
                print("\n📋 설치된 주요 패키지:")
                packages = [
                    "openai", "praw", "pytrends", "beautifulsoup4", 
                    "python-unsplash", "supabase", "requests", "jinja2"
                ]
                
                for package in packages:
                    try:
                        subprocess.run([sys.executable, '-c', f'import {package.replace("-", "_")}'], 
                                     check=True, capture_output=True)
                        print(f"   ✅ {package}")
                    except subprocess.CalledProcessError:
                        print(f"   ⚠️ {package}")
                
                return True
            else:
                print("❌ 패키지 설치 중 오류가 발생했습니다:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ 설치 실패: {e}")
            return False
    
    def guide_api_setup(self):
        """API 키 설정 안내"""
        print("\n🔑 3단계: API 키 설정")
        print("-" * 40)
        
        print("이제 AI App Factory를 사용하기 위해 필요한 API 키를 설정해야 합니다.")
        print()
        
        # 필수 API 키 목록
        required_apis = [
            {
                "name": "OpenAI API Key",
                "description": "AI 기반 UX 분석용",
                "url": "https://platform.openai.com/api-keys",
                "cost": "사용량 기반 (소량 사용 시 월 $5-10)",
                "free": False
            },
            {
                "name": "Reddit API",
                "description": "트렌드 데이터 수집용",
                "url": "https://www.reddit.com/prefs/apps",
                "cost": "무료",
                "free": True
            }
        ]
        
        # 선택적 API 키 목록
        optional_apis = [
            {
                "name": "Unsplash API",
                "description": "고품질 이미지 수집",
                "url": "https://unsplash.com/developers",
                "cost": "무료 (월 50회 요청)",
                "free": True
            },
            {
                "name": "Supabase",
                "description": "결과 데이터 저장",
                "url": "https://supabase.com",
                "cost": "무료 플랜 사용 가능",
                "free": True
            },
            {
                "name": "Notion API",
                "description": "자동 보고서 생성",
                "url": "https://www.notion.so/my-integrations",
                "cost": "무료",
                "free": True
            }
        ]
        
        print("🔴 필수 API 키:")
        for api in required_apis:
            icon = "🆓" if api["free"] else "💰"
            print(f"   • {api['name']}: {api['description']}")
            print(f"     {icon} 비용: {api['cost']}")
            print(f"     🌐 발급: {api['url']}")
            print()
        
        print("🟡 선택적 API 키 (더 많은 기능):")
        for api in optional_apis:
            icon = "🆓" if api["free"] else "💰"
            print(f"   • {api['name']}: {api['description']}")
            print(f"     {icon} 비용: {api['cost']}")
            print()
        
        print("💡 권장사항:")
        print("   1. 먼저 필수 API 키만 설정하여 기본 기능을 테스트")
        print("   2. 필요에 따라 선택적 API 키를 추가 설정")
        print("   3. OpenAI API는 소량 사용 시 비용이 매우 저렴함 (월 $5-10)")
        print()
        
        choice = input("API 키 설정을 진행하시겠습니까? (y/n): ").lower().strip()
        
        if choice in ['y', 'yes', '예']:
            print("\n🚀 토큰 설정 프로그램을 실행합니다...")
            print("   다음 화면에서 API 키를 하나씩 입력하게 됩니다.")
            input("\n준비되면 Enter를 누르세요...")
            
            try:
                # 토큰 설정 프로그램 실행
                subprocess.run([sys.executable, 'setup_tokens.py'], check=True)
            except subprocess.CalledProcessError:
                print("❌ 토큰 설정 프로그램 실행 실패")
                print("수동으로 'python setup_tokens.py' 명령어를 실행해주세요.")
            except FileNotFoundError:
                print("❌ setup_tokens.py 파일을 찾을 수 없습니다.")
        else:
            print("\n⏭️ API 키 설정을 나중에 진행할 수 있습니다.")
            print("   설정 방법:")
            print("   • 자동 설정: python setup_tokens.py")
            print("   • 간단 설정: python token_manager.py")
            print("   • 수동 설정: .env 파일 편집")
    
    def final_setup(self):
        """최종 설정 및 테스트"""
        print("\n🎯 4단계: 설치 완료 및 테스트")
        print("-" * 40)
        
        # 환경 검증
        print("🔍 설치 상태 검증 중...")
        
        try:
            result = subprocess.run([
                sys.executable, 'main.py', '--validate-env'
            ], capture_output=True, text=True, timeout=30)
            
            if "Environment validation failed" in result.stdout:
                print("⚠️ 일부 API 키가 설정되지 않았습니다.")
                print("기본 기능은 Mock 데이터로 테스트할 수 있습니다.")
            else:
                print("✅ 환경 설정 검증 완료!")
                
        except subprocess.TimeoutExpired:
            print("⏰ 검증 시간 초과")
        except Exception as e:
            print(f"⚠️ 검증 중 오류: {e}")
        
        # 테스트 실행 제안
        print("\n🧪 설치 테스트:")
        test_choice = input("드라이런 테스트를 실행하시겠습니까? (y/n): ").lower().strip()
        
        if test_choice in ['y', 'yes', '예']:
            print("\n🚀 드라이런 테스트 실행 중...")
            try:
                subprocess.run([
                    sys.executable, 'main.py', 
                    '--trend', 'AI fitness', '--dry-run'
                ], check=True, timeout=60)
                print("✅ 드라이런 테스트 성공!")
            except subprocess.CalledProcessError as e:
                print(f"❌ 테스트 실패: {e}")
            except subprocess.TimeoutExpired:
                print("⏰ 테스트 시간 초과")
        
        # 설치 완료 메시지
        self.print_completion()
    
    def print_completion(self):
        """설치 완료 메시지"""
        completion = """
🎉 ══════════════════════════════════════════════════════════════
   ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗     ███████╗████████╗███████╗██████╗ ██╗
  ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██║     ██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║
  ██║     ██║   ██║██╔████╔██║██████╔╝██║     █████╗     ██║   █████╗  ██║  ██║██║
  ██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝     ██║   ██╔══╝  ██║  ██║╚═╝
  ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ███████╗███████╗   ██║   ███████╗██████╔╝██╗
   ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝   ╚═╝   ╚══════╝╚═════╝ ╚═╝
                                                                                  
   🎉 AI App Factory 설치가 완료되었습니다!
🎉 ══════════════════════════════════════════════════════════════

🚀 이제 AI App Factory를 사용할 준비가 되었습니다!

📋 다음 단계:
   1. API 키 설정 (아직 안 했다면):
      python setup_tokens.py

   2. 환경 확인:
      python main.py --validate-env

   3. 첫 번째 앱 생성:
      python main.py --trend "AI fitness" --output-dir "./my_apps"

💡 유용한 명령어:
   • 도움말: python main.py --help
   • 토큰 관리: python token_manager.py
   • 드라이런 테스트: python main.py --trend "test" --dry-run
   • 워크플로우 목록: python main.py --list-workflows

📚 문서:
   • 전체 가이드: README.md
   • 오케스트레이터 가이드: ORCHESTRATOR_GUIDE.md
   • 완료 요약: COMPLETION_SUMMARY.md

🎯 목표:
   30분 만에 아이디어에서 배포 가능한 앱 프로토타입까지!

Happy coding! 🏭✨
"""
        print(completion)

def main():
    """메인 함수"""
    try:
        installer = AIAppFactoryInstaller()
        
        if installer.run_installation():
            print("\n✅ 설치가 성공적으로 완료되었습니다!")
        else:
            print("\n❌ 설치 중 문제가 발생했습니다.")
            print("문제를 해결한 후 다시 시도해주세요.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 설치가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()