# API 키 설정 완전 가이드 🔑

## 🎯 개요

AI App Factory를 사용하기 위해 필요한 API 키들을 쉽게 설정할 수 있는 완전한 가이드입니다.

## 🚀 빠른 시작 (3분 설정)

### 방법 1: 자동 설정 마법사 🪄
```bash
python setup_tokens.py
```
- 대화형 가이드로 모든 토큰을 단계별 설정
- 상세한 발급 안내와 예시 제공
- 자동 검증 및 .env 파일 생성

### 방법 2: 간단한 토큰 관리자 ⚡
```bash
python token_manager.py
```
- 빠르고 간단한 토큰 설정
- 현재 상태 확인 및 개별 토큰 관리
- 실시간 형식 검증

### 방법 3: 완전 자동 설치 🎯
```bash
python install.py
```
- 시스템 요구사항부터 API 키까지 모든 것을 한 번에
- 패키지 설치 + 토큰 설정 + 테스트
- 초보자 추천

## 📋 필요한 API 키 목록

### 🔴 필수 토큰 (기본 기능)

#### 1. OpenAI API Key 🤖
- **용도**: AI 기반 UX 분석, 페르소나 생성
- **비용**: 사용량 기반 (소량 사용 시 월 $5-10)
- **발급**: https://platform.openai.com/api-keys

#### 2. Reddit API 📊
- **용도**: 실시간 트렌드 데이터 수집
- **비용**: 무료
- **발급**: https://www.reddit.com/prefs/apps

### 🟡 선택적 토큰 (고급 기능)

#### 3. Unsplash API 📸
- **용도**: 고품질 트렌드 이미지 수집
- **비용**: 무료 (월 50회 요청)
- **발급**: https://unsplash.com/developers

#### 4. Supabase 💾
- **용도**: 워크플로우 결과 데이터베이스 저장
- **비용**: 무료 플랜 사용 가능
- **발급**: https://supabase.com

#### 5. Notion API 📄
- **용도**: 자동 프로젝트 보고서 생성
- **비용**: 무료
- **발급**: https://www.notion.so/my-integrations

#### 6. Figma API 🎨
- **용도**: 디자인 시스템 연동
- **비용**: 무료
- **발급**: Figma 계정 설정 페이지

#### 7. Vercel API 🚀
- **용도**: 자동 배포
- **비용**: 무료 플랜 사용 가능
- **발급**: https://vercel.com/account/tokens

## 🔧 단계별 설정 가이드

### 1️⃣ OpenAI API Key 설정

```
1. https://platform.openai.com 접속
2. 로그인 후 'API Keys' 메뉴 클릭
3. 'Create new secret key' 버튼 클릭
4. 키 이름 입력 (예: AI App Factory)
5. 생성된 키 복사 (sk-로 시작하는 긴 문자열)
```

**예시**: `sk-proj-abc123def456...`

**💰 비용 관리 팁**:
- Usage 페이지에서 사용량 모니터링
- Billing limits 설정으로 예산 관리
- 소량 사용 시 월 $5-10 정도

### 2️⃣ Reddit API 설정

```
1. https://www.reddit.com/prefs/apps 접속
2. Reddit 계정으로 로그인
3. 'Create App' 또는 'Create Another App' 클릭
4. 앱 정보 입력:
   - name: AI App Factory
   - App type: script 선택
   - description: 트렌드 분석용
   - about url: (비워두거나 GitHub URL)
   - redirect uri: http://localhost:8080
5. 'create app' 클릭
```

**생성 후 필요한 정보**:
- **Client ID**: 앱 이름 아래의 14자리 문자열
- **Client Secret**: 'secret' 항목의 값
- **Username**: Reddit 사용자명
- **Password**: Reddit 비밀번호

### 3️⃣ Unsplash API 설정 (선택사항)

```
1. https://unsplash.com/developers 접속
2. 'Your apps' 클릭
3. 'New Application' 클릭
4. 약관 동의 체크
5. 앱 정보 입력:
   - Application name: AI App Factory
   - Description: 트렌드 이미지 수집
6. 'Create Application' 클릭
7. 'Access Key' 복사
```

### 4️⃣ Supabase 설정 (선택사항)

```
1. https://supabase.com 접속 후 회원가입
2. 'New Project' 클릭
3. 프로젝트 정보 입력 후 생성
4. 프로젝트 생성 완료 후 'Settings' > 'API' 이동
5. 다음 정보 복사:
   - Project URL: https://xxx.supabase.co
   - anon public key: eyJ로 시작하는 긴 문자열
```

### 5️⃣ Notion API 설정 (선택사항)

```
1. https://www.notion.so/my-integrations 접속
2. 'New integration' 클릭
3. 통합 정보 입력:
   - Name: AI App Factory
   - Associated workspace: 본인 워크스페이스
4. 'Submit' 클릭
5. 'Internal Integration Token' 복사 (secret_로 시작)

데이터베이스 설정:
6. Notion에서 새 데이터베이스 페이지 생성
7. 데이터베이스 '...' 메뉴 > 'Connections' > 생성한 통합 추가
8. 페이지 URL에서 32자리 데이터베이스 ID 복사
```

### 6️⃣ Figma API 설정 (선택사항)

```
1. Figma 계정 설정 페이지 접속
2. 'Personal access tokens' 섹션 찾기
3. 'Create new token' 클릭
4. 토큰 이름 입력 (예: AI App Factory)
5. 토큰 범위 선택 (File content 필요)
6. 생성된 토큰 복사 (figd_로 시작)
```

