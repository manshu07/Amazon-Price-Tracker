from scrapy import signals
from itemadapter import is_item, ItemAdapter
import json

class AmazonScraperPipeline:
    def __init__(self):
        self.items = []

    def process_item(self, item, spider):
        self.items.append(item)
        return item

    def close_spider(self, spider):
        # Save to JSON file
        with open('latest_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)
        
        # Save to SQLite if available
        try:
            import sqlite3
            from datetime import datetime
            
            conn = sqlite3.connect('products_new.db')
            c = conn.cursor()
            
            # Create table if it doesn't exist
            c.execute('''CREATE TABLE IF NOT EXISTS products
                         (id INTEGER PRIMARY KEY, product_name TEXT, type_of_product TEXT, 
                          weight TEXT, current_price TEXT, pet TEXT, seller TEXT, date TEXT)''')
            
            # Insert items
            date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            for item in self.items:
                c.execute("""
                    INSERT INTO products 
                    (product_name, type_of_product, weight, current_price, pet, seller, date) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.get('product_name'),
                    'Generic',  # type_of_product
                    item.get('weight', 'N/A'),
                    str(item.get('current_price')),
                    'N/A',  # pet
                    item.get('seller', 'Unknown'),
                    date
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error saving to database: {e}")
