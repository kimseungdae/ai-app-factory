#!/usr/bin/env python3
"""
AI App Factory Token Setup Wizard
API 키와 토큰을 쉽게 설정할 수 있는 대화형 설정 프로그램
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from getpass import getpass

@dataclass
class TokenInfo:
    """토큰 정보 클래스"""
    name: str
    env_var: str
    description: str
    required: bool
    get_url: str
    instructions: List[str]
    test_command: Optional[str] = None
    is_sensitive: bool = True

class TokenSetupWizard:
    """토큰 설정 마법사"""
    
    def __init__(self):
        self.tokens = self._define_tokens()
        self.env_file = Path('.env')
        self.current_values = self._load_current_values()
        
    def _define_tokens(self) -> List[TokenInfo]:
        """모든 토큰 정보 정의"""
        return [
            TokenInfo(
                name="OpenAI API Key",
                env_var="OPENAI_API_KEY",
                description="AI 기반 UX 분석 및 텍스트 생성을 위한 OpenAI API 키",
                required=True,
                get_url="https://platform.openai.com/api-keys",
                instructions=[
                    "1. https://platform.openai.com 접속",
                    "2. 로그인 후 'API Keys' 메뉴 클릭",
                    "3. 'Create new secret key' 버튼 클릭",
                    "4. 키 이름 입력 후 생성",
                    "5. 생성된 키를 복사 (sk-로 시작)"
                ],
                test_command="API 연결 테스트 가능"
            ),
            TokenInfo(
                name="Reddit Client ID",
                env_var="REDDIT_CLIENT_ID",
                description="Reddit 트렌드 데이터 수집을 위한 앱 클라이언트 ID",
                required=True,
                get_url="https://www.reddit.com/prefs/apps",
                instructions=[
                    "1. https://www.reddit.com/prefs/apps 접속",
                    "2. Reddit 계정으로 로그인",
                    "3. 'Create App' 또는 'Create Another App' 클릭",
                    "4. 앱 정보 입력:",
                    "   - name: AI App Factory",
                    "   - App type: script 선택",
                    "   - redirect uri: http://localhost:8080",
                    "5. 생성 후 앱 ID 복사 (앱 이름 아래 문자열)"
                ],
                is_sensitive=False
            ),
            TokenInfo(
                name="Reddit Client Secret",
                env_var="REDDIT_CLIENT_SECRET",
                description="Reddit API 인증을 위한 클라이언트 시크릿",
                required=True,
                get_url="https://www.reddit.com/prefs/apps",
                instructions=[
                    "1. Reddit 앱 설정 페이지에서",
                    "2. 생성한 앱의 'secret' 값 복사",
                    "3. 'edit' 링크를 클릭하면 secret 확인 가능"
                ]
            ),
            TokenInfo(
                name="Reddit Username",
                env_var="REDDIT_USERNAME",
                description="Reddit 계정 사용자명",
                required=True,
                get_url="https://www.reddit.com",
                instructions=[
                    "1. Reddit 계정의 사용자명 입력",
                    "2. /u/ 없이 사용자명만 입력",
                    "3. 예: your_username"
                ],
                is_sensitive=False
            ),
            TokenInfo(
                name="Reddit Password",
                env_var="REDDIT_PASSWORD",
                description="Reddit 계정 비밀번호",
                required=True,
                get_url="https://www.reddit.com",
                instructions=[
                    "1. Reddit 계정의 비밀번호 입력",
                    "2. 2FA 사용 시 앱 전용 비밀번호 생성 필요"
                ]
            ),
            TokenInfo(
                name="Unsplash Access Key",
                env_var="UNSPLASH_ACCESS_KEY",
                description="트렌드별 고품질 이미지 수집 (선택사항)",
                required=False,
                get_url="https://unsplash.com/developers",
                instructions=[
                    "1. https://unsplash.com/developers 접속",
                    "2. 'Your apps' 클릭",
                    "3. 'New Application' 클릭",
                    "4. 약관 동의 후 앱 정보 입력",
                    "5. 'Access Key' 복사"
                ],
                is_sensitive=False
            ),
            TokenInfo(
                name="Supabase URL",
                env_var="SUPABASE_URL",
                description="워크플로우 결과 저장을 위한 Supabase URL (선택사항)",
                required=False,
                get_url="https://supabase.com",
                instructions=[
                    "1. https://supabase.com 접속 후 회원가입",
                    "2. 'New Project' 클릭",
                    "3. 프로젝트 생성 후 'Settings' > 'API'",
                    "4. 'Project URL' 복사"
                ],
                is_sensitive=False
            ),
            TokenInfo(
                name="Supabase API Key",
                env_var="SUPABASE_KEY",
                description="Supabase 데이터베이스 접근 키 (선택사항)",
                required=False,
                get_url="https://supabase.com",
                instructions=[
                    "1. Supabase 프로젝트 설정에서",
                    "2. 'API' 탭의 'anon public' 키 복사",
                    "3. 또는 'service_role' 키 사용 가능"
                ]
            ),
            TokenInfo(
                name="Notion Integration Token",
                env_var="NOTION_TOKEN",
                description="자동 보고서 생성을 위한 Notion API 토큰 (선택사항)",
                required=False,
                get_url="https://www.notion.so/my-integrations",
                instructions=[
                    "1. https://www.notion.so/my-integrations 접속",
                    "2. 'New integration' 클릭",
                    "3. 통합 이름 입력 (예: AI App Factory)",
                    "4. 생성 후 'Internal Integration Token' 복사",
                    "5. secret_로 시작하는 토큰"
                ]
            ),
            TokenInfo(
                name="Notion Database ID",
                env_var="NOTION_DATABASE_ID",
                description="보고서가 저장될 Notion 데이터베이스 ID (선택사항)",
                required=False,
                get_url="https://www.notion.so",
                instructions=[
                    "1. Notion에서 새 데이터베이스 페이지 생성",
                    "2. 페이지 URL에서 32자리 ID 복사",
                    "3. 예: https://notion.so/database-id-here",
                    "4. 생성한 통합을 데이터베이스에 연결",
                    "5. 데이터베이스 '...' > 'Connections' > 통합 추가"
                ],
                is_sensitive=False
            ),
            TokenInfo(
                name="Figma Access Token",
                env_var="FIGMA_ACCESS_TOKEN",
                description="디자인 시스템 연동을 위한 Figma API 토큰 (선택사항)",
                required=False,
                get_url="https://www.figma.com/developers/api#access-tokens",
                instructions=[
                    "1. Figma 계정 설정 페이지 접속",
                    "2. 'Personal access tokens' 섹션",
                    "3. 'Create new token' 클릭",
                    "4. 토큰 이름 입력 후 생성",
                    "5. 생성된 토큰 복사 (figd_로 시작)"
                ]
            ),
            TokenInfo(
                name="Vercel Token",
                env_var="VERCEL_TOKEN",
                description="자동 배포를 위한 Vercel API 토큰 (선택사항)",
                required=False,
                get_url="https://vercel.com/account/tokens",
                instructions=[
                    "1. https://vercel.com/account/tokens 접속",
                    "2. 'Create Token' 클릭",
                    "3. 토큰 이름 입력 (예: AI App Factory)",
                    "4. 만료 기간 설정",
                    "5. 생성된 토큰 복사"
                ]
            )
        ]
    
    def _load_current_values(self) -> Dict[str, str]:
        """현재 설정된 값들 로드"""
        current_values = {}
        
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            current_values[key] = value
            except Exception as e:
                print(f"⚠️ .env 파일 읽기 오류: {e}")
        
        # 환경 변수에서도 확인
        for token in self.tokens:
            env_value = os.getenv(token.env_var)
            if env_value:
                current_values[token.env_var] = env_value
        
        return current_values
    
    def run_setup_wizard(self):
        """설정 마법사 실행"""
        self._print_banner()
        
        print("🔧 AI App Factory API 키 설정 마법사에 오신 것을 환영합니다!")
        print("=" * 70)
        print()
        
        print("📋 설정할 API 키 목록:")
        print()
        
        # 필수 토큰 목록
        print("🔴 필수 토큰 (기본 기능):")
        for i, token in enumerate([t for t in self.tokens if t.required], 1):
            status = "✅ 설정됨" if token.env_var in self.current_values else "❌ 미설정"
            print(f"   {i}. {token.name} - {status}")
        
        print()
        
        # 선택적 토큰 목록
        print("🟡 선택적 토큰 (고급 기능):")
        for i, token in enumerate([t for t in self.tokens if not t.required], 1):
            status = "✅ 설정됨" if token.env_var in self.current_values else "❌ 미설정"
            print(f"   {i}. {token.name} - {status}")
        
        print()
        print("💡 필수 토큰만 설정해도 기본 기능은 모두 사용 가능합니다.")
        print("💡 선택적 토큰을 추가하면 더 많은 기능을 이용할 수 있습니다.")
        print()
        
        while True:
            choice = input("🚀 설정을 시작하시겠습니까? (y/n): ").lower().strip()
            if choice in ['y', 'yes', '예', 'ㅇ']:
                break
            elif choice in ['n', 'no', '아니오', 'ㄴ']:
                print("👋 설정을 취소했습니다.")
                return False
        
        print()
        return self._interactive_setup()
    
    def _print_banner(self):
        """배너 출력"""
        banner = """