### 7️⃣ Vercel API 설정 (선택사항)

```
1. https://vercel.com/account/tokens 접속
2. 'Create Token' 클릭
3. 토큰 정보 입력:
   - Token Name: AI App Factory
   - Scope: Full Account (또는 필요한 프로젝트만)
   - Expiration: 원하는 만료일
4. 'Create' 클릭
5. 생성된 토큰 복사
```

## 💾 설정 파일 관리

### .env 파일 형식
```bash
# 필수 토큰
OPENAI_API_KEY=sk-proj-your-openai-key-here
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret
REDDIT_USERNAME=your-reddit-username
REDDIT_PASSWORD=your-reddit-password

# 선택적 토큰
UNSPLASH_ACCESS_KEY=your-unsplash-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
NOTION_TOKEN=secret_your-notion-token
NOTION_DATABASE_ID=your-32-char-database-id
FIGMA_ACCESS_TOKEN=figd_your-figma-token
VERCEL_TOKEN=your-vercel-token

# 추가 설정
DEBUG=false
LOG_LEVEL=INFO
```

### 보안 주의사항 🔒
- ❌ `.env` 파일을 git에 커밋하지 마세요
- ❌ API 키를 다른 사람과 공유하지 마세요
- ✅ 정기적으로 토큰을 재생성하세요
- ✅ 사용하지 않는 토큰은 삭제하세요

## 🧪 설정 확인 및 테스트

### 환경 검증
```bash
# 전체 환경 검증
python main.py --validate-env

# 토큰 상태 확인
python token_manager.py  # 메뉴에서 '3. 현재 상태 확인' 선택
```

### 드라이런 테스트
```bash
# 설정 확인용 드라이런
python main.py --trend "AI fitness" --dry-run

# 실제 기능 테스트 (API 호출 없음)
python main.py --trend "meditation apps" --no-supabase --dry-run
```

### 실제 실행 테스트
```bash
# 필수 토큰만으로 기본 기능 테스트
python main.py --trend "productivity tools" --category productivity

# 모든 기능 테스트
python main.py --trend "AI fitness" --notion-report
```

## 🔧 문제 해결

### 자주 발생하는 오류

#### 1. OpenAI API 키 오류
```
Error: 401 Unauthorized
해결: API 키가 올바른지 확인, 사용량 한도 확인
```

#### 2. Reddit API 오류
```
Error: 401 Client credential
해결: Client ID, Secret이 정확한지 확인
```

#### 3. 환경 변수 로드 실패
```
Error: API key for openai not found
해결: .env 파일이 프로젝트 루트에 있는지 확인
```

### 토큰 재설정
```bash
# 전체 토큰 재설정
python setup_tokens.py

# 개별 토큰 수정
python token_manager.py

# 설정 초기화
python token_manager.py  # 메뉴에서 '5. 설정 초기화' 선택
```

## 💰 비용 최적화 가이드

### OpenAI API 비용 절약
- **GPT-3.5-turbo 사용**: GPT-4보다 10배 저렴
- **프롬프트 최적화**: 불필요한 토큰 사용 줄이기
- **배치 처리**: 여러 요청을 한 번에 처리
- **사용량 모니터링**: 일일/월간 한도 설정

### 무료 플랜 활용
- **Reddit API**: 완전 무료, 제한 없음
- **Unsplash**: 월 50회 무료
- **Supabase**: 무료 플랜으로 충분
- **Notion API**: 완전 무료
- **Vercel**: 개인 프로젝트 무료

## 🎯 권장 설정 전략

### 1단계: 최소 설정 (필수만)
```bash
✅ OpenAI API Key
✅ Reddit API (4개 값)
❌ 기타 모든 선택적 토큰
```
**결과**: 기본 기능 모두 사용 가능, Mock 데이터로 고급 기능 시뮬레이션

### 2단계: 기본 설정 (+이미지)
```bash
✅ 1단계 토큰
✅ Unsplash API Key
❌ 기타 선택적 토큰
```
**결과**: 실제 트렌드 이미지 수집, 더 완성도 높은 결과

### 3단계: 완전 설정 (모든 기능)
```bash
✅ 1-2단계 토큰
✅ Supabase (저장)
✅ Notion API (보고서)
✅ Figma API (디자인)
✅ Vercel API (배포)
```
**결과**: 모든 기능 활용, 완전 자동화된 워크플로우

## 📞 도움받기

### 자동 진단
```bash
# 시스템 상태 확인
python system_health_check.py

# 환경 검증
python main.py --validate-env

# 토큰 테스트
python token_manager.py  # 메뉴에서 '4. 토큰 테스트'
```

### 수동 확인
1. `.env` 파일이 프로젝트 루트에 있는지 확인
2. API 키 형식이 올바른지 확인 (예: OpenAI는 sk-로 시작)
3. 인터넷 연결 상태 확인
4. Python 패키지가 모두 설치되었는지 확인

---

## 🎉 마무리

모든 토큰을 설정했다면 이제 AI App Factory의 강력한 기능을 체험해보세요!

```bash
# 첫 번째 앱 생성
python main.py --trend "AI fitness" --category health

# 결과 확인
python main.py --list-workflows
```

**30분 만에 아이디어에서 완성된 앱 프로토타입까지!** 🚀

*Happy coding! 🏭✨*