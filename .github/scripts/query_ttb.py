#!/usr/bin/env python3
"""
Query TTB COLA Public Registry for whiskey approval IDs.

This script searches the TTB (Alcohol and Tobacco Tax and Trade Bureau) 
COLA Public Registry to find TTB approval IDs for whiskey entries in the database.

The script uses Selenium WebDriver to automate browser interactions with the TTB website.

Requirements:
    pip install selenium
    
    You also need ChromeDriver or GeckoDriver installed:
    - Chrome: https://chromedriver.chromium.org/
    - Firefox: https://github.com/mozilla/geckodriver/releases

Usage:
    python3 .github/scripts/query_ttb.py [--test] [--browser chrome|firefox]
    
Options:
    --test       Run in test mode with a small sample of entries
    --browser    Browser to use (chrome or firefox, default: chrome)
    --headless   Run browser in headless mode
    --limit N    Limit to N entries (default: all without TTB_ID)
"""

import csv
import re
import sys
import time
import argparse
from urllib.parse import urlencode, quote

# Try to import selenium, provide helpful error if not available
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class TTBQuerier:
    """Query the TTB COLA Public Registry for whiskey approval IDs"""
    
    SEARCH_URL = "https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do"
    DETAIL_URL = "https://www.ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid="
    
    def __init__(self, verbose=False, browser_type='chrome', headless=True):
        self.verbose = verbose
        self.browser_type = browser_type
        self.headless = headless
        self.driver = None
        
    def _init_browser(self):
        """Initialize the Selenium WebDriver"""
        if not SELENIUM_AVAILABLE:
            raise RuntimeError(
                "Selenium is not installed. Please install it with: pip install selenium\n"
                "You also need to install ChromeDriver or GeckoDriver."
            )
        
        if self.browser_type == 'chrome':
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Chrome(options=options)
        elif self.browser_type == 'firefox':
            options = webdriver.FirefoxOptions()
            if self.headless:
                options.add_argument('--headless')
            self.driver = webdriver.Firefox(options=options)
        else:
            raise ValueError(f"Unsupported browser: {self.browser_type}")
        
        if self.verbose:
            print(f"Initialized {self.browser_type} browser (headless={self.headless})")
    
    def _close_browser(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
        
    def search_whiskey(self, name, batch, proof, release_year):
        """
        Search TTB COLA registry for a whiskey entry using browser automation.
        
        Args:
            name: Product name (e.g., "Booker's", "Angel's Envy Cask Strength")
            batch: Batch identifier
            proof: Proof value
            release_year: Release year
            
        Returns:
            List of matching TTB IDs with their details, or empty list if none found
        """
        if not self.driver:
            self._init_browser()
        
        # Extract brand name for search
        brand = self._extract_brand_name(name)
        
        if self.verbose:
            print(f"  Searching: {name} (brand: {brand}), batch: {batch}, proof: {proof}, year: {release_year}")
        
        try:
            # Navigate to search page
            self.driver.get(self.SEARCH_URL)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 10)
            
            # Fill in the search form
            # Brand Name field
            try:
                brand_field = wait.until(
                    EC.presence_of_element_located((By.NAME, "brandName"))
                )
                brand_field.clear()
                brand_field.send_keys(brand)
            except (TimeoutException, NoSuchElementException):
                if self.verbose:
                    print("    Warning: Could not find brand name field")
            
            # Filter by year if possible
            try:
                # Look for year field - the exact field name may vary
                year_field = self.driver.find_element(By.NAME, "effectiveYear")
                year_field.clear()
                year_field.send_keys(str(release_year))
            except NoSuchElementException:
                if self.verbose:
                    print(f"    Note: Year field not found, searching without year filter")
            
            # Submit the search
            try:
                search_button = self.driver.find_element(By.NAME, "search")
                search_button.click()
            except NoSuchElementException:
                # Try finding by button text
                search_button = self.driver.find_element(By.XPATH, "//input[@type='submit' and @value='Search']")
                search_button.click()
            
            # Wait for results to load
            time.sleep(2)
            
            # Parse search results
            results = self._parse_search_results(proof, release_year)
            
            if self.verbose:
                print(f"    Found {len(results)} potential match(es)")
            
            return results
            
        except Exception as e:
            if self.verbose:
                print(f"    Error during search: {e}")
            return []
    
    def _parse_search_results(self, target_proof, target_year):
        """
        Parse the search results page to extract TTB IDs.
        
        Filters results by proof and year to find the best matches.
        """
        results = []
        
        try:
            # Look for result rows - the exact structure may vary
            # This is a template that may need adjustment based on actual HTML
            result_rows = self.driver.find_elements(By.XPATH, "//table[@class='resultTable']//tr[position()>1]")
            
            for row in result_rows:
                try:
                    # Extract TTB ID from the row (typically a link)
                    ttb_link = row.find_element(By.XPATH, ".//a[contains(@href, 'ttbid=')]")
                    href = ttb_link.get_attribute('href')
                    
                    # Extract TTB ID from URL
                    match = re.search(r'ttbid=(\d+)', href)
                    if match:
                        ttb_id = match.group(1)
                        
                        # Try to extract proof and year from result
                        result_text = row.text
                        
                        # Store result with metadata
                        results.append({
                            'ttb_id': ttb_id,
                            'text': result_text,
                            'url': href
                        })
                except NoSuchElementException:
                    continue
            
        except Exception as e:
            if self.verbose:
                print(f"    Error parsing results: {e}")
        
        return results
    
    def _extract_brand_name(self, name):
        """Extract brand name from product name"""
        # Common whiskey product terms to split on
        split_terms = [
            'Cask Strength',
            'Barrel Proof',
            'Single Barrel',
            'Small Batch',
            'Limited Edition',
            'Special Release',
            'Straight',
        ]
        
        brand = name
        for term in split_terms:
            if term in name:
                brand = name.split(term)[0].strip()
                break
                
        return brand
    
    def query_csv_entries(self, csv_file, test_mode=False, limit=None):
        """
        Query TTB for all entries in CSV that don't have TTB IDs.
        
        Args:
            csv_file: Path to whiskeyindex.csv
            test_mode: If True, only process first 10 entries
            limit: Maximum number of entries to process
            
        Returns:
            Dictionary mapping row indices to found TTB IDs
        """
        results = {}
        
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return results
        
        # Filter to entries without TTB IDs
        entries_to_search = [
            (i, row) for i, row in enumerate(rows, start=2)
            if not row.get('TTB_ID', '').strip()
        ]
        
        print(f"Found {len(entries_to_search)} entries without TTB IDs")
        
        if test_mode:
            entries_to_search = entries_to_search[:10]
            print(f"Test mode: Processing only first {len(entries_to_search)} entries")
        elif limit:
            entries_to_search = entries_to_search[:limit]
            print(f"Limit set: Processing only first {len(entries_to_search)} entries")
        
        # Initialize browser once for all searches
        try:
            self._init_browser()
            
            for idx, (i, row) in enumerate(entries_to_search, start=1):
                name = row['Name']
                batch = row['Batch']
                proof = row['Proof']
                year = row['ReleaseYear']
                
                print(f"\n[{idx}/{len(entries_to_search)}] {name} - {batch} ({year})")
                
                ttb_results = self.search_whiskey(name, batch, proof, year)
                
                if ttb_results:
                    results[i] = ttb_results
                    print(f"  ✓ Found {len(ttb_results)} potential match(es)")
                    for result in ttb_results:
                        print(f"    - TTB ID: {result['ttb_id']}")
                else:
                    print(f"  ✗ No matches found")
                
                # Rate limiting - be respectful to the TTB server
                time.sleep(2)
        
        finally:
            self._close_browser()
        
        return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Query TTB COLA Public Registry for whiskey approval IDs'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode with only first 10 entries'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--csv',
        default='_data/whiskeyindex.csv',
        help='Path to CSV file (default: _data/whiskeyindex.csv)'
    )
    parser.add_argument(
        '--browser',
        choices=['chrome', 'firefox'],
        default='chrome',
        help='Browser to use (default: chrome)'
    )
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Run browser in visible mode (not headless)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of entries to process'
    )
    parser.add_argument(
        '--output',
        help='Output file to save results (JSON format)'
    )
    
    args = parser.parse_args()
    
    # Check if Selenium is available
    if not SELENIUM_AVAILABLE:
        print("=" * 60)
        print("ERROR: Selenium is not installed")
        print("=" * 60)
        print()
        print("This script requires Selenium to automate browser interactions")
        print("with the TTB COLA Public Registry.")
        print()
        print("To install Selenium:")
        print("  pip install selenium")
        print()
        print("You also need a WebDriver:")
        print("  - Chrome: https://chromedriver.chromium.org/")
        print("  - Firefox: https://github.com/mozilla/geckodriver/releases")
        print()
        sys.exit(1)
    
    print("=" * 60)
    print("TTB COLA Registry Query Tool")
    print("=" * 60)
    print()
    print("NOTE: This tool automates searches on the TTB COLA Public Registry.")
    print("Please use responsibly and respect the TTB server.")
    print()
    
    querier = TTBQuerier(
        verbose=args.verbose,
        browser_type=args.browser,
        headless=not args.no_headless
    )
    
    try:
        results = querier.query_csv_entries(
            args.csv,
            test_mode=args.test,
            limit=args.limit
        )
    except KeyboardInterrupt:
        print("\n\nSearch interrupted by user.")
        querier._close_browser()
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        querier._close_browser()
        sys.exit(1)
    
    print("=" * 60)
    print("Results Summary")
    print("=" * 60)
    print(f"Total entries searched: {len(results) if results else 0}")
    print(f"Entries with matches found: {len(results)}")
    
    if results:
        print("\nMatched entries:")
        for line_num, ttb_results in results.items():
            print(f"  Line {line_num}: {len(ttb_results)} potential match(es)")
            for result in ttb_results:
                print(f"    - {result['ttb_id']}")
        
        # Save results to file if requested
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to: {args.output}")
    else:
        print("\nNo matches found.")
        print("\nThis could mean:")
        print("  1. The entries don't have TTB COLA approvals in the public registry")
        print("  2. The search parameters need adjustment")
        print("  3. The TTB website structure has changed")
        print("\nConsider running with --verbose flag for more details.")


if __name__ == '__main__':
    main()
