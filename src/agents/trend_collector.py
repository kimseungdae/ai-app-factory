import logging
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from collections import Counter
from ..utils.config import config
from ..utils.api_clients import api_manager

logger = logging.getLogger(__name__)

class TrendCollector:
    def __init__(self):
        self.enabled = config.is_agent_enabled('trend_collector')
        self.update_interval = config.get('agents.trend_collector.update_interval', 3600)
        
        if not self.enabled:
            logger.info("Trend Collector agent is disabled")
            return
        
        self.reddit_client = api_manager.get_client('reddit')
        self.trends_client = api_manager.get_client('google_trends')
        self.unsplash_client = api_manager.get_client('unsplash')
        
        # Target subreddits for entrepreneurial trends
        self.target_subreddits = ['entrepreneur', 'SideProject', 'startups', 'apps']
        
        # Keywords to filter and categorize
        self.category_keywords = {
            'health': ['fitness', 'health', 'wellness', 'medical', 'mental health', 'nutrition', 'workout'],
            'productivity': ['productivity', 'efficiency', 'automation', 'workflow', 'task management', 'time management'],
            'finance': ['fintech', 'investing', 'cryptocurrency', 'banking', 'payments', 'money', 'budget'],
            'education': ['education', 'learning', 'course', 'teaching', 'training', 'skill'],
            'entertainment': ['gaming', 'streaming', 'content', 'social media', 'video', 'music'],
            'business': ['saas', 'b2b', 'marketplace', 'ecommerce', 'startup', 'business'],
            'technology': ['ai', 'machine learning', 'blockchain', 'cloud', 'mobile', 'web', 'api'],
            'lifestyle': ['travel', 'food', 'fashion', 'home', 'family', 'relationship']
        }
        
        self.trend_cache = {}
        self.last_update = None
    
    def collect_top_trends(self, limit: int = 10) -> Dict[str, Any]:
        """
        Main method to collect and rank top trends from all sources
        Returns top 10 trends with scores and related images
        """
        if not self.enabled:
            return {"error": "Trend Collector agent is disabled"}
        
        try:
            logger.info("Starting comprehensive trend collection...")
            
            # Step 1: Collect from all sources
            reddit_trends = self._collect_reddit_trends()
            google_trends = self._collect_google_trends()
            
            # Step 2: Extract and normalize keywords
            all_keywords = self._extract_keywords_from_sources(reddit_trends, google_trends)
            
            # Step 3: Score and rank keywords
            scored_trends = self._score_and_rank_trends(all_keywords, reddit_trends, google_trends)
            
            # Step 4: Get related images for top trends
            final_trends = self._enrich_with_images(scored_trends[:limit])
            
            return {
                'trends': final_trends,
                'total_keywords_analyzed': len(all_keywords),
                'data_sources_used': ['reddit', 'google_trends', 'unsplash'],
                'target_subreddits': self.target_subreddits,
                'collected_at': datetime.now().isoformat(),
                'next_update': (datetime.now() + timedelta(seconds=self.update_interval)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error collecting trends: {e}")
            return {"error": str(e)}
    
    def _collect_reddit_trends(self) -> List[Dict[str, Any]]:
        """Collect trending posts from target subreddits"""
        reddit_data = []
        
        for subreddit in self.target_subreddits:
            try:
                logger.info(f"Collecting from r/{subreddit}...")
                posts = self.reddit_client.get_hot_posts(subreddit, limit=25)
                
                for post in posts:
                    # Filter for quality posts
                    if post['score'] >= 50 and post['num_comments'] >= 5:
                        reddit_data.append({
                            'source': 'reddit',
                            'subreddit': subreddit,
                            'title': post['title'],
                            'content': post.get('selftext', '')[:500],  # First 500 chars
                            'score': post['score'],
                            'comments': post['num_comments'],
                            'url': post['url'],
                            'created_utc': post.get('created_utc', 0),
                            'engagement_score': self._calculate_engagement_score(post),
                            'collected_at': datetime.now().isoformat()
                        })
            except Exception as e:
                logger.error(f"Error collecting from r/{subreddit}: {e}")
                continue
        
        logger.info(f"Collected {len(reddit_data)} quality posts from Reddit")
        return reddit_data
    
    def _collect_google_trends(self) -> Dict[str, Any]:
        """Collect trending searches from Google Trends"""
        try:
            logger.info("Collecting Google Trends data...")
            
            # Get general trending searches
            trending_searches = self.trends_client.get_trending_searches('US')
            
            # Keywords related to entrepreneurship and apps
            startup_keywords = [
                'startup ideas', 'app development', 'saas', 'mvp', 'side project',
                'entrepreneurship', 'business ideas', 'ai tools', 'productivity apps'
            ]
            
            # Get interest over time for startup keywords
            interest_data = {}
            try:
                interest_data = self.trends_client.get_interest_over_time(startup_keywords)
            except Exception as e:
                logger.warning(f"Could not get interest over time data: {e}")
            
            google_data = {
                'trending_searches': trending_searches[:50] if trending_searches else [],
                'startup_keywords': startup_keywords,
                'interest_data': interest_data,
                'collected_at': datetime.now().isoformat()
            }
            
            logger.info(f"Collected {len(google_data['trending_searches'])} trending searches")
            return google_data
            
        except Exception as e:
            logger.error(f"Error collecting Google Trends: {e}")
            return {'trending_searches': [], 'startup_keywords': [], 'interest_data': {}}
    
    def _extract_keywords_from_sources(self, reddit_data: List[Dict], google_data: Dict) -> List[Dict[str, Any]]:
        """Extract and normalize keywords from all sources"""
        keyword_mentions = Counter()
        keyword_sources = {}
        keyword_contexts = {}
        
        # Extract from Reddit titles and content
        for post in reddit_data:
            text = f"{post['title']} {post['content']}".lower()
            keywords = self._extract_keywords_from_text(text)
            
            for keyword in keywords:
                keyword_mentions[keyword] += post['engagement_score']
                
                if keyword not in keyword_sources:
                    keyword_sources[keyword] = []
                keyword_sources[keyword].append('reddit')
                
                if keyword not in keyword_contexts:
                    keyword_contexts[keyword] = []
                keyword_contexts[keyword].append({
                    'title': post['title'],
                    'score': post['score'],
                    'subreddit': post['subreddit']
                })
        
        # Extract from Google Trends
        for search_term in google_data.get('trending_searches', []):
            keywords = self._extract_keywords_from_text(search_term.lower())
            for keyword in keywords:
                keyword_mentions[keyword] += 10  # Base score for trending searches
                
                if keyword not in keyword_sources:
                    keyword_sources[keyword] = []
                if 'google_trends' not in keyword_sources[keyword]:
                    keyword_sources[keyword].append('google_trends')
        
        # Convert to structured format
        extracted_keywords = []
        for keyword, score in keyword_mentions.most_common(100):  # Top 100 keywords
            extracted_keywords.append({
                'keyword': keyword,
                'raw_score': score,
                'sources': keyword_sources.get(keyword, []),
                'contexts': keyword_contexts.get(keyword, [])[:3],  # Top 3 contexts
                'category': self._categorize_keyword(keyword)
            })
        
        return extracted_keywords
    
    def _extract_keywords_from_text(self, text: str) -> Set[str]:
        """Extract meaningful keywords from text"""
        # Remove URLs, special characters, and normalize
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Split into potential keywords
        words = text.split()
        keywords = set()
        
        # Single words (filter out common words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'am', 'if', 'when', 'where', 'why', 'how', 'what', 'who', 'which', 'than', 'so', 'very', 'just', 'now', 'then', 'here', 'there', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'once', 'during', 'before', 'after', 'above', 'below', 'from', 'into', 'through', 'between', 'same', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'only', 'own', 'about', 'get', 'make', 'go', 'know', 'take', 'see', 'come', 'think', 'look', 'want', 'give', 'use', 'find', 'tell', 'ask', 'work', 'seem', 'feel', 'try', 'leave', 'call'}
        
        for word in words:
            if len(word) >= 3 and word.lower() not in stop_words and word.isalpha():
                keywords.add(word.lower())
        
        # Bigrams (two-word combinations)
        for i in range(len(words) - 1):
            if len(words[i]) >= 3 and len(words[i+1]) >= 3:
                bigram = f"{words[i].lower()} {words[i+1].lower()}"
                if not any(stop_word in bigram for stop_word in ['the ', ' the', 'and ', ' and']):
                    keywords.add(bigram)
        
        # Filter for business/tech relevant keywords
        relevant_keywords = set()
        business_indicators = ['app', 'platform', 'tool', 'service', 'software', 'system', 'solution', 'product', 'startup', 'business', 'market', 'user', 'customer', 'data', 'digital', 'online', 'mobile', 'web', 'api', 'saas', 'ai', 'automation', 'analytics', 'growth', 'revenue', 'monetization', 'subscription', 'freemium']
        
        for keyword in keywords:
            # Include if it contains business indicators or is in our category keywords
            if (any(indicator in keyword for indicator in business_indicators) or 
                any(keyword in cat_keywords for cat_keywords in self.category_keywords.values())):
                relevant_keywords.add(keyword)
        
        return relevant_keywords
    
    def _categorize_keyword(self, keyword: str) -> str:
        """Categorize keyword into predefined categories"""
        keyword_lower = keyword.lower()
        
        for category, keywords in self.category_keywords.items():
            if any(cat_keyword in keyword_lower for cat_keyword in keywords):
                return category
        
        return 'general'
    
    def _score_and_rank_trends(self, keywords: List[Dict], reddit_data: List[Dict], google_data: Dict) -> List[Dict[str, Any]]:
        """Calculate comprehensive scores and rank trends"""
        scored_trends = []
        
        for keyword_data in keywords:
            keyword = keyword_data['keyword']
            base_score = keyword_data['raw_score']
            sources = keyword_data['sources']
            category = keyword_data['category']
            
            # Calculate comprehensive score
            score = base_score
            
            # Source diversity bonus
            source_bonus = len(sources) * 10
            score += source_bonus
            
            # Google Trends bonus
            if 'google_trends' in sources:
                score += 25
            
            # Reddit engagement bonus
            if 'reddit' in sources:
                reddit_engagement = sum(
                    ctx['score'] for ctx in keyword_data['contexts'] 
                    if isinstance(ctx, dict) and 'score' in ctx
                )
                score += reddit_engagement * 0.1
            
            # Category relevance bonus
            category_bonuses = {
                'technology': 20,
                'business': 18,
                'productivity': 15,
                'finance': 12,
                'health': 10,
                'education': 8,
                'entertainment': 5,
                'lifestyle': 3
            }
            score += category_bonuses.get(category, 0)
            
            # Recency bonus
            recent_mentions = sum(
                1 for ctx in keyword_data['contexts']
                if isinstance(ctx, dict) and ctx.get('score', 0) > 100
            )
            score += recent_mentions * 5
            
            scored_trends.append({
                'keyword': keyword,
                'score': round(score, 1),
                'category': category,
                'data_sources': sources,
                'contexts': keyword_data['contexts'][:2],  # Top 2 contexts
                'source_breakdown': {
                    'reddit_mentions': len([s for s in sources if s == 'reddit']),
                    'google_trends': 'google_trends' in sources,
                    'base_score': base_score,
                    'bonus_points': round(score - base_score, 1)
                }
            })
        
        # Sort by score and return
        return sorted(scored_trends, key=lambda x: x['score'], reverse=True)
    
    def _enrich_with_images(self, trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add related images from Unsplash to top trends"""
        enriched_trends = []
        
        for trend in trends:
            keyword = trend['keyword']
            
            try:
                # Search for related images
                images = self.unsplash_client.search_photos(keyword, per_page=3)
                
                image_urls = []
                for img in images[:2]:  # Top 2 images
                    image_urls.append({
                        'url': img['url'],
                        'thumb_url': img['thumb_url'],
                        'description': img['description'],
                        'photographer': img['photographer'],
                        'likes': img['likes']
                    })
                
                trend['related_images'] = image_urls
                
            except Exception as e:
                logger.warning(f"Could not fetch images for '{keyword}': {e}")
                trend['related_images'] = []
            
            enriched_trends.append(trend)
        
        return enriched_trends
    
    def _calculate_engagement_score(self, post: Dict[str, Any]) -> float:
        """Calculate engagement score for a Reddit post"""
        score = post.get('score', 0)
        comments = post.get('comments', 0)
        
        # Base engagement score
        engagement = score + (comments * 2)
        
        # Recency bonus (posts from last 24 hours)
        created_time = post.get('created_utc', 0)
        if created_time > (time.time() - 86400):  # 24 hours
            engagement *= 1.5
        
        # Comment-to-score ratio bonus (indicates discussion)
        if score > 0:
            comment_ratio = comments / score
            if comment_ratio > 0.2:  # High discussion ratio
                engagement *= 1.2
        
        return engagement
    
    def get_trends_by_category(self, category: str, limit: int = 5) -> Dict[str, Any]:
        """Get trends filtered by specific category"""
        if not self.enabled:
            return {"error": "Trend Collector agent is disabled"}
        
        try:
            all_trends = self.collect_top_trends(limit=50)
            
            if 'error' in all_trends:
                return all_trends
            
            category_trends = [
                trend for trend in all_trends['trends']
                if trend['category'] == category
            ][:limit]
            
            return {
                'category': category,
                'trends': category_trends,
                'total_found': len(category_trends),
                'collected_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting trends by category: {e}")
            return {"error": str(e)}
    
    def get_trending_keywords_only(self, limit: int = 20) -> List[str]:
        """Get just the trending keywords as a simple list"""
        try:
            trends_data = self.collect_top_trends(limit=limit)
            
            if 'error' in trends_data:
                return []
            
            return [trend['keyword'] for trend in trends_data['trends']]
            
        except Exception as e:
            logger.error(f"Error getting trending keywords: {e}")
            return []

# Global instance
trend_collector = TrendCollector()