import logging
from celery import shared_task

from reviews.scrapers.factory import ScraperFactory
from restaurants.models import Restaurant
from reviews.models import Review

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60, ignore_result=True, queue='scraping')
def scrape_reviews(self, restaurant_id, source_slug=Review.Source.GOOGLE, limit=5):
    try:
        restaurant = Restaurant.objects.get(id=restaurant_id)
        
        scraper = ScraperFactory.create(source_slug)
        count = scraper.scrape_and_save(restaurant=restaurant, limit=limit)
        
        logger.info(f"Scraped {count} reviews from {source_slug} for {restaurant.name}")
    except ValueError as e:
        logger.error(f"Unknown source: {e}")
    except Restaurant.DoesNotExist:
        logger.warning(f"Restaurant not found: {restaurant_id}")
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)