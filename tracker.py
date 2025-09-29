from amazon_config import (
    get_chrome_options,
    get_chrome_driver,
    set_ignore_certificate_error,
    set_browser_as_incognito,
    NAME,
    CURRENCY,
    FILTERS,
    BASE_URL,
    DIRECTORY,
    ALLOWED_SELLERS
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import json
from datetime import datetime
import time
import re
import os
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def extract_weight(title):
    match = re.search(r'(\d+(?:\.\d+)?)\s*kg', title, re.IGNORECASE)
    if match:
        return match.group(1) + 'kg'
    return 'N/A'


def extract_pet(title):
    if 'dog' in title.lower():
        return 'Dog'
    elif 'cat' in title.lower():
        return 'Cat'
    return 'N/A'


class GenerateReport:
    def __init__(self, file_name, filters, base_link, currency, data):
        self.data = data
        self.file_name = file_name
        self.filters = filters
        self.base_link = base_link
        self.currency = currency
        self.directory = DIRECTORY
        file_path = f'{DIRECTORY}/{file_name}.json'
        existing = {'reports': []}
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                temp = json.load(f)
                if 'reports' in temp:
                    existing = temp
                else:
                    # Old format, convert to new
                    existing['reports'] = [temp]
        report = {
            'title': self.file_name,
            'date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'best_item': self.get_best_item(),
            'currency': self.currency,
            'filters': self.filters,
            'base_link': self.base_link,
            'products': self.data
        }
        os.makedirs(self.directory, exist_ok=True)
        existing['reports'].append(report)
        print("Generating report...")
        with open(file_path, 'w') as file:
            json.dump(existing, file, indent=2)
        print("Report generated successfully..")

    def get_best_item(self):
        try:
            valid_products = [p for p in self.data if p.get('current_price') is not None]
            if not valid_products:
                return None
            return sorted(valid_products, key=lambda k: k['current_price'])[0]
        except Exception as e:
            print(e)
            print("Problem with sorting items")
            return None


class AmazonAPI:
    def __init__(self, search_term, filters, base_url, currency):
        self.base_url = base_url
        self.search_term = search_term
        
        # Configure Chrome options
        options = get_chrome_options()
        set_ignore_certificate_error(options)
        set_browser_as_incognito(options)
        
        self.driver = get_chrome_driver(options)
        
        # Set CDP parameters for stealth
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "platform": "Windows",
            "acceptLanguage": "en-US,en;q=0.9"
        })
        
        # Execute stealth JavaScript
        self.driver.execute_script("""
            // Overwrite the 'navigator.webdriver' property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            });
            
            // Add regular browser features
            window.chrome = {
                runtime: {}
            };
            
            // Add regular plugins array
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Add regular languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        self.currency = currency
        self.price_filter = f"&low-price={filters['min']}&high-price={filters['max']}"
        
        # Randomize delays more naturally
        self.min_delay = 3
        self.max_delay = 7
        
        # Add session cookies
        self.driver.add_cookie({
            'name': 'session-id',
            'value': str(int(time.time())),
            'domain': '.amazon.in'
        })
        
        # Initialize retry count
        self.retry_count = 0
        self.max_retries = 3

    def run(self):
        print('Starting tracker....')
        print(f'Looking for {self.search_term}....')
        
        try:
            links = self.get_products_links()
            
            if self.check_if_blocked():
                print("Access is being blocked by Amazon. Please try again later.")
                return None
                
            if not links:
                print("No product links found. Stopping tracker....")
                return None
                
            print(f"Got {len(links)} links to products...")
            print("Getting info about products...")
            
            products = []
            for i, link in enumerate(links[:5]):  # Limit to first 5 products to avoid blocking
                if self.check_if_blocked():
                    print("Access is being blocked by Amazon. Stopping further scraping.")
                    break
                    
                asin = self.get_asin(link)
                if asin:
                    product = self.get_single_product_info(asin, i)
                    if product:
                        products.append(product)
                self.random_delay()  # Add delay between product scrapes
                
            print(f"Successfully scraped {len(products)} products")
            return products
            
        except Exception as e:
            print(f"Error during scraping: {str(e)}")
            return None
            
        finally:
            self.driver.quit()

    def get_products_info(self, links):
        asins = self.get_asins(links)
        products = []
        for asin in asins:
            product = self.get_single_product_info(asin, asins.index(asin))
            if product:
                products.append(product)
        print(f"Pr: {products}")
        return products

    def get_single_product_info(self, asin, index):
        try:
            print(f"{index+1} Product ID: {asin} - getting data...")
            product_short_url = self.shorten_url(asin)
            print(f"Accessing URL: {product_short_url}")
            
            # Add cache-busting parameter and language
            full_url = f'{product_short_url}?language=en_IN&_={int(time.time())}'
            self.driver.get(full_url)
            
            # Wait for the page to load
            self.random_delay()
            
            # Wait for price element to be present
            price_wait = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.a-price, #priceblock_ourprice, #priceblock_dealprice, .price-large'))
            )
            
            title = self.get_title()
            print(f"Title: {title}")
            seller = self.get_seller()
            print(f"Seller: {seller}")
            price = self.get_price()
            print(f"Price: {price}")
            
            if title and price:  # Make seller optional as it might not always be available
                product_info = {
                    'product_name': title,
                    'type_of_product': 'Generic',  # Changed from 'Pet Food' to be more generic
                    'weight': extract_weight(title),
                    'current_price': price,
                    'pet': extract_pet(title),
                    'seller': seller if seller else 'Amazon'  # Use 'Amazon' as default seller
                }
                return product_info
            else:
                print(f"Missing required info - Title: {bool(title)}, Price: {bool(price)}")
                return None
                
        except Exception as e:
            print(f"Error getting product info: {str(e)}")
            print(f"Current URL: {self.driver.current_url}")
            return None

    def get_title(self):
        try:
            return self.driver.find_element(By.ID, 'productTitle').text.strip()
        except Exception as e:
            print(f"Error getting title: {e}")
            print(f"Can't get title of a product - {self.driver.current_url}")
            return None

    def get_seller(self):
        try:
            return self.driver.find_element(By.ID, 'bylineInfo').text
        except Exception as e:
            print(e)
            print(f"Can't get seller of a product - {self.driver.current_url}")
            return None

    def get_price(self):
        price = None
        try:
            # Try the primary price element
            price_element = self.driver.find_element(By.CSS_SELECTOR, 'span.a-price-whole')
            fraction_element = self.driver.find_element(By.CSS_SELECTOR, 'span.a-price-fraction')
            if price_element and fraction_element:
                price = f"{price_element.text}.{fraction_element.text}"
                return self.convert_price(price)
        except NoSuchElementException:
            try:
                # Try alternative price elements
                price_element = self.driver.find_element(By.CSS_SELECTOR, '[data-a-color="price"] .a-offscreen')
                if price_element:
                    price = price_element.get_attribute('innerHTML')
                    return self.convert_price(price)
            except Exception as e:
                print(f"Error getting price: {e}")
                print(f"Can't get price of a product - {self.driver.current_url}")
                return None
        except Exception as e:
            print(f"Error getting price: {e}")
            print(f"Can't get price of a product - {self.driver.current_url}")
            return None
        return price

    def convert_price(self, price):
        if not price:
            return None
        # Remove currency symbol and any other non-numeric characters except dots
        price = re.sub(r'[^0-9.]', '', price)
        try:
            return float(price)
        except (ValueError, TypeError):
            return None

    def get_asins(self, links):
        return [self.get_asin(link) for link in links]

    def get_asin(self, product_link):
        return product_link[product_link.find('/dp/') + 4:product_link.find('/ref')]

    def shorten_url(self, asin):
        return self.base_url + 'dp/' + asin

    def random_delay(self):
        time.sleep(random.uniform(self.min_delay, self.max_delay))

    def check_if_blocked(self):
        """Check if we're being blocked by Amazon"""
        blocked_indicators = [
            'Sorry, we just need to make sure you',
            'Enter the characters you see below',
            'To discuss automated access to Amazon data',
            'Bot Check',
            'Type the characters you see in this image',
            'Your browser is not accepting cookies'
        ]
        
        page_source = self.driver.page_source.lower()
        for indicator in blocked_indicators:
            if indicator.lower() in page_source:
                print(f"Access blocked by Amazon: {indicator}")
                self.driver.save_screenshot('blocked.png')
                print("Screenshot of blocked page saved as 'blocked.png'")
                return True
        return False

    def verify_page_loaded(self, timeout=10):
        """Verify that the page has loaded properly"""
        try:
            # Wait for either product title or search results to be present
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            return True
        except Exception as e:
            print(f"Page load verification failed: {str(e)}")
            return False

    def wait_for_element(self, by, value, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            print(f"Timeout waiting for element {value}: {e}")
            return None

    def get_products_links(self):
        try:
            # Load homepage with random delay
            self.driver.get(self.base_url)
            self.random_delay()
            
            # Wait for and interact with search box
            search_box = self.wait_for_element(By.ID, "twotabsearchtextbox")
            if not search_box:
                print("Could not find search box")
                return []
                
            search_box.clear()
            # Type search term with random delays between characters
            for char in self.search_term:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            self.random_delay()
            search_box.send_keys(Keys.ENTER)
            self.random_delay()
            
            # Apply price filter
            filter_url = f'{self.driver.current_url}{self.price_filter}'
            print(f"Applying price filter: {filter_url}")
            self.driver.get(filter_url)
            self.random_delay()
        except Exception as e:
            print(f"Error during search: {e}")
            return []
            self.driver.save_screenshot('search_results.png')
            print("Screenshot saved: search_results.png")
            links = []
            try:
                # Wait for search results to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-component-type="s-search-result"]'))
                )
                
                # Try multiple selector patterns that Amazon might use
                selectors = [
                    'div[data-component-type="s-search-result"] h2 a',
                    'div.s-result-item h2 a',
                    'div.sg-col-inner h2 a',
                    'div[data-component-type="s-search-result"] .a-link-normal.s-no-outline'
                ]
                
                for selector in selectors:
                    results = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if results:
                        print(f"Found results using selector: {selector}")
                        links = [link.get_attribute('href') for link in results if link.get_attribute('href')]
                        # Filter out sponsored links and non-product URLs
                        links = [link for link in links if '/dp/' in link]
                        break
                
                if links:
                    print(f"Found {len(links)} product links")
                    for link in links:
                        print(f"Product URL: {link}")
                else:
                    print("No product links found in the search results")
                return links
            except Exception as e:
                print(f"Error finding products: {str(e)}")
                print(f"Current URL: {self.driver.current_url}")
                return links
if __name__ == "__main__":
    amazon = AmazonAPI(NAME, FILTERS, BASE_URL, CURRENCY)
    data = amazon.run()
    GenerateReport(NAME, FILTERS, BASE_URL, CURRENCY, data)
