from datetime import datetime, timezone

from helpers.google_seach import get_gmaps_client
from ..models import Review
from .base import BaseScraper
from .factory import ScraperFactory

import logging

logger = logging.getLogger(__name__)

@ScraperFactory.register('google')
class GoogleScraper(BaseScraper):
    source = 'google'
    
    def scrape(self, restaurant):
        if not restaurant.place_id:
            logger.warning(f"No google_place_id for {restaurant.name}")
            return []
        
        gmaps = get_gmaps_client()
        result = gmaps.place(
            place_id=restaurant.place_id,
            fields=['reviews', 'rating', 'user_ratings_total']
        ).get('result', {})
        
        reviews = []
        for r in result.get('reviews', []):
            reviews.append({
                'external_id': r.get('author_url'),
                'author': r.get('author_name'),
                'rating': r.get('rating'),
                'text': r.get('text'),
                'review_date': datetime.fromtimestamp(r.get('time'), tz=timezone.utc),
            })
        
        return reviews
    
    def scrape_and_save(self, restaurant):
        reviews = self.scrape(restaurant)
        return self.save_reviews(reviews, restaurant)