import scrapy
import logging

from hardware_scraper.items import Product, Article


class ChapuzasSpider(scrapy.Spider):
    name = 'chapuzas'
    allowed_domains = ['elchapuzasinformatico.com']
    start_urls = ['https://elchapuzasinformatico.com/informatica/hardware/']
    all_categories = []

    # Scrapes products from every page of each category
    def parse(self, response):

        # Create item object
        products = response.xpath('//div[contains(@class,"post-content")]')
        for product in products:
            item = Article()
            item['article_title'] = product.xpath('.//h2[contains(@class,"entry-title")]/a/@title').get()
            item['article_date'] = product.xpath('.//div[contains(@class,"post-date")]/text()').get()
            item['article_source'] = 'chapuzas'   
            item['article_link'] = product.xpath('.//h2[contains(@class,"entry-title")]/a/@href').get()
            yield item

        # URL of the next page
        current_page = response.xpath('//div[contains(@class,"nav-links")]/span[contains(@class,"page-numbers current")]/text()').get()
        next_page = response.xpath('//div[contains(@class,"nav-links")]/a[contains(@class,"next")]/@href').get()
        if next_page and current_page < 30:
            next_url = response.urljoin(next_page)
            yield scrapy.Request(next_url, self.parse)
        else:
            logging.warning("All articles scraped")
