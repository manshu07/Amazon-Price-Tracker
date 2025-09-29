"""
Proxy configuration and management
"""
import requests
import random
import json
from datetime import datetime, timedelta

class ProxyManager:
    def __init__(self, proxy_file='proxies.json'):
        self.proxy_file = proxy_file
        self.proxies = []
        self.last_update = None
        self.update_interval = timedelta(hours=1)
        self.load_proxies()
    
    def load_proxies(self):
        """Load proxies from file or initialize empty list"""
        try:
            with open(self.proxy_file, 'r') as f:
                data = json.load(f)
                self.proxies = data.get('proxies', [])
                last_update = data.get('last_update')
                if last_update:
                    self.last_update = datetime.fromisoformat(last_update)
        except (FileNotFoundError, json.JSONDecodeError):
            self.proxies = []
            self.last_update = None
    
    def save_proxies(self):
        """Save proxies to file"""
        with open(self.proxy_file, 'w') as f:
            json.dump({
                'proxies': self.proxies,
                'last_update': datetime.now().isoformat()
            }, f, indent=2)
    
    def update_proxies(self):
        """Update proxy list from various sources"""
        now = datetime.now()
        if (self.last_update and 
            now - self.last_update < self.update_interval and 
            len(self.proxies) > 0):
            return
        
        new_proxies = []
        
        # Free proxy lists
        sources = [
            'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt'
        ]
        
        for source in sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    proxies = response.text.strip().split('\n')
                    new_proxies.extend(proxies)
            except:
                continue
        
        # Filter and verify proxies
        verified_proxies = []
        for proxy in new_proxies:
            try:
                proxy = proxy.strip()
                if not proxy:
                    continue
                    
                # Test proxy with timeout
                test_url = 'https://www.amazon.in'
                proxy_dict = {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}'
                }
                response = requests.get(
                    test_url,
                    proxies=proxy_dict,
                    timeout=5
                )
                if response.status_code == 200:
                    verified_proxies.append(proxy)
            except:
                continue
        
        if verified_proxies:
            self.proxies = verified_proxies
            self.last_update = now
            self.save_proxies()
    
    def get_proxy(self):
        """Get a random working proxy"""
        self.update_proxies()
        return random.choice(self.proxies) if self.proxies else None

# Global proxy manager instance
proxy_manager = ProxyManager()
