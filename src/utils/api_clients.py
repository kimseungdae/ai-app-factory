import os
import requests
import praw
from typing import Dict, List, Any, Optional
from openai import OpenAI
from supabase import create_client, Client
from pytrends.request import TrendReq
from bs4 import BeautifulSoup
from unsplash.api import Api as UnsplashApi
from unsplash.auth import Auth as UnsplashAuth
import logging
from .config import config

logger = logging.getLogger(__name__)

class APIClientError(Exception):
    pass

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=config.get_api_key('openai'))
        self.model = config.get('apis.openai.model', 'gpt-3.5-turbo')
        self.max_tokens = config.get('apis.openai.max_tokens', 1000)
        self.temperature = config.get('apis.openai.temperature', 0.7)
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                temperature=kwargs.get('temperature', self.temperature)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise APIClientError(f"OpenAI API error: {e}")

class RedditClient:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=config.get_api_key('reddit_client_id'),
            client_secret=config.get_api_key('reddit_client_secret'),
            refresh_token=os.getenv('REDDIT_REFRESH_TOKEN'),
            user_agent=config.get('apis.reddit.user_agent', 'AI App Factory Bot 1.0')
        )
    
    def get_hot_posts(self, subreddit: str, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            posts = []
            for post in self.reddit.subreddit(subreddit).hot(limit=limit):
                posts.append({
                    'title': post.title,
                    'score': post.score,
                    'url': post.url,
                    'created_utc': post.created_utc,
                    'num_comments': post.num_comments,
                    'selftext': post.selftext[:500] if post.selftext else ''
                })
            return posts
        except Exception as e:
            logger.error(f"Reddit API error: {e}")
            raise APIClientError(f"Reddit API error: {e}")
    
    def search_posts(self, query: str, subreddit: str = 'all', limit: int = 10) -> List[Dict[str, Any]]:
        try:
            posts = []
            for post in self.reddit.subreddit(subreddit).search(query, limit=limit):
                posts.append({
                    'title': post.title,
                    'score': post.score,
                    'url': post.url,
                    'created_utc': post.created_utc,
                    'num_comments': post.num_comments,
                    'selftext': post.selftext[:500] if post.selftext else ''
                })
            return posts
        except Exception as e:
            logger.error(f"Reddit search error: {e}")
            raise APIClientError(f"Reddit search error: {e}")

class GoogleTrendsClient:
    def __init__(self):
        self.pytrends = TrendReq(
            hl='en-US',
            tz=360,
            timeout=config.get('apis.google_trends.timeout', 30)
        )
        self.geo = config.get('apis.google_trends.geo', 'US')
        self.timeframe = config.get('apis.google_trends.timeframe', 'today 12-m')
    
    def get_trending_searches(self, country: str = None) -> List[str]:
        try:
            trending_searches = self.pytrends.trending_searches(pn=country or self.geo)
            return trending_searches[0].tolist()
        except Exception as e:
            logger.error(f"Google Trends API error: {e}")
            raise APIClientError(f"Google Trends API error: {e}")
    
    def get_interest_over_time(self, keywords: List[str]) -> Dict[str, Any]:
        try:
            self.pytrends.build_payload(keywords, geo=self.geo, timeframe=self.timeframe)
            interest_over_time = self.pytrends.interest_over_time()
            return interest_over_time.to_dict() if not interest_over_time.empty else {}
        except Exception as e:
            logger.error(f"Google Trends interest over time error: {e}")
            raise APIClientError(f"Google Trends interest over time error: {e}")

class SupabaseClient:
    def __init__(self):
        url = config.get_api_key('supabase_url')
        key = config.get_api_key('supabase_key')
        self.client: Client = create_client(url, key)
    
    def insert_data(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = self.client.table(table).insert(data).execute()
            return result.data
        except Exception as e:
            logger.error(f"Supabase insert error: {e}")
            raise APIClientError(f"Supabase insert error: {e}")
    
    def select_data(self, table: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        try:
            query = self.client.table(table).select("*")
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Supabase select error: {e}")
            raise APIClientError(f"Supabase select error: {e}")

class WebScrapingClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_url(self, url: str) -> Dict[str, str]:
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ''
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ''
            
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text().strip() for p in paragraphs[:5]])
            
            return {
                'url': url,
                'title': title_text,
                'description': description,
                'content': content[:1000]
            }
        except Exception as e:
            logger.error(f"Web scraping error for {url}: {e}")
            raise APIClientError(f"Web scraping error: {e}")

class UnsplashClient:
    def __init__(self):
        access_key = config.get_api_key('unsplash_access_key')
        self.auth = UnsplashAuth(client_id=access_key, redirect_uri="", client_secret="")
        self.api = UnsplashApi(self.auth)
    
    def search_photos(self, query: str, per_page: int = 10) -> List[Dict[str, Any]]:
        try:
            photos = self.api.photo.search(query, per_page=per_page)
            
            results = []
            for photo in photos['results']:
                results.append({
                    'id': photo['id'],
                    'url': photo['urls']['regular'],
                    'thumb_url': photo['urls']['thumb'],
                    'description': photo.get('description', photo.get('alt_description', '')),
                    'tags': [tag['title'] for tag in photo.get('tags', [])],
                    'likes': photo.get('likes', 0),
                    'downloads': photo.get('downloads', 0),
                    'created_at': photo.get('created_at', ''),
                    'photographer': photo['user']['name']
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Unsplash API error: {e}")
            raise APIClientError(f"Unsplash API error: {e}")
    
    def get_trending_photos(self, category: str = None, per_page: int = 10) -> List[Dict[str, Any]]:
        try:
            if category:
                photos = self.api.photo.search(category, per_page=per_page, order_by="popular")
            else:
                photos = self.api.photo.list(per_page=per_page, order_by="popular")
            
            results = []
            photo_list = photos.get('results', photos) if 'results' in photos else photos
            
            for photo in photo_list:
                results.append({
                    'id': photo['id'],
                    'url': photo['urls']['regular'],
                    'thumb_url': photo['urls']['thumb'],
                    'description': photo.get('description', photo.get('alt_description', '')),
                    'tags': [tag['title'] for tag in photo.get('tags', [])],
                    'likes': photo.get('likes', 0),
                    'downloads': photo.get('downloads', 0),
                    'created_at': photo.get('created_at', ''),
                    'photographer': photo['user']['name']
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Unsplash trending photos error: {e}")
            raise APIClientError(f"Unsplash trending photos error: {e}")

class APIClientManager:
    def __init__(self):
        self.openai = OpenAIClient()
        self.reddit = RedditClient()
        self.google_trends = GoogleTrendsClient()
        self.supabase = SupabaseClient()
        self.web_scraper = WebScrapingClient()
        self.unsplash = UnsplashClient()
    
    def get_client(self, client_name: str):
        clients = {
            'openai': self.openai,
            'reddit': self.reddit,
            'google_trends': self.google_trends,
            'supabase': self.supabase,
            'web_scraper': self.web_scraper,
            'unsplash': self.unsplash
        }
        
        if client_name not in clients:
            raise ValueError(f"Unknown client: {client_name}")
        
        return clients[client_name]

api_manager = APIClientManager()