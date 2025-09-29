import schedule
import time
from tracker import AmazonAPI, GenerateReport
from amazon_config import FILTERS, BASE_URL, CURRENCY, NAME

def job():
    print("Running weekly tracker...")
    amazon = AmazonAPI(NAME, FILTERS, BASE_URL, CURRENCY)
    data = amazon.run()
    GenerateReport(NAME, FILTERS, BASE_URL, CURRENCY, data)
    print("Tracker completed.")

# Schedule to run every week
schedule.every().week.do(job)

# Run immediately for testing
job()

# Keep running
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute