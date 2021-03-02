import scrapy
from hardware_scraper.items import Product


class PccomSpider(scrapy.Spider):
    name = 'pccom'
    allowed_domains = ['pccomponentes.com']
    start_urls = ['https://www.pccomponentes.com/componentes']

    all_categories = []

    def yield_category(self):
        if self.all_categories:
            url = self.all_categories.pop()
            print("Scraping category %s " % (url))
            return scrapy.Request(url, self.parse_item_list)

    # Scrapes links for every category from main page
    def parse(self, response):
        categories = response.xpath(
            '//a[contains(@class,"enlace-secundario")]/@href')
        self.all_categories = list(response.urljoin(
            category.extract()) for category in categories)
        yield self.yield_category()

    # Scrapes products from every page of each category
    def parse_item_list(self, response):

        # Create item object
        products = response.xpath(
            '//article[contains(@class,"tarjeta-articulo")]')
        for product in products:
            item = Product()
            item['item_id'] = product.xpath('@data-name').extract()
            item['item_price'] = float(product.xpath('@data-price').get())
            item['item_category'] = product.xpath('@data-category').extract()
            """ item['imgSource'] = product.xpath(
                '//div[contains(@class,"tarjeta-articulo__foto")]//img/@src').extract_first() """
            yield item

        # URL of the next page
        next_page = response.xpath(
            '//div[@id="pager"]//li[contains(@class,"c-paginator__next")]//a/@href').extract_first()
        if next_page:
            next_url = response.urljoin(next_page)
            yield scrapy.Request(next_url, self.parse_item_list)
        else:
            print("All pages of this category scraped, scraping next category")
            yield self.yield_category()
