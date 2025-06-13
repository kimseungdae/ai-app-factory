import logging
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..utils.config import config
from ..utils.api_clients import api_manager

logger = logging.getLogger(__name__)

class UXResearcher:
    def __init__(self):
        self.enabled = config.is_agent_enabled('ux_researcher')
        self.sources = config.get('agents.ux_researcher.sources', ['reddit', 'google_trends'])
        
        if not self.enabled:
            logger.info("UX Researcher agent is disabled")
            return
        
        self.reddit_client = api_manager.get_client('reddit')
        self.trends_client = api_manager.get_client('google_trends')
        self.openai_client = api_manager.get_client('openai')
        self.web_scraper = api_manager.get_client('web_scraper')
        
        # Persona templates for different categories
        self.persona_templates = {
            'productivity': ['바쁜 직장인', '프리랜서', '학생'],
            'health': ['건강 관리자', '운동 초보자', '의료진'],
            'finance': ['투자 초보자', '절약형 소비자', '사업가'],
            'education': ['온라인 학습자', '교육자', '직무 전환자'],
            'entertainment': ['콘텐츠 소비자', '크리에이터', '게이머'],
            'business': ['스타트업 창업자', 'B2B 담당자', '마케터'],
            'technology': ['얼리어답터', '개발자', 'IT 관리자'],
            'lifestyle': ['라이프스타일 추구자', '소셜미디어 유저', '트렌드 세터']
        }
    
    def analyze_ux_for_trend(self, trend_keyword: str, category: str = 'general') -> Dict[str, Any]:
        """
        Main method to perform comprehensive UX analysis for a trending keyword
        """
        if not self.enabled:
            return {"error": "UX Researcher agent is disabled"}
        
        try:
            logger.info(f"Starting UX analysis for trend: {trend_keyword}")
            
            # Step 1: Generate user personas
            personas = self._generate_user_personas(trend_keyword, category)
            
            # Step 2: Analyze user needs using Jobs-to-be-Done framework
            user_needs = self._analyze_user_needs_jtbd(trend_keyword, category)
            
            # Step 3: Research competitor apps
            competitor_analysis = self._analyze_competitor_apps(trend_keyword)
            
            # Step 4: Generate UX strategy
            ux_strategy = self._generate_ux_strategy(trend_keyword, personas, user_needs, competitor_analysis)
            
            # Step 5: Additional insights
            user_journey = self._map_user_journey(trend_keyword, personas[0] if personas else None)
            pain_points = self._identify_key_pain_points(trend_keyword)
            
            return {
                'trend_keyword': trend_keyword,
                'category': category,
                'personas': personas,
                'user_needs': user_needs,
                'competitor_analysis': competitor_analysis,
                'ux_strategy': ux_strategy,
                'user_journey': user_journey,
                'key_pain_points': pain_points,
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in UX analysis: {e}")
            return {"error": str(e)}
    
    def _generate_user_personas(self, trend_keyword: str, category: str) -> List[Dict[str, Any]]:
        """Generate 3 detailed user personas using Claude API"""
        try:
            logger.info(f"Generating user personas for {trend_keyword}")
            
            prompt = f"""
            {trend_keyword}과(와) 관련된 앱/서비스의 타겟 사용자 페르소나 3개를 생성해주세요.
            각 페르소나는 다른 사용자 세그먼트를 대표해야 합니다.

            다음 JSON 형식으로 응답해주세요:
            {{
                "personas": [
                    {{
                        "name": "구체적인 한국 이름과 직업 (예: 바쁜 직장인 김현수)",
                        "age": 나이,
                        "occupation": "직업",
                        "background": "배경 설명 (100자 이내)",
                        "pain_points": ["구체적인 문제점 1", "구체적인 문제점 2", "구체적인 문제점 3"],
                        "motivations": ["동기 1", "동기 2", "동기 3"],
                        "tech_savviness": "초급/중급/고급",
                        "daily_challenges": ["일상의 도전과제 1", "일상의 도전과제 2"],
                        "preferred_features": ["선호하는 기능 1", "선호하는 기능 2", "선호하는 기능 3"]
                    }}
                ]
            }}

            카테고리: {category}
            
            실제 한국 사용자들의 특성을 반영하고, 각 페르소나가 {trend_keyword}에 대해 다른 접근 방식과 니즈를 가지도록 해주세요.
            """
            
            response = self.openai_client.generate_text(prompt, temperature=0.7)
            
            # JSON 응답 파싱
            try:
                parsed_response = self._extract_json_from_response(response)
                return parsed_response.get('personas', [])
            except:
                # Fallback: 구조화된 응답 생성
                return self._create_fallback_personas(trend_keyword, category)
                
        except Exception as e:
            logger.error(f"Error generating personas: {e}")
            return self._create_fallback_personas(trend_keyword, category)
    
    def _analyze_user_needs_jtbd(self, trend_keyword: str, category: str) -> Dict[str, Any]:
        """Analyze user needs using Jobs-to-be-Done framework"""
        try:
            logger.info(f"Analyzing user needs with JTBD framework for {trend_keyword}")
            
            prompt = f"""
            {trend_keyword}과(와) 관련된 서비스에 대해 Jobs-to-be-Done 프레임워크를 사용하여 사용자 니즈를 분석해주세요.

            다음 JSON 형식으로 응답해주세요:
            {{
                "functional_jobs": [
                    {{
                        "job": "사용자가 달성하려는 기능적 목표",
                        "current_solution": "현재 사용하는 해결책",
                        "satisfaction_level": "1-10점",
                        "improvement_opportunity": "개선 기회"
                    }}
                ],
                "emotional_jobs": [
                    {{
                        "job": "사용자가 느끼고 싶은 감정",
                        "current_gap": "현재 부족한 부분",
                        "desired_outcome": "원하는 결과"
                    }}
                ],
                "social_jobs": [
                    {{
                        "job": "사회적으로 보이고 싶은 모습",
                        "context": "상황/맥락",
                        "barriers": "현재 장벽"
                    }}
                ],
                "key_insights": [
                    "핵심 인사이트 1",
                    "핵심 인사이트 2", 
                    "핵심 인사이트 3"
                ]
            }}

            카테고리: {category}
            한국 사용자의 문화적 특성과 행동 패턴을 고려해주세요.
            """
            
            response = self.openai_client.generate_text(prompt, temperature=0.6)
            
            try:
                return self._extract_json_from_response(response)
            except:
                return self._create_fallback_jtbd(trend_keyword, category)
                
        except Exception as e:
            logger.error(f"Error analyzing user needs: {e}")
            return self._create_fallback_jtbd(trend_keyword, category)
    
    def _analyze_competitor_apps(self, trend_keyword: str) -> Dict[str, Any]:
        """Analyze competitor apps (simulated App Store research)"""
        try:
            logger.info(f"Analyzing competitor apps for {trend_keyword}")
            
            # Reddit에서 관련 앱 추천 수집
            reddit_app_mentions = self._collect_app_mentions_from_reddit(trend_keyword)
            
            prompt = f"""
            {trend_keyword}과(와) 관련된 기존 앱들의 경쟁 분석을 해주세요.
            다음 Reddit 멘션 데이터를 참고하되, 실제 존재할 법한 앱들을 분석해주세요:
            
            Reddit 멘션 데이터: {reddit_app_mentions[:3]}

            다음 JSON 형식으로 응답해주세요:
            {{
                "top_competitors": [
                    {{
                        "app_name": "앱 이름",
                        "category": "카테고리",
                        "key_features": ["주요 기능 1", "주요 기능 2", "주요 기능 3"],
                        "strengths": ["강점 1", "강점 2"],
                        "weaknesses": ["약점 1", "약점 2"],
                        "user_rating": "4.2/5.0 (추정)",
                        "pricing_model": "무료/유료/프리미엄",
                        "target_audience": "주요 타겟층"
                    }}
                ],
                "market_gaps": [
                    "시장에서 부족한 부분 1",
                    "시장에서 부족한 부분 2",
                    "시장에서 부족한 부분 3"
                ],
                "common_complaints": [
                    "사용자들의 공통 불만사항 1",
                    "사용자들의 공통 불만사항 2"
                ],
                "success_patterns": [
                    "성공하는 앱들의 공통점 1",
                    "성공하는 앱들의 공통점 2"
                ]
            }}

            한국 앱스토어 상황과 한국 사용자 선호도를 고려해주세요.
            실제 존재할 법한 앱 이름과 특징을 사용해주세요.
            """
            
            response = self.openai_client.generate_text(prompt, temperature=0.5)
            
            try:
                return self._extract_json_from_response(response)
            except:
                return self._create_fallback_competitor_analysis(trend_keyword)
                
        except Exception as e:
            logger.error(f"Error analyzing competitors: {e}")
            return self._create_fallback_competitor_analysis(trend_keyword)
    
    def _generate_ux_strategy(self, trend_keyword: str, personas: List[Dict], user_needs: Dict, competitor_analysis: Dict) -> Dict[str, Any]:
        """Generate 3 UX strategy directions"""
        try:
            logger.info(f"Generating UX strategy for {trend_keyword}")
            
            personas_summary = str(personas)[:500] if personas else "페르소나 정보 없음"
            needs_summary = str(user_needs)[:500] if user_needs else "니즈 정보 없음"
            competitor_summary = str(competitor_analysis)[:500] if competitor_analysis else "경쟁사 정보 없음"
            
            prompt = f"""
            {trend_keyword}을(를) 위한 UX 전략 3가지 방향을 제시해주세요.

            참고 정보:
            - 페르소나: {personas_summary}
            - 사용자 니즈: {needs_summary}
            - 경쟁사 분석: {competitor_summary}

            다음 JSON 형식으로 응답해주세요:
            {{
                "strategies": [
                    {{
                        "direction": "전략 방향 1 (예: 원터치 간편 사용)",
                        "core_concept": "핵심 컨셉 설명",
                        "target_persona": "주요 타겟 페르소나",
                        "key_features": ["핵심 기능 1", "핵심 기능 2", "핵심 기능 3"],
                        "differentiation": "기존 앱 대비 차별화 포인트",
                        "user_flow": ["단계 1", "단계 2", "단계 3"],
                        "success_metrics": ["성공 지표 1", "성공 지표 2"],
                        "implementation_priority": "높음/중간/낮음"
                    }}
                ],
                "recommended_strategy": {{
                    "strategy_index": 0,
                    "reason": "추천 이유",
                    "expected_outcome": "기대 효과"
                }},
                "design_principles": [
                    "디자인 원칙 1",
                    "디자인 원칙 2",
                    "디자인 원칙 3"
                ]
            }}

            각 전략은 서로 다른 접근 방식을 가져야 하며, 한국 사용자의 특성을 반영해주세요.
            """
            
            response = self.openai_client.generate_text(prompt, temperature=0.7)
            
            try:
                return self._extract_json_from_response(response)
            except:
                return self._create_fallback_ux_strategy(trend_keyword)
                
        except Exception as e:
            logger.error(f"Error generating UX strategy: {e}")
            return self._create_fallback_ux_strategy(trend_keyword)
    
    def _map_user_journey(self, trend_keyword: str, primary_persona: Dict = None) -> Dict[str, Any]:
        """Map user journey for the primary persona"""
        try:
            persona_info = str(primary_persona)[:300] if primary_persona else "기본 사용자"
            
            prompt = f"""
            {trend_keyword} 관련 서비스의 사용자 여정을 매핑해주세요.
            
            주요 페르소나: {persona_info}

            다음 JSON 형식으로 응답해주세요:
            {{
                "journey_stages": [
                    {{
                        "stage": "단계명 (예: 인지)",
                        "user_actions": ["사용자 행동 1", "사용자 행동 2"],
                        "emotions": ["감정 상태 1", "감정 상태 2"],
                        "pain_points": ["고충 1", "고충 2"],
                        "opportunities": ["개선 기회 1", "개선 기회 2"]
                    }}
                ],
                "critical_moments": [
                    {{
                        "moment": "중요한 순간",
                        "description": "설명",
                        "impact": "영향도 (높음/중간/낮음)"
                    }}
                ]
            }}
            """
            
            response = self.openai_client.generate_text(prompt, temperature=0.6)
            
            try:
                return self._extract_json_from_response(response)
            except:
                return self._create_fallback_user_journey(trend_keyword)
                
        except Exception as e:
            logger.error(f"Error mapping user journey: {e}")
            return self._create_fallback_user_journey(trend_keyword)
    
    def _identify_key_pain_points(self, trend_keyword: str) -> List[Dict[str, Any]]:
        """Identify key pain points from Reddit discussions"""
        try:
            logger.info(f"Identifying pain points for {trend_keyword}")
            
            # Reddit에서 페인 포인트 수집
            reddit_pain_points = []
            subreddits = ['productivity', 'apps', 'software', 'startups', 'entrepreneur']
            
            for subreddit in subreddits:
                try:
                    posts = self.reddit_client.search_posts(
                        query=f"{trend_keyword} problem OR {trend_keyword} issue OR {trend_keyword} frustrating OR {trend_keyword} difficult",
                        subreddit=subreddit,
                        limit=5
                    )
                    
                    for post in posts:
                        if post['score'] >= 3:
                            reddit_pain_points.append({
                                'title': post['title'],
                                'content': post.get('selftext', '')[:200],
                                'score': post['score'],
                                'subreddit': subreddit
                            })
                except:
                    continue
            
            # Claude로 페인 포인트 분석
            if reddit_pain_points:
                reddit_summary = str(reddit_pain_points[:5])
                
                prompt = f"""
                다음 Reddit 데이터를 분석하여 {trend_keyword}과(와) 관련된 주요 페인 포인트를 식별해주세요:

                {reddit_summary}

                다음 JSON 형식으로 응답해주세요:
                {{
                    "pain_points": [
                        {{
                            "category": "카테고리 (예: 사용성, 성능, 기능)",
                            "description": "페인 포인트 설명",
                            "frequency": "높음/중간/낮음",
                            "severity": "심각도 (1-10)",
                            "user_quotes": ["사용자 의견 1", "사용자 의견 2"]
                        }}
                    ]
                }}
                """
                
                response = self.openai_client.generate_text(prompt, temperature=0.5)
                
                try:
                    result = self._extract_json_from_response(response)
                    return result.get('pain_points', [])
                except:
                    pass
            
            return self._create_fallback_pain_points(trend_keyword)
            
        except Exception as e:
            logger.error(f"Error identifying pain points: {e}")
            return self._create_fallback_pain_points(trend_keyword)
    
    def _collect_app_mentions_from_reddit(self, trend_keyword: str) -> List[str]:
        """Collect app mentions from Reddit discussions"""
        try:
            app_mentions = []
            subreddits = ['apps', 'software', 'productivity', 'androidapps', 'iphone']
            
            for subreddit in subreddits:
                try:
                    posts = self.reddit_client.search_posts(
                        query=f"{trend_keyword} app OR {trend_keyword} software OR {trend_keyword} tool",
                        subreddit=subreddit,
                        limit=3
                    )
                    
                    for post in posts:
                        app_mentions.append(post['title'])
                        if post.get('selftext'):
                            app_mentions.append(post['selftext'][:100])
                except:
                    continue
            
            return app_mentions[:10]
            
        except Exception as e:
            logger.warning(f"Could not collect app mentions: {e}")
            return []
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from Claude API response"""
        # JSON 블록 찾기
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # {} 로 감싸진 JSON 찾기
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                raise ValueError("No JSON found in response")
        
        return json.loads(json_str)
    
    def _create_fallback_personas(self, trend_keyword: str, category: str) -> List[Dict[str, Any]]:
        """Create fallback personas when API fails"""
        return [
            {
                "name": f"바쁜 직장인 김현수",
                "age": 28,
                "occupation": "마케팅 담당자",
                "background": f"{trend_keyword}에 관심이 많지만 시간이 부족한 직장인",
                "pain_points": ["시간 부족", "복잡한 인터페이스 싫어함", "학습 비용 부담"],
                "motivations": ["효율성", "간편함", "성취감"],
                "tech_savviness": "중급",
                "daily_challenges": ["업무 효율성 향상", "개인 시간 확보"],
                "preferred_features": ["간단한 UI", "빠른 실행", "자동화"]
            },
            {
                "name": f"열정적인 학생 이지은",
                "age": 22,
                "occupation": "대학생",
                "background": f"{trend_keyword} 분야에 관심이 많은 열정적인 학생",
                "pain_points": ["예산 제약", "전문 지식 부족", "선택 장애"],
                "motivations": ["학습", "성장", "트렌드 따라가기"],
                "tech_savviness": "고급",
                "daily_challenges": ["학업과 개인 발전 균형", "비용 절약"],
                "preferred_features": ["무료 기능", "학습 자료", "커뮤니티"]
            },
            {
                "name": f"신중한 중년 박철수",
                "age": 45,
                "occupation": "중간관리자",
                "background": f"{trend_keyword}에 관심은 있지만 신중하게 접근하는 중년층",
                "pain_points": ["기술 적응 어려움", "보안 우려", "복잡한 기능"],
                "motivations": ["안정성", "신뢰성", "검증된 솔루션"],
                "tech_savviness": "초급",
                "daily_challenges": ["새로운 기술 적응", "업무 안정성 유지"],
                "preferred_features": ["간단한 조작", "안전성", "고객 지원"]
            }
        ]
    
    def _create_fallback_jtbd(self, trend_keyword: str, category: str) -> Dict[str, Any]:
        """Create fallback JTBD analysis"""
        return {
            "functional_jobs": [
                {
                    "job": f"{trend_keyword} 관련 작업을 더 효율적으로 처리하기",
                    "current_solution": "기존 방식 또는 다른 앱 사용",
                    "satisfaction_level": "6/10",
                    "improvement_opportunity": "속도와 편의성 개선"
                }
            ],
            "emotional_jobs": [
                {
                    "job": "성취감과 만족감 느끼기",
                    "current_gap": "복잡하고 시간이 많이 걸림",
                    "desired_outcome": "쉽고 빠른 성취감"
                }
            ],
            "social_jobs": [
                {
                    "job": "트렌드를 따라가는 사람으로 보이기",
                    "context": "동료나 친구들 사이에서",
                    "barriers": "복잡한 기술에 대한 두려움"
                }
            ],
            "key_insights": [
                "사용자들은 간편함을 최우선으로 생각함",
                "학습 비용을 최소화하고 싶어함", 
                "즉시 사용 가능한 솔루션을 선호함"
            ]
        }
    
    def _create_fallback_competitor_analysis(self, trend_keyword: str) -> Dict[str, Any]:
        """Create fallback competitor analysis"""
        return {
            "top_competitors": [
                {
                    "app_name": f"{trend_keyword} Pro",
                    "category": "생산성",
                    "key_features": ["기본 기능", "프리미엄 기능", "클라우드 동기화"],
                    "strengths": ["기능이 많음", "안정적임"],
                    "weaknesses": ["복잡함", "가격이 비쌈"],
                    "user_rating": "4.2/5.0",
                    "pricing_model": "프리미엄",
                    "target_audience": "전문가"
                }
            ],
            "market_gaps": [
                "초보자를 위한 간단한 솔루션 부족",
                "합리적인 가격의 옵션 부족",
                "한국 사용자 특화 기능 부족"
            ],
            "common_complaints": [
                "너무 복잡함",
                "가격이 비쌈"
            ],
            "success_patterns": [
                "간단한 UI",
                "빠른 로딩"
            ]
        }
    
    def _create_fallback_ux_strategy(self, trend_keyword: str) -> Dict[str, Any]:
        """Create fallback UX strategy"""
        return {
            "strategies": [
                {
                    "direction": "원터치 간편 사용",
                    "core_concept": "최소한의 클릭으로 원하는 결과 달성",
                    "target_persona": "바쁜 직장인",
                    "key_features": ["5초 온보딩", "원클릭 실행", "자동 저장"],
                    "differentiation": "기존 앱 대비 50% 더 간단한 UI",
                    "user_flow": ["앱 실행", "즉시 사용", "자동 완료"],
                    "success_metrics": ["사용 시간 단축", "재사용률 증가"],
                    "implementation_priority": "높음"
                },
                {
                    "direction": "게임화된 경험",
                    "core_concept": "재미있는 방식으로 목표 달성 유도",
                    "target_persona": "열정적인 학생",
                    "key_features": ["포인트 시스템", "레벨업", "소셜 공유"],
                    "differentiation": "지루한 작업을 재미있게 만듦",
                    "user_flow": ["도전 과제 확인", "실행", "보상 획득"],
                    "success_metrics": ["일일 활성 사용자", "완료율"],
                    "implementation_priority": "중간"
                },
                {
                    "direction": "AI 맞춤형 가이드",
                    "core_concept": "사용자 수준에 맞는 개인화된 안내",
                    "target_persona": "신중한 중년",
                    "key_features": ["단계별 가이드", "AI 추천", "도움말"],
                    "differentiation": "개인화된 학습 경험 제공",
                    "user_flow": ["수준 측정", "맞춤 가이드", "점진적 발전"],
                    "success_metrics": ["학습 완료율", "만족도"],
                    "implementation_priority": "중간"
                }
            ],
            "recommended_strategy": {
                "strategy_index": 0,
                "reason": "가장 넓은 사용자층에게 어필 가능",
                "expected_outcome": "빠른 사용자 확보와 높은 재사용률"
            },
            "design_principles": [
                "최소한의 인터랙션으로 최대한의 효과",
                "일관된 디자인 패턴 사용",
                "명확하고 직관적인 인터페이스"
            ]
        }
    
    def _create_fallback_user_journey(self, trend_keyword: str) -> Dict[str, Any]:
        """Create fallback user journey"""
        return {
            "journey_stages": [
                {
                    "stage": "인지",
                    "user_actions": ["검색", "추천 받음"],
                    "emotions": ["호기심", "기대감"],
                    "pain_points": ["정보 부족", "선택 어려움"],
                    "opportunities": ["명확한 가치 제안", "간단한 설명"]
                },
                {
                    "stage": "사용",
                    "user_actions": ["다운로드", "가입", "첫 사용"],
                    "emotions": ["설렘", "불안감"],
                    "pain_points": ["복잡한 가입", "학습 필요"],
                    "opportunities": ["간편 가입", "즉시 사용 가능"]
                },
                {
                    "stage": "지속 사용",
                    "user_actions": ["반복 사용", "기능 탐색"],
                    "emotions": ["만족감", "익숙함"],
                    "pain_points": ["지루함", "한계 느낌"],
                    "opportunities": ["새로운 기능", "개인화"]
                }
            ],
            "critical_moments": [
                {
                    "moment": "첫 사용 후 5분",
                    "description": "사용자가 가치를 느끼는 첫 순간",
                    "impact": "높음"
                },
                {
                    "moment": "3일 후 재방문",
                    "description": "습관 형성의 중요한 시점",
                    "impact": "높음"
                }
            ]
        }
    
    def _create_fallback_pain_points(self, trend_keyword: str) -> List[Dict[str, Any]]:
        """Create fallback pain points"""
        return [
            {
                "category": "사용성",
                "description": "복잡하고 직관적이지 않은 인터페이스",
                "frequency": "높음",
                "severity": "8",
                "user_quotes": ["너무 복잡해요", "어떻게 사용하는지 모르겠어요"]
            },
            {
                "category": "성능", 
                "description": "느린 로딩 속도와 반응성",
                "frequency": "중간",
                "severity": "7",
                "user_quotes": ["너무 느려요", "계속 멈춰요"]
            },
            {
                "category": "기능",
                "description": "필요한 기능 부족",
                "frequency": "중간",
                "severity": "6",
                "user_quotes": ["이런 기능이 있으면 좋겠어요", "다른 앱에서는 되는데"]
            }
        ]

# Global instance
ux_researcher = UXResearcher()