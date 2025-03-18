import asyncio
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, project_root)

from src.scraping.industry.crawler import IndustryCrawler

async def test_industry_crawler():
    # Use the client ID from our database
    client_id = "6115501596"
    
    # Initialize crawler
    crawler = IndustryCrawler(client_id)
    print("[test_industry_crawler][main] Initialized crawler for client:", client_id)
    
    # Test URLs with tags for different types of sales industry data
    test_data = [
        {
            "urls": ["https://www.pipedrive.com/en/blog/sales-statistics"],
            "tags": ["sales_statistics", "industry_insights"]
        },
        {
            "urls": ["https://www.zendesk.com/blog/sales-trends/"],
            "tags": ["sales_trends", "industry_insights", "future_outlook"]
        },
        {
            "urls": ["https://www.ringcentral.com/us/en/blog/sales-statistics/"],
            "tags": ["sales_statistics", "industry_insights", "best_practices"]
        }
    ]
    
    all_results = []
    
    # Crawl industry data with tags
    print("[test_industry_crawler][main] Starting crawl...")
    for data in test_data:
        results = await crawler.crawl_industry_data(data["urls"], data["tags"])
        all_results.extend(results)
    
    # Print results
    print("[test_industry_crawler][main] Crawl results:")
    for result in all_results:
        print(f"\nSource: {result['source']}")
        print(f"Title: {result['title']}")
        print(f"Tags: {result['tags']}")
        print(f"Content preview: {result['content']}")
        print(f"Pain points: {result['pain_points']}")
    
    # Test data retrieval with different tag filters
    print("\n[test_industry_crawler][main] Testing data retrieval with tags:")
    
    # Get recent statistics
    stats_data = crawler.get_recent_data(limit=2, tags=["sales_statistics"])
    print("\nRecent Sales Statistics:")
    for data in stats_data:
        print(f"\nID: {data['id']}")
        print(f"Source: {data['source']}")
        print(f"Tags: {data['tags']}")
        print(f"Created at: {data['created_at']}")
    
    # Get recent trends
    trends_data = crawler.get_recent_data(limit=2, tags=["sales_trends"])
    print("\nRecent Sales Trends:")
    for data in trends_data:
        print(f"\nID: {data['id']}")
        print(f"Source: {data['source']}")
        print(f"Tags: {data['tags']}")
        print(f"Created at: {data['created_at']}")
    
    # Test search with tag filtering
    print("\n[test_industry_crawler][main] Testing search with tags:")
    search_results = crawler.search_data("sales", tags=["industry_insights"])
    print("\nSearch Results for 'sales' in industry insights:")
    for data in search_results:
        print(f"\nID: {data['id']}")
        print(f"Source: {data['source']}")
        print(f"Tags: {data['tags']}")
        print(f"Created at: {data['created_at']}")

if __name__ == "__main__":
    asyncio.run(test_industry_crawler())
