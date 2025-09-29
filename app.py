from flask import Flask, request, render_template, send_from_directory, jsonify
import webbrowser
import sqlite3
import threading
import time
import random
from datetime import datetime
from tracker import AmazonAPI
import amazon_config

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('products_new.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY, product_name TEXT, type_of_product TEXT, weight TEXT, current_price TEXT, pet TEXT, seller TEXT, date TEXT)''')
    conn.commit()
    conn.close()

def save_products(products, date):
    conn = sqlite3.connect('products_new.db')
    c = conn.cursor()
    for product in products:
        c.execute("INSERT INTO products (product_name, type_of_product, weight, current_price, pet, seller, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (product.get('product_name'), product.get('type_of_product'), product.get('weight'), product.get('current_price'), product.get('pet'), product.get('seller'), date))
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('form.html')

def scrape_with_selenium(name, min_price, max_price):
    """Try scraping with Selenium first"""
    amazon = AmazonAPI(name, {'min': min_price, 'max': max_price}, amazon_config.BASE_URL, amazon_config.CURRENCY)
    return amazon.run()

def scrape_with_scrapy(name, min_price, max_price):
    """Fall back to Scrapy if Selenium fails"""
    from amazon_scraper.run_spider import run_spider
    try:
        run_spider(
            search_term=name,
            min_price=min_price,
            max_price=max_price,
            max_pages=5
        )
        # Read the results from the JSON file
        with open('latest_data.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Scrapy scraping failed: {e}")
        return None

@app.route('/run', methods=['POST'])
def run():
    name = request.form['name'].replace(' ', '_')
    min_price = request.form['min']
    max_price = request.form['max']
    amazon_config.NAME = name
    amazon_config.MIN_PRICE = min_price
    amazon_config.MAX_PRICE = max_price
    amazon_config.FILTERS = {'min': min_price, 'max': max_price}
    
    print("Starting data fetch...")
    data = None
    
    # Try Selenium first
    print("Attempting to scrape with Selenium...")
    max_attempts = 2
    for attempt in range(max_attempts):
        try:
            data = scrape_with_selenium(name, min_price, max_price)
            if data:
                print("Successfully scraped with Selenium")
                break
        except Exception as e:
            print(f"Selenium attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_attempts - 1:
                time.sleep(random.uniform(2, 4))
    
    # If Selenium failed, try Scrapy
    if not data:
        print("Selenium failed, attempting to scrape with Scrapy...")
        try:
            data = scrape_with_scrapy(name, min_price, max_price)
            if data:
                print("Successfully scraped with Scrapy")
        except Exception as e:
            print(f"Scrapy scraping failed: {str(e)}")
    
    if data is None:
        data = []
        print("All scraping attempts failed.")
    print(f"Data fetch complete. Scraped {len(data)} products")
    # Always save to JSON file for display
    import json
    print(f"Saving data to JSON: {data}")
    with open('latest_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("JSON file saved")
    if data:
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        save_products(data, date)
        print("Data saved to SQLite database and JSON file")
    else:
        print("No products found to save")
    return render_template('data.html')

@app.route('/api/products')
def get_products():
    conn = sqlite3.connect('products_new.db')
    c = conn.cursor()
    c.execute("SELECT product_name, type_of_product, weight, current_price, pet, seller FROM products ORDER BY id DESC LIMIT 100")
    rows = c.fetchall()
    conn.close()
    products = [dict(zip(['product_name', 'type_of_product', 'weight', 'current_price', 'pet', 'seller'], row)) for row in rows]
    return jsonify(products)

@app.route('/status')
def status():
    try:
        conn = sqlite3.connect('products_new.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM products")
        count = c.fetchone()[0]
        conn.close()
        return f"""
        <h1>Database Status</h1>
        <p style="color: green;">✅ SQLite database is active</p>
        <p>Total products stored: {count}</p>
        <a href="/">Back to form</a> | <a href="/debug">View debug data</a>
        """
    except Exception as e:
        return f"""
        <h1>Database Status</h1>
        <p style="color: red;">❌ Database error: {e}</p>
        <p>SQLite may not be available. Please ensure Python sqlite3 module is installed.</p>
        <a href="/">Back to form</a>
        """

@app.route('/debug')
def debug():
    try:
        conn = sqlite3.connect('products_new.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM products")
        count = c.fetchone()[0]
        c.execute("SELECT * FROM products ORDER BY id DESC LIMIT 10")
        rows = c.fetchall()
        conn.close()
        return f"""
        <h1>Debug Info</h1>
        <p>Total products in database: {count}</p>
        <h2>Latest 10 products:</h2>
        <pre>{rows}</pre>
        <a href="/">Back to form</a>
        """
    except Exception as e:
        return f"""
        <h1>Debug Info</h1>
        <p style="color: red;">Database error: {e}</p>
        <a href="/">Back to form</a>
        """

@app.route('/data.json')
def data_json():
    try:
        with open('latest_data.json', 'r') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'application/json'}
    except FileNotFoundError:
        return '[]', 200, {'Content-Type': 'application/json'}

@app.route('/static/<path:filename>')
def static_file(filename):
    return send_from_directory('reports', filename)

if __name__ == '__main__':
    print("Starting Flask app on http://127.0.0.1:5000")
    print("Open your browser and go to the URL above")
    app.run(debug=True, port=5000)