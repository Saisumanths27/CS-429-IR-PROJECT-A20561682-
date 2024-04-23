from scrapy.spiders import CrawlSpider, Rule # type: ignore
from scrapy.linkextractors import LinkExtractor # type: ignore
from scrapy.http import HtmlResponse  # type: ignore


class WebCrawler(CrawlSpider):
    name = "mycrawler"
    allowed_domains = ["toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    max_pages = 10  # Maximum number of pages to crawl
    max_depth = 6  # Maximum depth of crawling
    pages_crawled = 0  # Counter to track the number of pages crawled

    rules = (
        Rule(LinkExtractor(allow="catalogue/category"), follow=True),
        Rule(LinkExtractor(allow="catalogue", deny="category"), callback="parse_item", follow=True)
    )

    def parse_item(self, response):
        self.pages_crawled += 1
        if self.pages_crawled >= self.max_pages:
            self.logger.info(f"Reached maximum number of pages ({self.max_pages}). Stopping the crawler.")
            self.crawler.engine.close_spider(self, 'Reached maximum number of pages')

        depth = response.meta.get('depth', 0)
        if depth >= self.max_depth:
            self.logger.info(f"Reached maximum depth ({self.max_depth}). Ignoring further links.")
            return []

        filename = 'output.html'
        with open(filename, 'a') as f:
            f.write(response.body.decode())  # Write the entire HTML content of the page

        self.log('Saved file %s' % filename)
