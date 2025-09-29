import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider
import json
import re

class AmazonSpider(CrawlSpider):
    name = 'amazon'
    allowed_domains = ['amazon.in']
    
    # Custom settings for the spider
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 2,  # Limit concurrent requests
        'DOWNLOAD_DELAY': 2,  # Add delay between requests
        'COOKIES_ENABLED': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'FEEDS': {
            'products.json': {
                'format': 'json',
                'encoding': 'utf8',
                'indent': 2,
                'overwrite': True,
            },
        },
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
            'scrapy_proxy_pool.middlewares.ProxyPoolMiddleware': 610,
            'scrapy_proxy_pool.middlewares.BanDetectionMiddleware': 620,
        }
    }

    def __init__(self, search_term=None, min_price=None, max_price=None, max_pages=5, *args, **kwargs):
        super(AmazonSpider, self).__init__(*args, **kwargs)
        self.search_term = search_term.replace(' ', '+')
        self.min_price = min_price
        self.max_price = max_price
        self.max_pages = int(max_pages)
        self.current_page = 1
        
        # Construct the start URL
        base_url = f'https://www.amazon.in/s?k={self.search_term}'
        if min_price and max_price:
            base_url += f'&rh=p_36%3A{min_price}00-{max_price}00'
        self.start_urls = [base_url]

    def extract_price(self, response):
        price = None
        price_whole = response.css('span.a-price-whole::text').get()
        price_fraction = response.css('span.a-price-fraction::text').get()
        
        if price_whole:
            price = price_whole.strip().replace(',', '')
            if price_fraction:
                price = float(f"{price}.{price_fraction}")
            else:
                price = float(price)
        return price

    def extract_weight(self, title):
        if not title:
            return 'N/A'
        match = re.search(r'(\d+(?:\.\d+)?)\s*kg', title, re.IGNORECASE)
        if match:
            return match.group(1) + 'kg'
        return 'N/A'

    def parse_start_url(self, response):
        # Check for captcha/blocking
        if 'Robot Check' in response.text or 'Sorry' in response.text:
            raise CloseSpider('Detected anti-bot page')

        # Extract product links from search results
        products = response.css('div[data-component-type="s-search-result"]')
        
        for product in products:
            product_url = product.css('h2 a::attr(href)').get()
            if product_url and '/dp/' in product_url:
                yield response.follow(
                    product_url,
                    callback=self.parse_product,
                    cb_kwargs={'search_page_url': response.url}
                )

        # Handle pagination
        if self.current_page < self.max_pages:
            next_page = response.css('a.s-pagination-next::attr(href)').get()
            if next_page:
                self.current_page += 1
                yield response.follow(next_page, callback=self.parse_start_url)

    def parse_product(self, response, search_page_url):
        # Check for anti-bot detection
        if 'Robot Check' in response.text:
            raise CloseSpider('Detected anti-bot page')

        title = response.css('#productTitle::text').get()
        if title:
            title = title.strip()
        
        price = self.extract_price(response)
        seller = response.css('#sellerProfile span::text').get()
        if not seller:
            seller = response.css('#merchant-info a::text').get()
        if not seller:
            seller = 'Amazon'

        # Only yield if we have at least title and price
        if title and price:
            yield {
                'product_name': title,
                'current_price': price,
                'seller': seller.strip() if seller else 'Unknown',
                'weight': self.extract_weight(title),
                'product_url': response.url,
                'search_url': search_page_url
            }
