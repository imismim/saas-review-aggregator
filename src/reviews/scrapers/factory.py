
class ScraperFactory:
    _scrapers = {}
    
    @classmethod
    def register(cls, source_slug):

        def decorator(scraper_class):
            cls._scrapers[source_slug] = scraper_class
            return scraper_class
        return decorator
    
    @classmethod
    def create(cls, source_slug):
        scraper_class = cls._scrapers.get(source_slug)
        if not scraper_class:
            raise ValueError(f"Unknown source: {source_slug}")
        return scraper_class()
    
    @classmethod
    def available_sources(cls):
        return list(cls._scrapers.keys())