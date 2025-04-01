import os
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
import threading

# Load environment variables
load_dotenv()

class WebCrawler:
    def __init__(self):
        self.crawler = FirecrawlApp(api_key=os.getenv('FIRE_CRAWL_API'))

    def get_web_data(self, url, params=None, poll_interval=30):
        if params is None:
            params = {
                'limit': 50, 
                'scrapeOptions': {'formats': ['markdown']}
            }
        # Start the crawling process
        crawl_status = self.crawler.crawl_url(url=url, params=params, poll_interval=poll_interval)
        return crawl_status

   

# Example Usage
if __name__ == "__main__":
    crawler = WebCrawler()
    crawler.run_in_background("https://heallabsonline.com")
