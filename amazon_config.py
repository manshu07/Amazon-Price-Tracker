from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

DIRECTORY = 'reports'
NAME = 'book'
CURRENCY = '₹'
MIN_PRICE = '200'
MAX_PRICE = '10000'
FILTERS = {
    'min' : MIN_PRICE,
    'max' : MAX_PRICE
}
BASE_URL = 'https://www.amazon.in/'
ALLOWED_SELLERS = ['Kennel Kitchen', 'Purina', 'Pedigree', 'Royal Canin', 'Drools', 'Whiskas', 'Purepet', 'Farmina', 'Chip chops']


def get_chrome_driver(options):
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def get_chrome_options():
    return webdriver.ChromeOptions()

def set_ignore_certificate_error(options):
    options.add_argument('--ignore-certificate-errors')

def set_browser_as_incognito(options):
    options.add_argument('--incognito')
    # options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')