import scrapy
import logging

from hardware_scraper.items import Product

#logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.WARNING)


class PccomSpider(scrapy.Spider):
    name = 'pccom'
    allowed_domains = ['pccomponentes.com']
    start_urls = ['https://www.pccomponentes.com/componentes']
    all_categories = []

    def yield_category(self):
        if self.all_categories:
            url = self.all_categories.pop()
            logging.warning("Scraping category %s " % (url))
            return scrapy.Request(url, self.parse_item_list)

    # Scrapes links for every category from main page
    def parse(self, response):
        catList = ['https://www.pccomponentes.com/placas-base', 'https://www.pccomponentes.com/procesadores', 'https://www.pccomponentes.com/discos-duros', 'https://www.pccomponentes.com/tarjetas-graficas', 'https://www.pccomponentes.com/memorias-ram']

        categories = response.xpath('//a[contains(@class,"enlace-secundario")]/@href')
        for category in categories:
            if str(category.extract()) in catList:
                self.all_categories.append(response.urljoin(category.extract()))
        yield self.yield_category()

    # Scrapes products from every page of each category
    def parse_item_list(self, response):

        # Create item object
        products = response.xpath('//article[contains(@class,"c-product-card")]')
        for product in products:
            item = Product()
            item['item_id'] = product.xpath('@data-name').extract_first()
            item['item_price'] = float(product.xpath('@data-price').get())
            item['item_category'] = product.xpath('@data-category').extract_first()
            item['item_source'] = 'pccomponentes'
            item['item_rating'] = product.xpath('//div[contains(@class,"c-star-rating")]/span[contains(@class,"cy-product-text")]/text()').get()
            item['item_reviews'] = product.xpath('//div[contains(@class,"c-star-rating")]/span[contains(@class,"cy-product-rating-result")]/text()').get()
            sale = product.xpath('//div[contains(@class,"c-product-card__discount")]/span[contains(@class,"c-badge--discount")]/text()').get()
            if sale is None:
                item['sale'] = False
            else:
                item['sale'] = True
                item['sale_price'] = product.xpath('//div[contains(@class,"c-product-card__prices")]/div[contains(@class,"c-product-card__prices-actual")]/span/text()').get()
            yield item

        # URL of the next page
        next_page = response.xpath('//div[@id="pager"]//li[contains(@class,"c-paginator__next")]//a/@href').extract_first()
        if next_page:
            next_url = response.urljoin(next_page)
            yield scrapy.Request(next_url, self.parse_item_list)
        else:
            logging.warning("All pages of this category scraped, scraping next category")
            yield self.yield_category()
