#!/usr/bin/env python3
"""
Script to search TTB COLA registry and populate TTB IDs for whiskey entries.
Uses the TTB online COLA search form to find approval IDs.
"""

import csv
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TTBColaSearcher:
    """Class to search TTB COLA registry for whiskey approvals."""
    
    BASE_URL = "https://ttbonline.gov/colasonline/publicSearchColasBasicProcess.do?action=search"
    
    def __init__(self, headless=True):
        """Initialize the searcher with a Chrome webdriver."""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(30)
        self.wait = WebDriverWait(self.driver, 10)
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()
        
    def search_product(self, product_name, start_year=2000, end_year=None):
        """
        Search for a product in the TTB COLA registry.
        
        Args:
            product_name: Name of the whiskey product
            start_year: Start year for search (default 2000)
            end_year: End year for search (default current year)
            
        Returns:
            List of dict with TTB ID, brand name, proof, approval date, etc.
        """
        if end_year is None:
            end_year = datetime.now().year
            
        logger.info(f"Searching for: {product_name} ({start_year}-{end_year})")
        
        try:
            # Load the search form
            self.driver.get(self.BASE_URL)
            time.sleep(2)
            
            # Fill in the product name
            try:
                product_input = self.wait.until(
                    EC.presence_of_element_located((By.NAME, "productName"))
                )
                product_input.clear()
                product_input.send_keys(product_name)
            except TimeoutException:
                logger.error(f"Could not find product name field")
                return []
            
            # Set date range - find the from/to date fields
            try:
                # From date
                from_month = self.driver.find_element(By.NAME, "approvalFromMonth")
                from_month.send_keys("01")
                from_day = self.driver.find_element(By.NAME, "approvalFromDay")
                from_day.send_keys("01")
                from_year = self.driver.find_element(By.NAME, "approvalFromYear")
                from_year.send_keys(str(start_year))
                
                # To date
                to_month = self.driver.find_element(By.NAME, "approvalToMonth")
                to_month.send_keys("12")
                to_day = self.driver.find_element(By.NAME, "approvalToDay")
                to_day.send_keys("31")
                to_year = self.driver.find_element(By.NAME, "approvalToYear")
                to_year.send_keys(str(end_year))
            except NoSuchElementException as e:
                logger.warning(f"Date fields might have different names: {e}")
            
            # Submit the search
            try:
                submit_button = self.driver.find_element(By.NAME, "submit")
                submit_button.click()
            except NoSuchElementException:
                # Try finding by value
                submit_button = self.driver.find_element(By.XPATH, "//input[@type='submit']")
                submit_button.click()
            
            time.sleep(3)  # Wait for results to load
            
            # Parse results
            results = self._parse_results()
            logger.info(f"Found {len(results)} results for {product_name}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching for {product_name}: {e}")
            return []
    
    def _parse_results(self):
        """Parse the search results page to extract TTB IDs and details."""
        results = []
        
        try:
            # Look for results table
            # The TTB site typically shows results in a table or list
            # We need to extract TTB IDs (14-digit numbers)
            page_source = self.driver.page_source
            
            # Find all TTB IDs (14-digit numbers)
            ttb_ids = re.findall(r'\b(\d{14})\b', page_source)
            
            # Try to find the results table
            try:
                results_table = self.driver.find_element(By.TAG_NAME, "table")
                rows = results_table.find_elements(By.TAG_NAME, "tr")
                
                for row in rows[1:]:  # Skip header
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 3:
                        result = {
                            'ttb_id': None,
                            'brand_name': cells[0].text if len(cells) > 0 else '',
                            'approval_date': cells[1].text if len(cells) > 1 else '',
                            'details': cells[2].text if len(cells) > 2 else ''
                        }
                        
                        # Try to extract TTB ID from the row
                        row_text = row.text
                        ttb_match = re.search(r'\b(\d{14})\b', row_text)
                        if ttb_match:
                            result['ttb_id'] = ttb_match.group(1)
                            results.append(result)
            except NoSuchElementException:
                logger.warning("Could not find results table")
                
                # If we found TTB IDs but no table, create basic results
                for ttb_id in set(ttb_ids):
                    results.append({
                        'ttb_id': ttb_id,
                        'brand_name': '',
                        'approval_date': '',
                        'details': ''
                    })
        
        except Exception as e:
            logger.error(f"Error parsing results: {e}")
        
        return results


def load_whiskey_data(csv_path):
    """Load whiskey data from CSV."""
    whiskeys = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            whiskeys.append(row)
    return whiskeys


def save_whiskey_data(csv_path, whiskeys):
    """Save updated whiskey data to CSV."""
    if not whiskeys:
        return
    
    fieldnames = whiskeys[0].keys()
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(whiskeys)


def match_ttb_result_to_whiskey(whiskey, ttb_results):
    """
    Try to match a TTB result to a specific whiskey entry.
    This is a best-effort matching based on available information.
    """
    # For now, return the first result if any
    # In a more sophisticated version, we could match by proof, year, etc.
    if ttb_results:
        return ttb_results[0]['ttb_id']
    return None


def main():
    """Main function to search and update TTB IDs."""
    csv_path = '_data/whiskeyindex.csv'
    
    # Load current data
    whiskeys = load_whiskey_data(csv_path)
    logger.info(f"Loaded {len(whiskeys)} whiskey entries")
    
    # Get unique product names
    unique_names = sorted(set(w['Name'] for w in whiskeys))
    logger.info(f"Found {len(unique_names)} unique product names")
    
    # Search for each unique name
    ttb_cache = {}
    
    with TTBColaSearcher(headless=True) as searcher:
        for name in unique_names:
            if name in ttb_cache:
                continue
                
            logger.info(f"Searching for: {name}")
            results = searcher.search_product(name, start_year=2000)
            ttb_cache[name] = results
            
            # Rate limiting - be respectful to the server
            time.sleep(2)
    
    # Update whiskey entries with TTB IDs
    updated_count = 0
    for whiskey in whiskeys:
        if whiskey.get('TTB_ID'):
            continue  # Already has a TTB ID
        
        name = whiskey['Name']
        if name in ttb_cache and ttb_cache[name]:
            ttb_id = match_ttb_result_to_whiskey(whiskey, ttb_cache[name])
            if ttb_id:
                whiskey['TTB_ID'] = ttb_id
                updated_count += 1
                logger.info(f"Updated {name} with TTB ID: {ttb_id}")
    
    logger.info(f"Updated {updated_count} entries with TTB IDs")
    
    # Save updated data
    save_whiskey_data(csv_path, whiskeys)
    logger.info("CSV file updated successfully")
    
    # Print summary
    print("\n=== TTB ID Search Summary ===")
    print(f"Total entries: {len(whiskeys)}")
    print(f"Entries updated: {updated_count}")
    print(f"Unique products searched: {len(unique_names)}")
    print(f"Products with results: {sum(1 for results in ttb_cache.values() if results)}")


if __name__ == '__main__':
    main()