🔑 ════════════════════════════════════════════════════════
   ╔═══╗╔═══╗╔═══╗   ╔═══╗╔═══╗╔═══╗   ╔═══╗╔═══╗╔═══╗╔═══╗╔═══╗╔═══╗╔═══╗
   ║╔═╗║║╔═╗║║╔═╗║   ║╔═╗║║╔═╗║║╔═╗║   ║╔══╝║╔═╗║║╔═╗║║╔══╝║╔═╗║║╔═╗║║╔═╗║
   ║║ ║║║╚═╝║║╚═╝║   ║║ ║║║╚═╝║║╚═╝║   ║╚══╗║║ ║║║║ ║║║╚══╗║║ ║║║╚═╝║║╚═╝║
   ║╚═╝║║╔══╝║╔══╝   ║╚═╝║║╔══╝║╔══╝   ║╔══╝║╚═╝║║╚═╝║║╔══╝║╚═╝║║╔╗╔╝║╔╗╔╝
   ╚═══╝╚╝   ╚╝       ╚═══╝╚╝   ╚╝       ╚╝   ╚═══╝╚═══╝╚╝   ╚═══╝╚╝╚╝ ╚╝╚╝
                                                                                
   🔐 API Key & Token Configuration Wizard
   🚀 Complete Setup for AI App Factory
