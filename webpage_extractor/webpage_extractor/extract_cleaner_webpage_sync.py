from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
from datetime import datetime
import os

# Try multiple common cookie consent button selectors
cookie_button_selectors = [
    'button[id*="accept"]',
    'button[id*="cookie"]',
    'button[class*="cookie"]',
    'button[class*="consent"]',
    '[data-tracking-element-id*="cookie"]',
    '[aria-label*="accept" i]',
    '[aria-label*="cookie" i]',
    'button:has-text("Accept")',
    'button:has-text("Accept all")',
    'button:has-text("I agree")',
    'button:has-text("Allow all")'
]

async def extract_clean_content(url, output_dir=None):
    """
    Extract clean content from a webpage.
    
    Args:
        url (str): The URL to extract content from
        output_dir (str, optional): Directory to save files. Defaults to current directory.
        
    Returns:
        dict: Dictionary containing clean_data and screenshot_path
    """
    if output_dir is None:
        output_dir = os.getcwd()
    
    os.makedirs(output_dir, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.firefox.launch()
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_load_state('networkidle')
        # Try each selector and click the first one that works
        for selector in cookie_button_selectors:
            try:
                await page.wait_for_selector(selector, timeout=2000)
                await page.click(selector)
                break  # Exit loop after successful click
            except:
                continue

        # Scroll to the bottom of the page
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)  # Wait for any lazy-loaded content

        name = f'extracted_clean_page_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        screenshot_path = os.path.join(output_dir, f'{name}.png')
        await page.screenshot(path=screenshot_path, full_page=True)
        
        html_content = await page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove all style and script elements
        for element in soup(['style', 'script', 'link', 'meta']):
            element.decompose()

        # Save the cleaned HTML
        filename = os.path.join(output_dir, f'{name}.html')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
        # Extract just the meaningful text content
        clean_data = {
            'title': soup.title.string.strip() if soup.title else '',
            'main_content': [],
            'links': []
        }
        
        # Get main content (headings and paragraphs)
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p']):
            text = tag.get_text().strip()
            if text:
                clean_data['main_content'].append({
                    'type': tag.name,
                    'text': text
                })
        
        # Get links with their text
        for link in soup.find_all('a'):
            href = link.get('href')
            text = link.get_text().strip()
            if href and text:
                clean_data['links'].append({
                    'text': text,
                    'url': href
                })
                
        await browser.close()

        return {
            'clean_data': clean_data,
            'screenshot_path': screenshot_path,
            'html_path': filename
        }

def print_extraction_results(result):
    """Print the extraction results in a readable format"""
    clean_data = result['clean_data']
    print("Title:", clean_data['title'])
    print("\nMain Content:")
    for item in clean_data['main_content']:
        print(f"{item['type'].upper()}: {item['text']}")
    print("\nLinks:")
    for link in clean_data['links']:
        print(f"- {link['text']}: {link['url']}")
    print(f"\nScreenshot saved to: {result['screenshot_path']}")
    print(f"HTML saved to: {result['html_path']}")

