import asyncio
import sys
import os
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from datetime import datetime
import json

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, project_root)

from typing import List, Dict, Any, Optional
from database.db_manager import DatabaseManager

def debug_print(class_name: str, function_name: str, detail: str):
    """Print debug messages in the standard format."""
    print(f"[industry_crawler][{class_name}][{function_name}] {detail}")

class IndustryCrawler:
    def __init__(self, client_id: str):
        """Initialize industry crawler for a specific client."""
        self.client_id = client_id
        self.db = DatabaseManager(client_id)
        debug_print("IndustryCrawler", "__init__", f"Initialized for client {client_id}")

    async def _get_page_content(self, url: str) -> Optional[str]:
        """
        Get page content using Playwright with anti-detection measures.
        """
        try:
            async with async_playwright() as p:
                # Use chromium with stealth mode
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                )

                # Enable JavaScript and wait for network idle
                page = await context.new_page()
                await page.set_extra_http_headers({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1'
                })

                # Navigate and wait for content to load
                response = await page.goto(url, wait_until='networkidle')
                if not response or not response.ok:
                    raise Exception(f"Failed to fetch {url}: {response.status if response else 'No response'}")

                # Wait for main content to load
                await page.wait_for_load_state('networkidle')
                
                # Get the page content
                content = await page.content()
                
                await browser.close()
                return content

        except Exception as e:
            debug_print("IndustryCrawler", "_get_page_content", f"Error fetching {url}: {str(e)}")
            return None

    async def crawl_industry_data(self, urls: List[str], tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Crawl multiple URLs for industry data using Playwright.
        
        Args:
            urls: List of URLs to crawl
            tags: Optional list of tags to categorize the data (e.g., ['sales_trends', 'statistics'])
        """
        results = []
        for url in urls:
            try:
                debug_print("IndustryCrawler", "crawl_industry_data", f"Crawling {url}")
                
                # Get page content using Playwright
                content = await self._get_page_content(url)
                if not content:
                    continue
                
                # Parse HTML and extract content
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract title if available
                title = soup.title.string if soup.title else None
                
                # Remove non-content elements
                for element in soup(["script", "style", "iframe", "nav", "footer", "header", "aside"]):
                    element.decompose()
                
                # Extract main content area if possible
                main_content = None
                for tag in ["main", "article", "div[role='main']", ".content", "#content", ".post-content"]:
                    main_content = soup.select_one(tag)
                    if main_content:
                        break
                
                # Convert to markdown
                content = md(str(main_content if main_content else soup))
                
                # TODO: Use LLM to extract pain points from content
                pain_points = "TODO: Extract pain points using LLM"
                
                # Store in database with metadata
                entry_id = self.db.add_industry_data(
                    source=url,
                    content=content,
                    pain_points=pain_points,
                    title=title,
                    tags=tags,
                    crawled_at=datetime.now().isoformat()
                )
                
                results.append({
                    "id": entry_id,
                    "source": url,
                    "title": title,
                    "content": content[:200] + "...",  # Truncated for logging
                    "pain_points": pain_points,
                    "tags": tags
                })
                
                debug_print("IndustryCrawler", "crawl_industry_data", 
                          f"Successfully crawled and stored data from {url}")
                
            except Exception as e:
                debug_print("IndustryCrawler", "crawl_industry_data", 
                          f"Error crawling {url}: {str(e)}")
        
        return results

    def get_recent_data(self, limit: int = 10, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get recent industry data entries.
        
        Args:
            limit: Maximum number of entries to return
            tags: Optional list of tags to filter by
        """
        return self.db.get_industry_data(limit=limit, tags=tags)

    def search_data(self, keyword: str, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search industry data by keyword.
        
        Args:
            keyword: Search term
            tags: Optional list of tags to filter by
        """
        return self.db.search_industry_data(keyword, tags=tags)
