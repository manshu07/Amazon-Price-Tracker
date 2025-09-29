# Amazon(India) Price Tracker

A desktop application to track pet food prices from Amazon India with a web-based interface.

## Features
- Filter by specific pet food brands (Pedigree, Royal Canin, etc.)
- Web interface for input and results
- Searchable results table
- Historic price tracking
- CSV export
- Double-click to run (no terminal needed)

## How to Run

### Double-Click Method (Recommended)
1. Locate the `run.command` file in the project folder
2. Double-click `run.command`
3. If prompted, allow the app to run (System Preferences > Security & Privacy)
4. Your default browser will open automatically
5. Enter product name, min/max prices, and click "Start Tracking"
6. Wait for data fetching, then view results

### Manual Method
1. Open Terminal
2. Navigate to the project folder: `cd /path/to/Amazon-Price-Tracker-master`
3. Activate virtual environment: `source .venv/bin/activate`
4. Run: `python app.py`
5. Open http://127.0.0.1:5000 in your browser

## Requirements
- macOS
- Python 3.8+ (already installed)
- Internet connection for price tracking

## Files Description
- `run.command`: Double-click launcher
- `app.py`: Main Flask application
- `tracker.py`: Amazon scraping logic
- `amazon_config.py`: Configuration and settings
- `json_to_csv.py`: Export script
- `templates/`: HTML templates
- `reports/`: Generated reports and data

## Troubleshooting
- If double-click doesn't work, right-click `run.command` > Open
- Ensure Chrome browser is installed
- Check `reports/` folder for generated files
- Run `python json_to_csv.py` to export latest data to CSV

## Data Output
- JSON: `reports/{product_name}.json` (historic data)
- CSV: `reports/{product_name}.csv` (latest data)
- Web interface shows latest results with search
