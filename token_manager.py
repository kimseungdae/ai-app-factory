#!/usr/bin/env python3
"""
Token Manager - 간단한 토큰 관리 프로그램
빠르고 쉽게 API 토큰을 관리할 수 있는 유틸리티
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List
from getpass import getpass

class SimpleTokenManager:
    """간단한 토큰 관리자"""
    
    def __init__(self):
        self.env_file = Path('.env')
        self.config_file = Path('token_config.json')
        
        # 토큰 정보 (간단 버전)
        self.tokens = {
            # 필수 토큰
            "OPENAI_API_KEY": {
                "name": "OpenAI API Key",
                "required": True,
                "description": "AI 분석용 OpenAI API 키",
                "example": "sk-...",
                "url": "https://platform.openai.com/api-keys"
            },
            "REDDIT_CLIENT_ID": {
                "name": "Reddit Client ID",
                "required": True,
                "description": "Reddit 앱 클라이언트 ID",
                "example": "abcd1234",
                "url": "https://www.reddit.com/prefs/apps"
            },
            "REDDIT_CLIENT_SECRET": {
                "name": "Reddit Client Secret",
                "required": True,
                "description": "Reddit 앱 시크릿",
                "example": "xyz789...",
                "url": "https://www.reddit.com/prefs/apps"
            },
            "REDDIT_REFRESH_TOKEN": {
                "name": "Reddit Refresh Token",
                "required": True,
                "description": "OAuth 인증을 위한 리프레시 토큰",
                "example": "your_refresh_token",
                "url": "https://www.reddit.com/prefs/apps"
            },
            
            # 선택적 토큰
            "UNSPLASH_ACCESS_KEY": {
                "name": "Unsplash API Key",
                "required": False,
                "description": "이미지 수집용 (선택사항)",
                "example": "abc123...",
                "url": "https://unsplash.com/developers"
            },
            "SUPABASE_URL": {
                "name": "Supabase URL",
                "required": False,
                "description": "데이터 저장용 (선택사항)",
                "example": "https://xxx.supabase.co",
                "url": "https://supabase.com",
                "sensitive": False
            },
            "SUPABASE_KEY": {
                "name": "Supabase Key",
                "required": False,
                "description": "Supabase API 키 (선택사항)",
                "example": "eyJ...",
                "url": "https://supabase.com"
            },
            "NOTION_TOKEN": {
                "name": "Notion Token",
                "required": False,
                "description": "보고서 생성용 (선택사항)",
                "example": "secret_...",
                "url": "https://www.notion.so/my-integrations"
            },
            "NOTION_DATABASE_ID": {
                "name": "Notion Database ID",
                "required": False,
                "description": "Notion 데이터베이스 ID (선택사항)",
                "example": "32자리 ID",
                "url": "https://www.notion.so",
                "sensitive": False
            }
        }
    
    def run(self):
        """메인 실행"""
        self.print_header()
        
        while True:
            self.show_menu()
            choice = input("\n선택 (1-6): ").strip()
            
            if choice == "1":
                self.quick_setup()
            elif choice == "2":
                self.manual_setup()
            elif choice == "3":
                self.view_status()
            elif choice == "4":
                self.test_tokens()
            elif choice == "5":
                self.reset_config()
            elif choice == "6":
                print("👋 프로그램을 종료합니다.")
                break
            else:
                print("❌ 1-6 중에서 선택해주세요.")
            
            input("\n계속하려면 Enter를 누르세요...")
    
    def print_header(self):
        """헤더 출력"""
        print("🔑" + "="*60 + "🔑")
        print("   🚀 AI App Factory - 간단 토큰 관리자")
        print("   💡 API 키를 쉽고 빠르게 설정하세요")
        print("🔑" + "="*60 + "🔑")
        print()
    
    def show_menu(self):
        """메뉴 표시"""
        print("\n📋 메뉴:")
        print("1. 🚀 빠른 설정 (필수 토큰만)")
        print("2. ⚙️  수동 설정 (개별 선택)")
        print("3. 👀 현재 상태 확인")
        print("4. 🧪 토큰 테스트")
        print("5. 🗑️  설정 초기화")
        print("6. 🚪 종료")
    
    def quick_setup(self):
        """빠른 설정"""
        print("\n🚀 빠른 설정 - 필수 토큰만 입력")
        print("="*50)
        
        required_tokens = {k: v for k, v in self.tokens.items() if v["required"]}
        
        print(f"📝 {len(required_tokens)}개의 필수 토큰을 설정합니다:")
        for token_key, token_info in required_tokens.items():
            print(f"   • {token_info['name']}")
        
        print(f"\n💡 각 토큰의 발급 방법:")
        for token_key, token_info in required_tokens.items():
            print(f"   • {token_info['name']}: {token_info['url']}")
        
        print()
        confirm = input("설정을 시작하시겠습니까? (y/n): ").lower().strip()
        
        if confirm not in ['y', 'yes', '예']:
            print("설정을 취소했습니다.")
            return
        
        values = {}
        for token_key, token_info in required_tokens.items():
            value = self.input_token(token_key, token_info)
            if value:
                values[token_key] = value
        
        if values:
            self.save_to_env(values)
            print(f"\n✅ {len(values)}개 토큰이 설정되었습니다!")
        else:
            print("\n❌ 설정된 토큰이 없습니다.")
    
    def manual_setup(self):
        """수동 설정"""
        print("\n⚙️ 수동 설정 - 원하는 토큰 선택")
        print("="*50)
        
        # 토큰 목록 표시
        print("\n📋 사용 가능한 토큰:")
        current_values = self.load_current_values()
        
        for i, (token_key, token_info) in enumerate(self.tokens.items(), 1):
            status = "✅" if current_values.get(token_key) else "❌"
            required = "🔴필수" if token_info["required"] else "🟡선택"
            print(f"   {i:2d}. {status} {required} {token_info['name']}")
        
        print(f"\n💡 설정할 토큰 번호를 입력하세요:")
        print(f"   예: 1,3,5 (여러 개) 또는 1-5 (범위) 또는 all (전체)")
        
        selection = input("\n선택: ").strip()
        
        if selection.lower() == 'all':
            selected_tokens = list(self.tokens.items())
        else:
            try:
                indices = self.parse_selection(selection, len(self.tokens))
                selected_tokens = [(list(self.tokens.items())[i-1]) for i in indices]
            except Exception as e:
                print(f"❌ 잘못된 입력: {e}")
                return
        
        # 선택된 토큰 설정
        values = {}
        for token_key, token_info in selected_tokens:
            print(f"\n" + "-"*40)
            value = self.input_token(token_key, token_info)
            if value:
                values[token_key] = value
        
        if values:
            self.save_to_env(values)
            print(f"\n✅ {len(values)}개 토큰이 설정되었습니다!")
        else:
            print("\n❌ 설정된 토큰이 없습니다.")
    
    def input_token(self, token_key: str, token_info: Dict) -> str:
        """개별 토큰 입력"""
        print(f"\n🔐 {token_info['name']} 설정")
        print(f"설명: {token_info['description']}")
        print(f"발급: {token_info['url']}")
        print(f"예시: {token_info['example']}")
        
        # 현재 값 확인
        current_values = self.load_current_values()
        current_value = current_values.get(token_key, "")
        
        if current_value:
            is_sensitive = token_info.get("sensitive", True)
            masked = self.mask_value(current_value, is_sensitive)
            print(f"현재: {masked}")
            
            keep = input("현재 값을 유지하시겠습니까? (y/n): ").lower().strip()
            if keep in ['y', 'yes', '예']:
                return current_value
        
        try:
            is_sensitive = token_info.get("sensitive", True)
            if is_sensitive:
                value = getpass("토큰 입력 (숨김): ")
            else:
                value = input("값 입력: ")
            
            value = value.strip()
            
            if not value:
                if token_info["required"]:
                    print("❌ 필수 토큰은 비워둘 수 없습니다.")
                    return self.input_token(token_key, token_info)
                else:
                    print("⏭️ 건너뜁니다.")
                    return ""
            
            return value
            
        except KeyboardInterrupt:
            print("\n설정을 취소했습니다.")
            return ""
    
    def parse_selection(self, selection: str, max_num: int) -> List[int]:
        """선택 문자열 파싱"""
        indices = []
        
        for part in selection.split(','):
            part = part.strip()
            
            if '-' in part:
                start, end = part.split('-', 1)
                start, end = int(start.strip()), int(end.strip())
                indices.extend(range(start, end + 1))
            else:
                indices.append(int(part))
        
        # 범위 검증
        for idx in indices:
            if idx < 1 or idx > max_num:
                raise ValueError(f"번호 {idx}는 1-{max_num} 범위를 벗어남")
        
        return sorted(list(set(indices)))
    
    def view_status(self):
        """현재 상태 확인"""
        print("\n👀 현재 토큰 설정 상태")
        print("="*50)
        
        current_values = self.load_current_values()
        
        # 필수 토큰
        print("\n🔴 필수 토큰:")
        required_set = 0
        for token_key, token_info in self.tokens.items():
            if token_info["required"]:
                if current_values.get(token_key):
                    is_sensitive = token_info.get("sensitive", True)
                    masked = self.mask_value(current_values[token_key], is_sensitive)
                    print(f"   ✅ {token_info['name']}: {masked}")
                    required_set += 1
                else:
                    print(f"   ❌ {token_info['name']}: 미설정")
        
        # 선택적 토큰
        print("\n🟡 선택적 토큰:")
        optional_set = 0
        for token_key, token_info in self.tokens.items():
            if not token_info["required"]:
                if current_values.get(token_key):
                    is_sensitive = token_info.get("sensitive", True)
                    masked = self.mask_value(current_values[token_key], is_sensitive)
                    print(f"   ✅ {token_info['name']}: {masked}")
                    optional_set += 1
                else:
                    print(f"   ❌ {token_info['name']}: 미설정")
        
        # 통계
        required_total = len([t for t in self.tokens.values() if t["required"]])
        optional_total = len([t for t in self.tokens.values() if not t["required"]])
        
        print(f"\n📊 설정 통계:")
        print(f"   필수: {required_set}/{required_total} ({required_set/required_total*100:.0f}%)")
        print(f"   선택: {optional_set}/{optional_total} ({optional_set/optional_total*100:.0f}%)")
        
        if required_set == required_total:
            print(f"\n🎉 기본 기능 사용 준비 완료!")
        else:
            print(f"\n⚠️ 필수 토큰 {required_total - required_set}개가 미설정되었습니다.")
    
    def test_tokens(self):
        """토큰 테스트"""
        print("\n🧪 토큰 유효성 테스트")
        print("="*50)
        
        current_values = self.load_current_values()
        
        if not current_values:
            print("❌ 설정된 토큰이 없습니다.")
            return
        
        print("🔍 간단한 형식 검증을 실행합니다...")
        
        test_results = {}
        
        for token_key, value in current_values.items():
            if not value:
                continue
                
            token_info = self.tokens.get(token_key, {})
            print(f"\n🔍 {token_info.get('name', token_key)} 검증 중...")
            
            # 간단한 형식 검증
            is_valid = self.validate_token_format(token_key, value)
            
            if is_valid:
                print(f"   ✅ 형식이 올바릅니다")
                test_results[token_key] = "✅ 통과"
            else:
                print(f"   ⚠️ 형식이 의심스럽습니다")
                test_results[token_key] = "⚠️ 의심"
        
        print(f"\n📋 테스트 결과:")
        for token_key, result in test_results.items():
            token_name = self.tokens.get(token_key, {}).get('name', token_key)
            print(f"   {result} {token_name}")
        
        print(f"\n💡 실제 API 연결 테스트는 main.py --validate-env 명령어를 사용하세요.")
    
    def validate_token_format(self, token_key: str, value: str) -> bool:
        """토큰 형식 검증"""
        if not value or value.startswith("your_"):
            return False
        
        validations = {
            "OPENAI_API_KEY": lambda v: v.startswith("sk-") and len(v) > 20,
            "REDDIT_CLIENT_ID": lambda v: len(v) > 10,
            "REDDIT_CLIENT_SECRET": lambda v: len(v) > 10,
            "REDDIT_REFRESH_TOKEN": lambda v: len(v) > 20,
            "UNSPLASH_ACCESS_KEY": lambda v: len(v) > 20,
            "SUPABASE_URL": lambda v: v.startswith("https://") and "supabase" in v,
            "SUPABASE_KEY": lambda v: len(v) > 50,
            "NOTION_TOKEN": lambda v: v.startswith("secret_"),
            "NOTION_DATABASE_ID": lambda v: len(v) == 32,
        }
        
        validator = validations.get(token_key)
        return validator(value) if validator else True
    
    def reset_config(self):
        """설정 초기화"""
        print("\n🗑️ 설정 초기화")
        print("="*40)
        
        print("⚠️ 이 작업은 모든 토큰 설정을 삭제합니다.")
        confirm = input("정말로 초기화하시겠습니까? (yes 입력): ").strip()
        
        if confirm.lower() != "yes":
            print("초기화를 취소했습니다.")
            return
        
        try:
            if self.env_file.exists():
                backup_file = Path(f".env.backup.{int(time.time())}")
                self.env_file.rename(backup_file)
                print(f"💾 기존 설정을 {backup_file}에 백업했습니다.")
            
            if self.config_file.exists():
                self.config_file.unlink()
            
            print("✅ 설정이 초기화되었습니다.")
            
        except Exception as e:
            print(f"❌ 초기화 실패: {e}")
    
    def load_current_values(self) -> Dict[str, str]:
        """현재 값 로드"""
        values = {}
        
        # .env 파일에서 로드
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            values[key] = value
            except Exception:
                pass
        
        # 환경 변수에서 로드
        for token_key in self.tokens.keys():
            env_value = os.getenv(token_key)
            if env_value:
                values[token_key] = env_value
        
        return values
    
    def save_to_env(self, new_values: Dict[str, str]):
        """환경 변수 파일 저장"""
        try:
            # 기존 값 로드
            current_values = self.load_current_values()
            
            # 새 값 병합
            current_values.update(new_values)
            
            # 백업
            if self.env_file.exists():
                import time
                backup_file = Path(f".env.backup.{int(time.time())}")
                self.env_file.rename(backup_file)
                print(f"💾 기존 설정을 {backup_file}에 백업했습니다.")
            
            # 새 파일 작성
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write("# AI App Factory 설정\n")
                f.write(f"# 생성일: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # 필수 토큰
                f.write("# 필수 토큰\n")
                for token_key, token_info in self.tokens.items():
                    if token_info["required"]:
                        value = current_values.get(token_key, "")
                        f.write(f"{token_key}={value}\n")
                
                f.write("\n# 선택적 토큰\n")
                for token_key, token_info in self.tokens.items():
                    if not token_info["required"]:
                        value = current_values.get(token_key, "")
                        f.write(f"{token_key}={value}\n")
                
                f.write("\n# 추가 설정\n")
                f.write("DEBUG=false\n")
                f.write("LOG_LEVEL=INFO\n")
            
            print(f"💾 설정이 {self.env_file}에 저장되었습니다.")
            
        except Exception as e:
            print(f"❌ 저장 실패: {e}")
    
    def mask_value(self, value: str, is_sensitive: bool) -> str:
        """값 마스킹"""
        if not is_sensitive:
            return value
        
        if len(value) <= 8:
            return "*" * len(value)
        else:
            return value[:4] + "*" * (len(value) - 8) + value[-4:]

def main():
    """메인 함수"""
    try:
        manager = SimpleTokenManager()
        manager.run()
    except KeyboardInterrupt:
        print("\n\n👋 프로그램을 종료합니다.")
    except Exception as e:
        print(f"\n❌ 오류: {e}")

if __name__ == "__main__":
    main()