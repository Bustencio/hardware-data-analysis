import scrapy
import logging

from hardware_scraper.items import Product


class WipoidSpider(scrapy.Spider):
    name = 'wipoid'
    allowed_domains = ['wipoid.com']
    start_urls = ['https://www.wipoid.com/componentes/']
    all_categories = []

    def yield_category(self):
        if self.all_categories:
            url = self.all_categories.pop()
            logging.warning("Scraping category %s " % (url))
            return scrapy.Request(url, self.parse_item_list)

    # Scrapes links for every category from main page
    def parse(self, response):
        catList = ['https://www.wipoid.com/placas-base/', 'https://www.wipoid.com/procesadores/', 'https://www.wipoid.com/discos-duros/', 'https://www.wipoid.com/tarjetas-graficas/', 'https://www.wipoid.com/memoria-ram/']

        categories = response.xpath('//a[contains(@class,"cat_name")]/@href')
        for category in categories:
            if str(category.extract()) in catList:
                self.all_categories.append(response.urljoin(category.extract()))
        yield self.yield_category()

    # Scrapes products from every page of each category
    def parse_item_list(self, response):

        # Create item object
        products = response.xpath('//div[contains(@class,"prd")]')
        for product in products:
            item = Product()
            item['item_id'] = product.xpath('.//a[contains(@class,"product-name")]/@title').get()
            item['item_price'] = float(product.xpath('.//span[contains(@class,"price product-price")]/@content').get().strip())
            item['item_category'] = response.xpath('/h2[contains(@class,"category-name")]').get()
            item['item_source'] = 'wipoid'   
            item['item_link'] = product.xpath('.//a[contains(@class,"product-name")]/@href').extract_first()
            sale = product.xpath('.//span[contains(@class,"old-price")]/text()').get()

            if sale is None:
                item['item_sale'] = False
                item['item_discount'] = 0
            else:
                item['item_sale'] = True
                salePrice = float(str(sale.replace(',','.').strip())[:-2])
                item['item_discount'] = int(100-(item['item_price']*100//salePrice))

            yield item

        # URL of the next page
        next_page = response.xpath('//div[@id="pager"]//li[contains(@class,"c-paginator__next")]//a/@href').extract_first()
        if next_page:
            next_url = response.urljoin(next_page)
            yield scrapy.Request(next_url, self.parse_item_list)
        else:
            logging.warning("All pages of this category scraped, scraping next category")
            yield self.yield_category()
