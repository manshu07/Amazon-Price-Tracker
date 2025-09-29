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
CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1
CONCURRENT_REQUESTS_PER_IP = 1

# Configure delays and randomization
DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_TIMEOUT = 15

# Enable and configure cookies
COOKIES_ENABLED = True
COOKIES_DEBUG = False

# Add custom headers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'amazon_scraper.middlewares.CustomRetryMiddleware': 550,
    'amazon_scraper.middlewares.CustomUserAgentMiddleware': 400,
    'amazon_scraper.middlewares.RotateHeadersMiddleware': 410,
    'scrapy_proxy_pool.middlewares.ProxyPoolMiddleware': 610,
    'scrapy_proxy_pool.middlewares.BanDetectionMiddleware': 620,
}

# Configure proxy settings
PROXY_POOL_ENABLED = True
PROXY_POOL_BAN_POLICY = 'amazon_scraper.policy.BanDetectionPolicy'

# Custom proxy settings
CUSTOM_PROXY_ENABLED = True
CUSTOM_PROXY_FILE = 'proxies.json'
CUSTOM_PROXY_UPDATE_INTERVAL = 3600  # 1 hour in seconds

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
