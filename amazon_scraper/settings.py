"""
Scrapy settings for amazon_scraper project
"""

BOT_NAME = 'amazon_scraper'

SPIDER_MODULES = ['amazon_scraper.spiders']
NEWSPIDER_MODULE = 'amazon_scraper.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performing at the same time
CONCURRENT_REQUESTS = 2

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 2

# Enable or disable cookies
COOKIES_ENABLED = True

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
    'scrapy_proxy_pool.middlewares.ProxyPoolMiddleware': 610,
    'scrapy_proxy_pool.middlewares.BanDetectionMiddleware': 620,
}

# Configure proxy settings
PROXY_POOL_ENABLED = True
PROXY_POOL_BAN_POLICY = 'amazon_scraper.policy.BanDetectionPolicy'

# Configure retry settings
RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404, 408]

# Configure item pipelines
ITEM_PIPELINES = {
    'amazon_scraper.pipelines.AmazonScraperPipeline': 300,
}

# Enable and configure HTTP caching
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
