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
    options = webdriver.ChromeOptions()
    
    # Use a more common user agent
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
    
    # Add common browser features
    options.add_argument('--enable-javascript')
    options.add_argument('--lang=en-IN,en-US;q=0.9,en;q=0.8')
    
    # Add common window properties
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Add privacy features that regular browsers might have
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    
    # Add experimental features
    options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Add common preferences
    prefs = {
        'profile.default_content_settings.popups': 0,
        'profile.default_content_setting_values.notifications': 2,
        'profile.password_manager_enabled': False,
        'profile.managed_default_content_settings.images': 2,  # Don't load images
        'disk-cache-size': 4096,
        'profile.default_content_setting_values.cookies': 1  # Allow cookies
    }
    options.add_experimental_option('prefs', prefs)
    
    return options

def set_ignore_certificate_error(options):
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--allow-insecure-localhost')

def set_browser_as_incognito(options):
    # Additional stealth settings
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-web-security')
    
    # Remove navigator.webdriver flag
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Add window properties
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--force-device-scale-factor=1')