🔑 ════════════════════════════════════════════════════════
"""
        print(banner)
    
    def _interactive_setup(self) -> bool:
        """대화형 설정"""
        setup_choice = self._ask_setup_mode()
        
        if setup_choice == "1":
            return self._setup_required_only()
        elif setup_choice == "2":
            return self._setup_all_tokens()
        elif setup_choice == "3":
            return self._setup_selective()
        elif setup_choice == "4":
            return self._view_current_config()
        else:
            print("❌ 잘못된 선택입니다.")
            return False
    
    def _ask_setup_mode(self) -> str:
        """설정 모드 선택"""
        print("📋 설정 모드를 선택해주세요:")
        print()
        print("1. 🔴 필수 토큰만 설정 (빠른 시작)")
        print("2. 🟢 모든 토큰 설정 (전체 기능)")
        print("3. 🟡 선택적 토큰 설정 (커스텀)")
        print("4. 👀 현재 설정 상태 확인")
        print()
        
        while True:
            choice = input("선택 (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                return choice
            print("❌ 1-4 중에서 선택해주세요.")
    
    def _setup_required_only(self) -> bool:
        """필수 토큰만 설정"""
        print("\n🔴 필수 토큰 설정을 시작합니다...")
        print("=" * 50)
        
        required_tokens = [t for t in self.tokens if t.required]
        return self._setup_token_group(required_tokens, "필수")
    
    def _setup_all_tokens(self) -> bool:
        """모든 토큰 설정"""
        print("\n🟢 모든 토큰 설정을 시작합니다...")
        print("=" * 50)
        
        return self._setup_token_group(self.tokens, "전체")
    
    def _setup_selective(self) -> bool:
        """선택적 토큰 설정"""
        print("\n🟡 설정할 토큰을 선택해주세요...")
        print("=" * 50)
        print()
        
        # 토큰 선택
        selected_tokens = []
        
        print("📋 사용 가능한 토큰:")
        for i, token in enumerate(self.tokens, 1):
            status = "✅" if token.env_var in self.current_values else "❌"
            required_text = "(필수)" if token.required else "(선택)"
            print(f"   {i:2d}. {status} {token.name} {required_text}")
        
        print()
        print("💡 설정할 토큰 번호를 입력하세요 (예: 1,3,5 또는 1-5)")
        print("💡 'all'을 입력하면 모든 토큰을 설정합니다")
        
        while True:
            selection = input("\n선택: ").strip()
            
            if selection.lower() == 'all':
                selected_tokens = self.tokens
                break
            
            try:
                indices = self._parse_selection(selection, len(self.tokens))
                selected_tokens = [self.tokens[i-1] for i in indices]
                break
            except ValueError as e:
                print(f"❌ {e}")
        
        if not selected_tokens:
            print("❌ 선택된 토큰이 없습니다.")
            return False
        
        print(f"\n✅ {len(selected_tokens)}개 토큰 설정을 시작합니다...")
        return self._setup_token_group(selected_tokens, "선택")
    
    def _parse_selection(self, selection: str, max_num: int) -> List[int]:
        """선택 문자열 파싱"""
        indices = []
        
        for part in selection.split(','):
            part = part.strip()
            
            if '-' in part:
                # 범위 (예: 1-5)
                start, end = part.split('-', 1)
                start, end = int(start.strip()), int(end.strip())
                
                if start < 1 or end > max_num or start > end:
                    raise ValueError(f"잘못된 범위: {part} (1-{max_num} 사이여야 함)")
                
                indices.extend(range(start, end + 1))
            else:
                # 단일 번호
                num = int(part)
                if num < 1 or num > max_num:
                    raise ValueError(f"잘못된 번호: {num} (1-{max_num} 사이여야 함)")
                indices.append(num)
        
        return sorted(list(set(indices)))
    
    def _setup_token_group(self, tokens: List[TokenInfo], group_name: str) -> bool:
        """토큰 그룹 설정"""
        success_count = 0
        
        for i, token in enumerate(tokens, 1):
            print(f"\n{'='*60}")
            print(f"📝 토큰 설정 {i}/{len(tokens)}: {token.name}")
            print(f"{'='*60}")
            
            if self._setup_single_token(token):
                success_count += 1
            else:
                if token.required:
                    print(f"❌ 필수 토큰 '{token.name}' 설정에 실패했습니다.")
                    return False
        
        print(f"\n🎉 {group_name} 토큰 설정 완료!")
        print(f"✅ 성공: {success_count}/{len(tokens)}")
        
        # .env 파일 저장
        if self._save_env_file():
            print("💾 설정이 .env 파일에 저장되었습니다.")
            self._print_next_steps()
            return True
        else:
            print("❌ .env 파일 저장에 실패했습니다.")
            return False
    
    def _setup_single_token(self, token: TokenInfo) -> bool:
        """개별 토큰 설정"""
        print(f"\n📖 {token.name}")
        print(f"설명: {token.description}")
        print(f"필수 여부: {'🔴 필수' if token.required else '🟡 선택사항'}")
        
        # 현재 값 확인
        current_value = self.current_values.get(token.env_var, "")
        if current_value:
            masked_value = self._mask_value(current_value, token.is_sensitive)
            print(f"현재 값: {masked_value}")
        
        # 설정 옵션 제시
        print(f"\n📋 설정 옵션:")
        print(f"1. 새 값 입력")
        if current_value:
            print(f"2. 현재 값 유지")
        print(f"3. 가이드 보기")
        if not token.required:
            print(f"4. 건너뛰기")
        
        while True:
            choice = input(f"\n선택 (1-{'4' if not token.required else '3'}): ").strip()
            
            if choice == "1":
                return self._input_token_value(token)
            elif choice == "2" and current_value:
                print(f"✅ 현재 값을 유지합니다.")
                return True
            elif choice == "3":
                self._show_token_guide(token)
                continue
            elif choice == "4" and not token.required:
                print(f"⏭️ {token.name} 설정을 건너뜁니다.")
                return True
            else:
                print(f"❌ 잘못된 선택입니다.")
    
    def _input_token_value(self, token: TokenInfo) -> bool:
        """토큰 값 입력"""
        print(f"\n🔐 {token.name} 입력:")
        print(f"💡 빈 값을 입력하면 설정을 건너뜁니다.")
        
        try:
            if token.is_sensitive:
                value = getpass(f"토큰 입력 (입력 내용이 숨겨집니다): ")
            else:
                value = input(f"값 입력: ")
            
            value = value.strip()
            
            if not value:
                if token.required:
                    print(f"❌ 필수 토큰은 비워둘 수 없습니다.")
                    return self._input_token_value(token)
                else:
                    print(f"⏭️ 빈 값으로 인해 설정을 건너뜁니다.")
                    return True
            
            # 값 검증
            if self._validate_token_value(token, value):
                self.current_values[token.env_var] = value
                print(f"✅ {token.name} 설정 완료!")
                return True
            else:
                print(f"❌ 잘못된 형식입니다. 다시 입력해주세요.")
                return self._input_token_value(token)
                
        except KeyboardInterrupt:
            print(f"\n⏹️ 설정을 취소했습니다.")
            return False
    
    def _validate_token_value(self, token: TokenInfo, value: str) -> bool:
        """토큰 값 검증"""
        if not value.strip():
            return not token.required
        
        # 기본적인 형식 검증
        validations = {
            "OPENAI_API_KEY": lambda v: v.startswith("sk-") and len(v) > 20,
            "REDDIT_CLIENT_ID": lambda v: len(v) > 10 and not v.startswith("your_"),
            "REDDIT_CLIENT_SECRET": lambda v: len(v) > 10 and not v.startswith("your_"),
            "REDDIT_USERNAME": lambda v: len(v) > 0 and not v.startswith("your_"),
            "REDDIT_PASSWORD": lambda v: len(v) > 0 and not v.startswith("your_"),
            "UNSPLASH_ACCESS_KEY": lambda v: len(v) > 20,
            "SUPABASE_URL": lambda v: v.startswith("https://") and "supabase" in v,
            "SUPABASE_KEY": lambda v: len(v) > 50,
            "NOTION_TOKEN": lambda v: v.startswith("secret_") and len(v) > 30,
            "NOTION_DATABASE_ID": lambda v: len(v) == 32 and v.replace("-", "").isalnum(),
            "FIGMA_ACCESS_TOKEN": lambda v: v.startswith("figd_") and len(v) > 20,
            "VERCEL_TOKEN": lambda v: len(v) > 20
        }
        
        validator = validations.get(token.env_var)
        if validator:
            is_valid = validator(value)
            if not is_valid:
                print(f"⚠️ 토큰 형식이 올바르지 않을 수 있습니다.")
                confirm = input("그래도 저장하시겠습니까? (y/n): ").lower().strip()
                return confirm in ['y', 'yes', '예']
        
        return True
    
    def _show_token_guide(self, token: TokenInfo):
        """토큰 가이드 표시"""
        print(f"\n📖 {token.name} 설정 가이드")
        print("=" * 50)
        print(f"🌐 발급 페이지: {token.get_url}")
        print()
        print("📋 단계별 안내:")
        for step in token.instructions:
            print(f"   {step}")
        
        if token.test_command:
            print(f"\n🧪 테스트: {token.test_command}")
        
        print()
        input("📚 가이드를 확인했으면 Enter를 누르세요...")
    
    def _mask_value(self, value: str, is_sensitive: bool) -> str:
        """값 마스킹"""
        if not is_sensitive:
            return value
        
        if len(value) <= 8:
            return "*" * len(value)
        else:
            return value[:4] + "*" * (len(value) - 8) + value[-4:]
    
    def _view_current_config(self) -> bool:
        """현재 설정 상태 확인"""
        print(f"\n👀 현재 설정 상태")
        print("=" * 60)
        
        # 필수 토큰
        print(f"\n🔴 필수 토큰:")
        required_set = 0
        for token in [t for t in self.tokens if t.required]:
            if token.env_var in self.current_values:
                value = self.current_values[token.env_var]
                masked = self._mask_value(value, token.is_sensitive)
                print(f"   ✅ {token.name}: {masked}")
                required_set += 1
            else:
                print(f"   ❌ {token.name}: 미설정")
        
        # 선택적 토큰
        print(f"\n🟡 선택적 토큰:")
        optional_set = 0
        for token in [t for t in self.tokens if not t.required]:
            if token.env_var in self.current_values:
                value = self.current_values[token.env_var]
                masked = self._mask_value(value, token.is_sensitive)
                print(f"   ✅ {token.name}: {masked}")
                optional_set += 1
            else:
                print(f"   ❌ {token.name}: 미설정")
        
        # 통계
        required_total = len([t for t in self.tokens if t.required])
        optional_total = len([t for t in self.tokens if not t.required])
        
        print(f"\n📊 설정 통계:")
        print(f"   🔴 필수 토큰: {required_set}/{required_total} ({required_set/required_total*100:.0f}%)")
        print(f"   🟡 선택적 토큰: {optional_set}/{optional_total} ({optional_set/optional_total*100:.0f}%)")
        
        # 상태 평가
        if required_set == required_total:
            print(f"\n🎉 기본 기능 사용 준비 완료!")
        else:
            print(f"\n⚠️ 추가 설정이 필요합니다.")
        
        print(f"\n💾 설정 파일: {self.env_file}")
        
        input(f"\n📚 확인했으면 Enter를 누르세요...")
        return True
    
    def _save_env_file(self) -> bool:
        """환경 변수 파일 저장"""
        try:
            # 기존 .env 파일 백업
            if self.env_file.exists():
                backup_file = Path(f".env.backup.{int(time.time())}")
                self.env_file.rename(backup_file)
                print(f"💾 기존 설정을 {backup_file}에 백업했습니다.")
            
            # 새 .env 파일 생성
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write("# AI App Factory Configuration\n")
                f.write(f"# Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # 필수 토큰
                f.write("# ===== 필수 토큰 (Required Tokens) =====\n")
                for token in [t for t in self.tokens if t.required]:
                    value = self.current_values.get(token.env_var, "")
                    f.write(f"# {token.description}\n")
                    f.write(f"{token.env_var}={value}\n\n")
                
                # 선택적 토큰
                f.write("# ===== 선택적 토큰 (Optional Tokens) =====\n")
                for token in [t for t in self.tokens if not t.required]:
                    value = self.current_values.get(token.env_var, "")
                    f.write(f"# {token.description}\n")
                    f.write(f"{token.env_var}={value}\n\n")
                
                # 추가 설정
                f.write("# ===== 추가 설정 (Additional Settings) =====\n")
                f.write("DEBUG=false\n")
                f.write("LOG_LEVEL=INFO\n")
            
            return True
            
        except Exception as e:
            print(f"❌ .env 파일 저장 오류: {e}")
            return False
    
    def _print_next_steps(self):
        """다음 단계 안내"""
        print(f"\n🎉 토큰 설정이 완료되었습니다!")
        print("=" * 50)
        print()
        print("🚀 다음 단계:")
        print("   1. 설정 확인: python main.py --validate-env")
        print("   2. 드라이런 테스트: python main.py --trend \"AI fitness\" --dry-run")
        print("   3. 실제 실행: python main.py --trend \"AI fitness\"")
        print()
        print("📚 추가 명령어:")
        print("   • 도움말: python main.py --help")
        print("   • 워크플로우 목록: python main.py --list-workflows")
        print("   • 설정 재실행: python setup_tokens.py")
        print()
        print("🔐 보안 주의사항:")
        print("   • .env 파일을 git에 커밋하지 마세요")
        print("   • API 키를 다른 사람과 공유하지 마세요")
        print("   • 정기적으로 토큰을 재생성하세요")
        print()

def main():
    """메인 함수"""
    try:
        wizard = TokenSetupWizard()
        wizard.run_setup_wizard()
        
    except KeyboardInterrupt:
        print(f"\n⏹️ 설정을 취소했습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()