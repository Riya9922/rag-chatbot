import requests
from bs4 import BeautifulSoup
import json
import time
import schedule
from datetime import datetime
import os

# Configuration
FUND_URLS = [
    "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth"
]

DATA_DIR = "data/raw"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def scrape_fund_data(url):
    print(f"Scraping: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"Failed to fetch {url}. Status: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Groww specific extraction (Placeholder logic - needs verification of actual DOM)
        # Note: Groww might be a SPA, if this fails we might need Playwright.
        
        data = {
            "url": url,
            "scraped_at": datetime.now().isoformat(),
            "fund_name": soup.title.text.split(" - ")[0] if soup.title else "Unknown",
            "raw_text": soup.get_text(separator=' ', strip=True) # Fallback: get all text for RAG
        }
        
        # Attempting to find specific values like Expense Ratio if they exist in text
        # Real-world extraction would use specific CSS selectors
        return data
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def run_scraping_job():
    print(f"Starting scraping job at {datetime.now()}")
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    all_data = []
    for url in FUND_URLS:
        fund_data = scrape_fund_data(url)
        if fund_data:
            all_data.append(fund_data)
            # Save individual fund data
            filename = url.split('/')[-1] + ".json"
            with open(os.path.join(DATA_DIR, filename), "w") as f:
                json.dump(fund_data, f, indent=4)
        time.sleep(2) # Politeness
    
    print(f"Job completed. Scraped {len(all_data)} funds.")

if __name__ == "__main__":
    import sys
    
    # Run once
    run_scraping_job()
    
    # If not running in one-off mode, start the scheduler
    if "--once" not in sys.argv:
        # Schedule for 9:15 AM
        schedule.every().day.at("09:15").do(run_scraping_job)
        
        print("Scheduler started. Waiting for 09:15 AM...")
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        print("One-off job completed.")
