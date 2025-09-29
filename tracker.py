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
        options = get_chrome_options()
        set_ignore_certificate_error(options)
        set_browser_as_incognito(options)
        self.driver = get_chrome_driver(options)

        self.currency = currency
        self.price_filter = f"&low-price={filters['min']}&high-price={filters['max']}"

    def run(self):
        print('Starting tracker....')
        print(f'Looking for {self.search_term}....')
        links = self.get_products_links()
        if not links:
            print("Stopping tracker....")
            return
        print(f"Got {len(links)} links to products...")
        print("Getting info about products...")
        products = self.get_products_info(links)
        print(f"Got info about {len(products)} products...")
        self.driver.quit()
        return products

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
        print(f"{index+1} Product ID: {asin} - getting data...")
        product_short_url = self.shorten_url(asin)
        print(product_short_url)
        self.driver.get(f'{product_short_url}?language=en_IN')
        time.sleep(5)
        title = self.get_title()
        print(f"Title: {title}")
        seller = self.get_seller()
        print(f"Seller: {seller}")
        price = self.get_price()
        print(f"Price: {price}")
        if title and seller and price:
            # if seller not in ALLOWED_SELLERS:
            #     return None
            product_info = {
                'product_name': title,
                'type_of_product': 'Pet Food',
                'weight': extract_weight(title),
                'current_price': price,
                'pet': extract_pet(title),
                'seller': seller
            }
            return product_info
        return None

    def get_title(self):
        try:
            return self.driver.find_element(By.CLASS_NAME, 'title-recipe').text
        except Exception as e:
            print(f"Error getting title by .title-recipe: {e}")
            try:
                return self.driver.find_element(By.CSS_SELECTOR, 'span#productTitle').text
            except Exception as e2:
                print(f"Error getting title by span#productTitle: {e2}")
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
            price = self.driver.find_element(By.CLASS_NAME, 'apexPriceToPay').text
            price = self.convert_price(price)
        except NoSuchElementException:
            try:
                availability = self.driver.find_element(By.ID, 'availability').text
                if 'Available' in availability or 'In Stock' in availability:
                    price = self.driver.find_element(By.CLASS_NAME, 'olp-padding-right').text
                    price = price[price.find(self.currency):]
                    price = self.convert_price(price)
            except Exception as e:
                print(e)
                print(f"Can't get price of a product - {self.driver.current_url}")
                return None
        except Exception as e:
            print(e)
            print(f"Can't get price of a product - {self.driver.current_url}")
            return None
        return price

    def convert_price(self, price):
        if self.currency in price:
            price = price.split(self.currency)[1]
        # Clean the price string
        price = price.replace(',', '').strip()
        try:
            price = price.split("\n")[0] + "." + price.split("\n")[1]
        except Exception:
            pass
        try:
            return float(price)
        except Exception:
            return None

    def get_asins(self, links):
        return [self.get_asin(link) for link in links]

    def get_asin(self, product_link):
        return product_link[product_link.find('/dp/') + 4:product_link.find('/ref')]

    def shorten_url(self, asin):
        return self.base_url + 'dp/' + asin

    def get_products_links(self):
        self.driver.get(self.base_url)
        element = self.driver.find_element(By.ID, "twotabsearchtextbox")
        element.send_keys(self.search_term)
        element.send_keys(Keys.ENTER)
        time.sleep(2)
        self.driver.get(f'{self.driver.current_url}{self.price_filter}')
        time.sleep(2)
        self.driver.save_screenshot('search_results.png')
        print("Screenshot saved: search_results.png")
        links = []
        try:
            results = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-component-type="s-search-result"] h2 a')
            links = [link.get_attribute('href') for link in results]
            print(f"Found {len(links)} product links")
            return links
        except Exception as e:
            print(f"Couldn't find any product by name {self.search_term}...")
            print(e)
            return links


if __name__ == "__main__":
    amazon = AmazonAPI(NAME, FILTERS, BASE_URL, CURRENCY)
    data = amazon.run()
    GenerateReport(NAME, FILTERS, BASE_URL, CURRENCY, data)
