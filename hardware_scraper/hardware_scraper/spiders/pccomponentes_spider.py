import scrapy
import logging

from hardware_scraper.items import Product


class PccomSpider(scrapy.Spider):
    name = 'pccom'
    allowed_domains = ['pccomponentes.com']
    start_urls = ['https://www.pccomponentes.com/componentes']
    all_categories = []

    def yield_category(self):
        if self.all_categories:
            url = self.all_categories.pop()
            logging.info("Scraping category %s " % (url))
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
            reviews = product.xpath('.//div[contains(@class,"c-star-rating")]/span[contains(@class,"cy-product-rating-result")]/text()').get()
            if reviews is not None:
                item['item_rating'] = float(product.xpath('.//div[contains(@class,"c-star-rating")]/span[contains(@class,"cy-product-text")]/text()').get())
                item['item_reviews'] = int(reviews.split(' ')[0])
            else:
                item['item_rating'] = 0
                item['item_reviews'] = 0

            item['item_link'] = response.urljoin(product.xpath('.//a[contains(@class,"enlace-superpuesto")]/@href').extract_first())
            sale = product.xpath('.//div[contains(@class,"c-product-card__discount")]/span[contains(@class,"c-badge--discount")]/text()').get()

            if sale is None:
                item['item_sale'] = False
                item['item_discount'] = 0
            else:
                item['item_sale'] = True
                item['item_discount'] = int(sale[1:-1])

            yield item

        # URL of the next page
        next_page = response.xpath('//div[@id="pager"]//li[contains(@class,"c-paginator__next")]//a/@href').extract_first()
        if next_page:
            next_url = response.urljoin(next_page)
            yield scrapy.Request(next_url, self.parse_item_list)
        else:
            logging.info("All pages of this category scraped, scraping next category")
            yield self.yield_category()
