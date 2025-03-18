import asyncio
from crawl4ai import AsyncWebCrawler

async def test_crawl():
    print("[test_crawler][test_crawl] Starting crawler test...")
    try:
        async with AsyncWebCrawler() as crawler:
            # Test with a simple website
            result = await crawler.arun(url="https://example.com")
            print("[test_crawler][test_crawl] Successfully crawled website")
            print("[test_crawler][test_crawl] Content:", result.markdown[:200])
            return True
    except Exception as e:
        print("[test_crawler][test_crawl] Error:", str(e))
        return False

if __name__ == "__main__":
    asyncio.run(test_crawl())
