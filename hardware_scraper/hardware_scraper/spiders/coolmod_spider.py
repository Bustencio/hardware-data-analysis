import scrapy
import logging
from scrapy_splash import SplashRequest

from hardware_scraper.items import Product

class CoolmodSpider(scrapy.Spider):
    name = 'coolmod'
    allowed_domains = ['coolmod.com']
    start_urls = ['https://www.coolmod.com/componentes-hardware']
    all_categories = []

    def yield_category(self):
        if self.all_categories:
            url = self.all_categories.pop()
            if url == 'https://www.coolmod.com/componentes-pc-discos-duros':
                url = 'https://www.coolmod.com/discos-ssd'
            
            logging.warning("Scraping category %s " % (url))
            return scrapy.Request(url, self.load_items, cb_kwargs=dict(item_url=url))

    # Scrapes links for every category from main page
    def parse(self, response):
        catList = ['https://www.coolmod.com/componentes-pc-placas-base', 'https://www.coolmod.com/componentes-pc-procesadores', 'https://www.coolmod.com/tarjetas-gráficas', 'https://www.coolmod.com/componentes-pc-memorias-ram', 'https://www.coolmod.com/componentes-pc-discos-duros']

        categories = response.xpath('//li[contains(@class,"mod-li-cat")]//a/@href')
        for category in categories:
            if str(response.urljoin(category.extract())) in catList:
                print(str(response.urljoin(category.extract())))
                self.all_categories.append(response.urljoin(category.extract()))
        yield self.yield_category()

    # Scrapes products from every page of each category
    def load_items(self, response, item_url):

        script = """
        function main(splash, args)
            assert(splash:go(args.url))
            assert(splash:wait(0.5))
            while splash:select('.button-load-more') do
                local element = splash:select('.button-load-more')
                local bounds = element:bounds()
                assert(element:mouse_click{x=bounds.width/2, y=bounds.height/2})
                assert(splash:wait(1))
            end
            return {
                html = splash:html()
            }
        end
        """

        loadMoreButton = response.xpath('//button[contains(@class,"button-load-more")]').get()

        if loadMoreButton is None:
            yield scrapy.Request(item_url, self.parse_item_list)
        else:
            yield SplashRequest(item_url, self.parse_item_list, endpoint='execute',
                                args={'lua_source': script, 'timeout': 90})



    def parse_item_list(self, response):
        # Create item object
        products = response.xpath('//div[contains(@class,"item-product")]')
        for product in products:
            item = Product()
            item_id = str(product.xpath('.//div[contains(@class,"product-name")]//a/@title').get()).replace("<span class='trademark_name'>®</span>", '')
            item['item_id'] = item_id.split(' - ')[0]
            item['item_price'] = float(str(product.xpath('.//div[contains(@class,"mod-product-price")]/text()').get()).replace('.','').replace(',','.').strip()[:-1])
            item['item_category'] = str(response.xpath('//span[contains(@class,"category-title")]/text()').get()).strip()
            item['item_source'] = 'coolmod'
            item['item_link'] = response.urljoin(product.xpath('.//div[contains(@class,"product-name")]//a/@href').get())
            sale = product.xpath('.//div[contains(@class,"mod-product-discount-container")]/text()').get()

            if sale is None:
                item['item_sale'] = False
                item['item_discount'] = 0
            else:
                item['item_sale'] = True
                saleDiscount = str(sale).strip()
                item['item_discount'] = int(saleDiscount[1:-1])

            stock = product.xpath('.//div[contains(@class,"cat-product-availability")]').get()
            stockText = str(product.xpath('.//div[contains(@class,"cat-product-availability")]/text()').get()).strip()
            if stockText == 'Sin Stock':
                item['item_available'] = False
            else:
                item['item_available'] = True

            yield item

        # URL of the next page
        next_page = response.xpath('//div[contains(@class,"pagination")]//li[contains(@class,"pagination_next")]//a/@href').get()
        if next_page:
            next_url = response.urljoin(next_page)
            yield scrapy.Request(next_url, self.parse_item_list)
        else:
            logging.warning("All pages of this category scraped, scraping next category")
            yield self.yield_category()