import json
import csv
import os
from amazon_config import DIRECTORY, NAME

def json_to_csv():
    json_file = f'{DIRECTORY}/{NAME}.json'
    if not os.path.exists(json_file):
        print("JSON file not found")
        return

    with open(json_file, 'r') as f:
        temp = json.load(f)

    if 'reports' in temp:
        data = temp
    else:
        # Old format
        data = {'reports': [temp]}

    reports = data.get('reports', [])
    products = reports[-1].get('products', []) if reports else []
    if not products:
        print("No products in JSON")
        return

    csv_file = f'{DIRECTORY}/{NAME}.csv'
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=products[0].keys(), delimiter='|')
        writer.writeheader()
        writer.writerows(products)

    print(f"CSV generated: {csv_file}")

if __name__ == "__main__":
    json_to_csv()