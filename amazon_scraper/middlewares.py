"""
Custom middleware for handling anti-bot detection
"""
import random
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

class CustomRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        if response.status in [403, 503]:
            spider.logger.warning(f'Retrying {request} due to {response.status}')
            return self._retry(request, response.status, spider) or response
        return response

class RotateHeadersMiddleware:
    """Rotate headers and add random viewport sizes"""
    
    def __init__(self):
        self.viewports = [
            '1920x1080', '1366x768', '1536x864', '1440x900',
            '1280x720', '1600x900', '1024x768', '1280x800'
        ]
        
    def process_request(self, request, spider):
        # Add random viewport
        viewport = random.choice(self.viewports)
        width, height = viewport.split('x')
        
        # Add random headers
        request.headers.update({
            'Viewport-Width': width,
            'Viewport-Height': height,
            'Device-Memory': f'{random.choice([2,4,8,16])}',
            'DPR': f'{random.choice([1,2,3])}',
            'RTT': f'{random.randint(50,150)}',
            'Downlink': f'{random.choice([5,10,15,20])}',
            'ECT': random.choice(['4g','3g']),
        })
        
        return None

class CustomUserAgentMiddleware(UserAgentMiddleware):
    """Rotate between different browser profiles"""
    
    def __init__(self):
        super().__init__()
        self.user_agents = [
            # Windows Chrome
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            # Windows Firefox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            # Windows Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            # macOS Safari
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            # macOS Chrome
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        ]
    
    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agents)
        request.headers['User-Agent'] = user_agent
