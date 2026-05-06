import requests
from bs4 import BeautifulSoup
import json
import time
import schedule
from datetime import datetime
import os
import sys
import logging
from markdownify import markdownify as md
import concurrent.futures

logger = logging.getLogger(__name__)

# Configuration
FUND_URLS = [
    "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth"
]

DATA_DIR = os.path.join(os.getcwd(), "data", "raw")
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def scrape_fund_data(url):
    """
    Fetches the URL, converts the main content to Markdown, and extracts metadata.
    """
    logger.info(f"Scraping: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            logger.warning(f"HTTP {response.status_code} for {url}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Basic Metadata
        fund_name = soup.title.text.split(" - ")[0] if soup.title else "Unknown Fund"
        
        # 2. HTML to Markdown Conversion
        # We focus on the main content area if possible, or the whole body
        content_html = str(soup.find('body') or soup)
        markdown_content = md(content_html, heading_style="ATX")
        
        # 3. Extract Important Metrics from the Markdown Content
        # This is more reliable as the markdown already has the text in a predictable flow
        metrics = {
            "nav": "N/A",
            "min_sip": "N/A",
            "fund_size": "N/A",
            "expense_ratio": "N/A",
            "rating": "N/A"
        }
        
        import re
        
        # 3.1 NAV (Look for NAV: [Date] [Newlines] ₹Value)
        nav_match = re.search(r"NAV:.*?[₹|Rs\.?]\s*([\d\.,]+)", markdown_content, re.IGNORECASE | re.DOTALL)
        if nav_match: metrics["nav"] = nav_match.group(1)
        
        # 3.2 Min SIP (Look for Min. for SIP [Newline] ₹Value)
        sip_match = re.search(r"Min\.\sfor\sSIP\s*₹\s*([\d,]+)", markdown_content, re.IGNORECASE)
        if not sip_match:
            sip_match = re.search(r"Minimum\sSIP\sInvestment\sis\sset\sto\s₹\s*([\d,]+)", markdown_content, re.IGNORECASE)
        if sip_match: metrics["min_sip"] = sip_match.group(1)
        
        # 3.3 Fund Size (Look for Fund size \(AUM\)\s*₹Value)
        size_match = re.search(r"Fund\ssize\s\(AUM\)\s*₹\s*([\d,\.]+)\s*Cr", markdown_content, re.IGNORECASE)
        if not size_match:
            size_match = re.search(r"Asset\sUnder\sManagement\(AUM\)\sof\s₹\s*([\d,\.]+)\s*Cr", markdown_content, re.IGNORECASE)
        if size_match: metrics["fund_size"] = size_match.group(1) + " Cr"
        
        # 3.4 Expense Ratio (Look for Expense ratio\s*[\d\.]%)
        expense_match = re.search(r"Expense\sratio\s*([\d\.]+%?)", markdown_content, re.IGNORECASE)
        if expense_match: metrics["expense_ratio"] = expense_match.group(1)
        
        # 3.5 Rating (Look for Rating\s*[Newline]\s*Value)
        rating_match = re.search(r"Rating\s*[\n\r\s]+(\d\.?\d?)", markdown_content, re.IGNORECASE)
        if rating_match: metrics["rating"] = rating_match.group(1)
        
        # 4. Structured Data
        data = {
            "metadata": {
                "fund_name": fund_name,
                "url": url,
                "scraped_at": datetime.now().isoformat(),
                "source": "Groww.in",
                "content_type": "official_public_data",
                **metrics
            },
            "content": markdown_content
        }
        
        return data
        
    except Exception as exc:
        logger.exception(f"Exception during scraping {url}: {exc}")
        return None

def run_scraping_job():
    """
    Executes the full scraping cycle for all configured URLs using multi-threading.
    """
    logger.info(f"Starting Scraping Job — {len(FUND_URLS)} URLs queued")
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    def process_url(url):
        fund_data = scrape_fund_data(url)
        if fund_data:
            # Generate a safe filename
            safe_name = url.split('/')[-1].replace('-', '_') + ".json"
            file_path = os.path.join(DATA_DIR, safe_name)
            
            with open(file_path, "w", encoding='utf-8') as f:
                json.dump(fund_data, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Saved: {safe_name}")
            return True
        logger.warning(f"No data returned for: {url}")
        return False

    success_count = 0
    # Use ThreadPoolExecutor to scrape multiple URLs concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(process_url, FUND_URLS)
        success_count = sum(1 for r in results if r)
    
    logger.info(f"Scraping Job Completed — {success_count}/{len(FUND_URLS)} succeeded")

if __name__ == "__main__":
    # Standalone usage: configure basic logging so prints go to stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Check for CLI flags
    if "--once" in sys.argv:
        run_scraping_job()
        sys.exit(0)
    
    # Default: Run once then start scheduler
    run_scraping_job()
    
    # Schedule for 09:15 AM
    # Note: For local runs, this uses system time.
    # For GitHub Actions, we use the workflow YAML schedule.
    schedule.every().day.at("09:15").do(run_scraping_job)
    
    logger.info("Scheduler active. Waiting for next trigger at 09:15...")
    while True:
        schedule.run_pending()
        time.sleep(60)
