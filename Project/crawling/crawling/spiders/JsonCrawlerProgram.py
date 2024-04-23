import scrapy # type: ignore
import json

class WebCrawler(scrapy.Spider):
    name = "crawler"
    start_urls = ["https://books.toscrape.com/"]
    max_pages = 10  # Maximum number of pages to crawl
    max_depth = 6  # Maximum depth of crawling
    pages_crawled = 0  # Counter to track the number of pages crawled

    def parse(self, response):
        self.pages_crawled += 1
        if self.pages_crawled > self.max_pages:
            self.logger.info(f"Reached maximum number of pages ({self.max_pages}). Stopping the crawler.")
            return

        depth = response.meta.get('depth', 0)
        if depth >= self.max_depth:
            self.logger.info(f"Reached maximum depth ({self.max_depth}). Ignoring further links.")
            return

        filename = 'output.json'
        data_list = []

        for product in response.css('article.product_pod'):
            data = {
                'title': product.css('h3 a::text').get(),
                'price': product.css('p.price_color::text').get(),
                'availability': product.css('p.instock.availability').xpath('normalize-space()').get()  # Updated selector
            }
            data_list.append(data)

        with open(filename, 'a') as f:
            json.dump(data_list, f, indent=2)  # Dumping the entire list at once with indentation
            f.write('\n')  # Add a newline at the end

        self.log(f'Saved page {response.url}')

        # Follow links to next pages
        for next_page in response.css('ul.pager li.next a::attr(href)'):
            yield response.follow(next_page, self.parse)
