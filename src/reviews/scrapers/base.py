import logging
logger = logging.getLogger(__name__)

class BaseScraper:
    source = None
    
    def scrape(self, restaurant):
        raise NotImplementedError
    
    def save_reviews(self, reviews, restaurant):
        from reviews.models import Review
        
        created_count = 0
        for review_data in reviews:
            _, created = Review.objects.get_or_create(
                restaurant=restaurant,
                source=self.source,
                external_id=review_data.get('external_id'),
                defaults=review_data
            )
            if created:
                created_count += 1
        
        logger.info(f"Saved {created_count} new reviews for {restaurant.name}")
        return created_count