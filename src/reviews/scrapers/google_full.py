from serpapi import GoogleSearch
from django.conf import settings
from .base import BaseScraper
from .factory import ScraperFactory
from datetime import datetime

import logging

logger = logging.getLogger(__name__)

@ScraperFactory.register('google_full')
class GoogleFullScraper(BaseScraper):
    source = 'google'
    
    def scrape(self, restaurant, limit=5):
        if not restaurant.place_id:
            logger.warning(f"No google_place_id for {restaurant.name}")
            return []
        
        if not settings.SERPAPI_KEY:
            logger.error("SERPAPI_KEY not set")
            return []
        
        all_reviews = []
        params = {
            'engine': 'google_maps_reviews',
            'place_id': restaurant.place_id,
            'api_key': settings.SERPAPI_KEY,
            'hl': 'en',
            'sort_by': '2',  # newest first
        }
        
        while len(all_reviews) < limit:
            search = GoogleSearch(params)
            results = search.get_dict()
            
            for r in results.get('reviews', []):
                iso_date = r.get('iso_date')
                all_reviews.append({
                    'external_id': r.get('user', {}).get('link'),
                    'author': r.get('user', {}).get('name'),
                    'rating': r.get('rating'),
                    'text': r.get('snippet'),
                    'review_date': datetime.fromisoformat(iso_date.replace('Z', '+00:00')) if iso_date else None,
                })
            
            next_token = results.get('serpapi_pagination', {}).get('next_page_token')
            if not next_token:
                break
            params['next_page_token'] = next_token
        
        logger.info(f"Scraped {len(all_reviews)} reviews for {restaurant.name}")
        return all_reviews[:limit]
    
    def scrape_and_save(self, restaurant, limit=5):
        reviews = self.scrape(restaurant=restaurant, limit=limit)
        return self.save_reviews(reviews, restaurant)