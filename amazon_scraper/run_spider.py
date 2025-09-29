from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from amazon_scraper.spiders.amazon_spider import AmazonSpider
import os

def run_spider(search_term, min_price=None, max_price=None, max_pages=5):
    # Set the working directory to where the scrapy project is
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Get the project settings
    settings = get_project_settings()
    
    # Create and configure the crawler process
    process = CrawlerProcess(settings)
    
    # Start the spider
    process.crawl(
        AmazonSpider,
        search_term=search_term,
        min_price=min_price,
        max_price=max_price,
        max_pages=max_pages
    )
    
    # Run the spider
    process.start()

if __name__ == "__main__":
    # Example usage
    run_spider(
        search_term="laptop",
        min_price="30000",
        max_price="80000",
        max_pages=3
    )
