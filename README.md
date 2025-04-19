# common
common library

# Webpage Extractor

A Python package for extracting and cleaning web content using Playwright and BeautifulSoup.

## Installation

```bash
pip install -e .
```

## Usage

```python
import asyncio
from webpage_extractor import extract_clean_content

async def main():
    url = "https://www.example.com"
    result = await extract_clean_content(url)
    print(f"Screenshot saved to: {result['screenshot_path']}")
    print("Clean data:", result['clean_data'])

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- Extracts title, main content, and links from webpages
- Takes screenshots of webpages
- Cleans and organizes extracted data
- Supports asynchronous operation
```

With these changes, you've now:
1. Created a centralized module structure with `webpage_extractor`
2. Moved the extraction functionality to this module
3. Updated the imports in the Streamlit app
4. Created proper package files (setup.py, requirements.txt, README.md)

To install and use this package, you would run:

```bash
pip install -e .

