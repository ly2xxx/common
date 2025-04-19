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

async def extract_clean_content(url):
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
        screenshot_path = os.path.abspath(f'{name}.png')  # Get absolute path
        await page.screenshot(path=screenshot_path, full_page=True)
        
        html_content = await page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove all style and script elements
        for element in soup(['style', 'script', 'link', 'meta']):
            element.decompose()

        # Save the cleaned HTML
        filename = f'{name}.html'
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

        # # Generate HTML content
        # html_output = f"""
        # <html>
        # <head><title>{clean_data['title']}</title></head>
        # <body>
        #     <h1>{clean_data['title']}</h1>
        #     <h2>Main Content:</h2>
        #     {''.join(f'<{item["type"]}>{item["text"]}</{item["type"]}>' for item in clean_data['main_content'])}
        #     <h2>Links:</h2>
        #     <ul>
        #     {''.join(f'<li><a href="{link["url"]}">{link["text"]}</a></li>' for link in clean_data['links'])}
        #     </ul>
        # </body>
        # </html>
        # """
        
        # # Save to file with timestamp
        # filename = f'extracted_clean_page_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        # with open(filename, 'w', encoding='utf-8') as f:
        #     f.write(html_output)

        print("Title:", clean_data['title'])
        print("\nMain Content:")
        for item in clean_data['main_content']:
            print(f"{item['type'].upper()}: {item['text']}")
        print("\nLinks:")
        for link in clean_data['links']:
            print(f"- {link['text']}: {link['url']}")
        return {
            'clean_data': clean_data,
            'screenshot_path': screenshot_path
        }

# Usage
async def main(url):
    # url = "https://www.skyscanner.net/transport/flights/GLAS/CSHA/cheapest-flights-from-Glasgow-to-Shanghai.html?oym=2504&iym=2504&preferDirects=false&qp_prevPrice=378&qp_prevProvider=mas_adfeeds&qp_prevCurrency=GBP&utm_medium=display&utm_source=criteo&utm_campaign=uk-flights-conversion-cookiepool&utm_content=feed&utm_term=71517&AssociateID=DIS_FLI_00053_00000&campaign_id=21172&adgroupid=71517&click_timestamp=1738103951&utm_id=71517&cto_pld=sZgC93gLAAD9us0aCVsoLg&selectedoday=01&selectediday=01"
    # url = "https://www.skyscanner.net/transport/flights/GLAS/CSHA/cheapest-flights-from-Glasgow-to-Shanghai.html?oym=2507&iym=2508&preferDirects=false&qp_prevPrice=378&qp_prevProvider=mas_adfeeds&qp_prevCurrency=GBP&utm_medium=display&utm_source=criteo&utm_campaign=uk-flights-conversion-cookiepool&utm_content=feed&utm_term=71517&AssociateID=DIS_FLI_00053_00000&campaign_id=21172&adgroupid=71517&click_timestamp=1738103951&utm_id=71517&cto_pld=sZgC93gLAAD9us0aCVsoLg&selectedoday=21&selectediday=11"
    result = await extract_clean_content(url)
    print(f"Screenshot saved to: {result['screenshot_path']}")
    print("Clean data:", result['clean_data'])

if __name__ == "__main__":
    # url = "https://footballdatabase.com/ranking/world/1"
    url = "https://www.perplexity.ai/search/research-unfair-cases-when-old-65CgNCQHRtW3FQqd_pHvng#0"
    asyncio.run(main(url))
