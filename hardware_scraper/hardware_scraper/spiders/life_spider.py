import scrapy
import logging

from scrapy_splash import SplashRequest
from hardware_scraper.items import Product


class LifeSpider(scrapy.Spider):
    name = 'life'
    allowed_domains = ['lifeinformatica.com']
    start_urls = ['https://lifeinformatica.com/categoria-producto/family-componentes/']
    all_categories = []

    def yield_category(self):
        if self.all_categories:
            url = self.all_categories.pop()
            logging.warning("Scraping category %s " % (url))
            print(url)
            return scrapy.Request(url, self.load_items, cb_kwargs=dict(item_url=url))
            
            #return scrapy.Request(url, self.parse_item_list)

    # Scrapes links for every category from main page
    def parse(self, response):
        catList = ['https://lifeinformatica.com/categoria-producto/family-componentes/family-tarjetas-graficas/', 'https://lifeinformatica.com/categoria-producto/family-componentes/family-placas-base/', 'https://lifeinformatica.com/categoria-producto/family-componentes/family-memorias-ram/', 'https://lifeinformatica.com/categoria-producto/family-componentes/family-procesadores/', 'https://lifeinformatica.com/categoria-producto/family-componentes/family-discos-duros/']

        categories = response.xpath('//ul[contains(@class,"sub-categories")]//li[contains(@class,"cat-item")]//a/@href')
        for category in categories:
            if str(response.urljoin(category.get())) in catList:
                self.all_categories.append(response.urljoin(category.get()))
        yield self.yield_category()

    # Scrapes products from every page of each category
    def load_items(self, response, item_url):

        script = """
        function main(splash, args)
            assert(splash:go(args.url))
            assert(splash:wait(2))
            while splash:select('#yith-infs-button') do
                local element = splash:select('#yith-infs-button')
                local bounds = element:bounds()
                assert(element:mouse_click{x=bounds.width/2, y=bounds.height/2})
                assert(splash:wait(5))
            end
            return {
                html = splash:html()
            }
        end
        """
        yield SplashRequest(item_url, self.parse_item_list, endpoint='execute',
                            args={'lua_source': script, 'timeout': 300})

    def parse_item_list(self, response):

        # Create item object
        products = response.xpath('//div[contains(@class,"product-item__inner")]')
        for product in products:
            item = Product()
            item['item_id'] = product.xpath('.//h2[contains(@class,"woocommerce-loop-product__title")]/text()').get()
            item['item_price'] = float(str(product.xpath('.//span[contains(@class,"woocommerce-Price-amount amount")]/text()').get()).replace('.','').replace(',','.'))
            item['item_category'] = response.xpath('//h1[contains(@class,"page-title")]/text()').get()
            item['item_source'] = 'life-informatica'   
            item['item_link'] = product.xpath('.//a[contains(@class,"woocommerce-LoopProduct-link")]/@href').get()
            sale = product.xpath('.//span[contains(@class,"dto-loop")]/text()').get()

            if sale is None:
                item['item_sale'] = False
                item['item_discount'] = 0
            else:
                item['item_sale'] = True

                salePrice = float(str(product.xpath('.//del//span[contains(@class,"woocommerce-Price-amount amount")]/text()').get()).replace('.','').replace(',','.'))
                item['item_discount'] = int(100-(item['item_price']*100//salePrice))

            stock = product.xpath('.//span[contains(@class,"rebajado")]').get()
            stockText = product.xpath('./span/text()').get()

            if stock is None or stockText == 'Sin stock':
                item['item_available'] = False
            else:
                item['item_available'] = True

            yield item

        logging.warning("All pages of this category scraped, scraping next category")
        yield self.yield_category()
