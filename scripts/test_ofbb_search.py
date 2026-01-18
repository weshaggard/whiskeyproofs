#!/usr/bin/env python3
"""Test different search terms for Old Forester Birthday Bourbon."""

import requests
import re
from bs4 import BeautifulSoup

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def search_ttb(brand_name, start_year, end_year):
    """Search TTB COLA registry."""
    url = "https://www.ttbonline.gov/colasonline/publicSearchColasBasicProcess.do"
    
    start_date = f"01/01/{start_year}"
    end_date = f"12/31/{end_year}"
    
    data = {
        'action': 'search',
        'brand': brand_name,
        'approvalDateFrom': start_date,
        'approvalDateTo': end_date,
    }
    
    try:
        response = requests.post(url, data=data, verify=False, timeout=30)
        return response.text
    except Exception as e:
        print(f"Error: {e}")
        return None

def count_results(html):
    """Count number of results in HTML."""
    if not html:
        return 0
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Look for result count text
    text = soup.get_text()
    
    # Check for "no results" message
    if "no records found" in text.lower() or "no results" in text.lower():
        return 0
    
    # Count table rows with links to TTB IDs
    rows = soup.find_all('a', href=re.compile(r'ttbid='))
    return len(rows)

# Test different search terms
search_terms = [
    "Birthday Bourbon",
    "Old Forester Birthday",
    "Old Forester",
    "Birthday",
]

print("Testing different search terms for years 2020-2025:\n")

for term in search_terms:
    print(f"Searching for '{term}'...")
    html = search_ttb(term, 2020, 2025)
    count = count_results(html)
    print(f"  Results: {count}")
    
    if count > 0 and count <= 10:
        # Show the TTB IDs found
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', href=re.compile(r'ttbid='))
        print(f"  TTB IDs found:")
        for link in links[:10]:
            href = link.get('href', '')
            match = re.search(r'ttbid=(\d+)', href)
            if match:
                ttb_id = match.group(1)
                # Try to get the brand name from the row
                row = link.find_parent('tr')
                if row:
                    cells = row.find_all('td')
                    brand_info = ' | '.join([cell.get_text(strip=True) for cell in cells[:3]])
                    print(f"    {ttb_id}: {brand_info}")
    print()
