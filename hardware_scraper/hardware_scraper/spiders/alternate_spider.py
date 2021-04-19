import scrapy
import logging

from scrapy_splash import SplashRequest
from hardware_scraper.items import Product


class AlternateSpider(scrapy.Spider):
    name = 'alternate'
    allowed_domains = ['alternate.es']
    start_urls = ['https://www.alternate.es/Hardware/Componentes-de-PC']
    all_categories = []
        
    def yield_category(self):
        if self.all_categories:
            url = self.all_categories.pop()
            logging.warning("Scraping category %s " % (url))
            return scrapy.Request(url, self.load_items, cb_kwargs=dict(item_url=url))

    # Scrapes links for every category from main page
    def parse(self, response):
        catList = ['https://www.alternate.es/Componentes-de-PC/Discos-duros', 'https://www.alternate.es/Componentes-de-PC/Placas-base', 'https://www.alternate.es/Memoria-RAM', 'https://www.alternate.es/Componentes-de-PC/Procesadores', 'https://www.alternate.es/Tarjetas-gráficas']

        categories = response.xpath('//form[@id="tle-tree-navigation:navigation-form"]//ul//li//a[contains(@class,"font-weight-bold")]/@href')
        for category in categories:
            if str(response.urljoin(category.get())) in catList:
                self.all_categories.append(response.urljoin(category.get()))
        yield self.yield_category()


    # Scrapes products from every page of each category
    def load_items(self, response, item_url):

        script = """
        function main(splash, args)
            assert(splash:go(args.url))
            assert(splash:wait(1))
            while splash:select('.loadMoreButton') do
                local element = splash:select('.loadMoreButton')
                local bounds = element:bounds()
                assert(element:mouse_click{x=bounds.width/2, y=bounds.height/2})
                assert(splash:wait(0.5))
            end
            return {
                html = splash:html()
            }
        end
        """
        
        yield SplashRequest(item_url, self.parse_item_list, endpoint='execute',
                            args={'lua_source': script, 'timeout': 300})

    # Scrapes products from every page of each category
    def parse_item_list(self, response):

        # Create item object
        products = response.xpath('//a[contains(@class,"productBox")]')

        for product in products:
            item = Product()
            item_brand = product.xpath('.//div[contains(@class,"product-name")]/span/text()').get().replace('®','').strip()
            item_name = product.xpath('.//div[contains(@class,"product-name")]/text()').get().replace('®','').strip()
            item['item_id'] = item_brand + ' ' + item_name
            item['item_price'] = float(str(product.xpath('.//span[contains(@class,"price")]/text()').get()).replace('.','').replace(',','.')[2:])
            item['item_category'] = response.xpath('//div[contains(@class,"listing-container")]//h1/text()').get().strip()
            item['item_source'] = 'alternate'   
            item['item_link'] = product.xpath('./@href').extract_first()
            sale = product.xpath('.//span[contains(@class,"old-price")]/text()').get()

            if sale is None:
                item['item_sale'] = False
                item['item_discount'] = 0
            else:
                item['item_sale'] = True
                salePrice = float(str(sale.replace(',','.').strip())[:-2])
                item['item_discount'] = int(100-(item['item_price']*100//salePrice))

            stock = product.xpath('.//div[contains(@class,"delivery-info")]').get()
            stockText = product.xpath('.//div[contains(@class,"delivery-info")]/span/text()').get()

            if stock is None or stockText != 'En stock':
                item['item_available'] = False
            else:
                item['item_available'] = True

            yield item

        
        logging.warning("All pages of this category scraped, scraping next category")
        yield self.yield_category()
