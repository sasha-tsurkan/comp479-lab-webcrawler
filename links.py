import scrapy
from urllib.parse import urlparse, urljoin

class LinksSpider(scrapy.Spider):
    name = "links"
    allowed_domains = []
    start_urls = []

    def __init__(self,start_url=None, allowed_domains = None,  max_pages = 10 ,*args, **kwargs):
        super().__init__(*args, **kwargs)
        if not start_url:
            start_url = "https://en.wikipedia.org/wiki/Socompa"
            print("Using default 'https://en.wikipedia.org/wiki/Socompa'")
        self.start_urls = [start_url]
        if allowed_domains and allowed_domains.lower() != 'nil':
            self.allowed_domains = [d.strip() for d in allowed_domains.split(',')]
        else:
            self.allowed_domains = None
        self.max_pages = int(max_pages)
        self.page_count = 0
        self.visited = set()

    def parse(self, response):
        if self.page_count >= self.max_pages:
            self.crawler.engine.close_spider(self, reason='max_pages_reached')
            return
        self.page_count += 1
        # Save or process the page as needed
        self.visited.add(response.url)
        self.log(f"Downloaded page {self.page_count}: {response.url}")
        links = response.css('a::attr(href)').getall()
        for link in links:
            absolute_url = urljoin(response.url, link)
            domain = urlparse(absolute_url).netloc
            # Filter by allowed_domains if provided
            if self.allowed_domains:
                if not any(domain.endswith(ad) for ad in self.allowed_domains):
                    continue
            if absolute_url not in self.visited:
                self.visited.add(absolute_url)
                yield {'link': absolute_url}
                # Only follow if we haven't reached the max page count
                if self.page_count < self.max_pages:
                    yield scrapy.Request(absolute_url, callback=self.parse)

#scrapy crawl links -a start_url=https://en.wikipedia.org/wiki/Socompa -a allowed_domains=wikipedia.org
#scrapy crawl links -a start_url=https://en.wikipedia.org/wiki/Socompa -a allowed_domains=nil
#scrapy crawl links -a start_url=https://en.wikipedia.org/wiki/Socompa -a allowed_domains=wikipedia.org -a max_pages=5

