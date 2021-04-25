import scrapy
import logging

from hardware_scraper.items import Product
from scrapy_splash import SplashRequest


class PccomSpider(scrapy.Spider):
    name = 'pccom'
    allowed_domains = ['pccomponentes.com']
    start_urls = ['https://www.pccomponentes.com/componentes']
    all_categories = []

    def start_requests(self):
        catList = ['https://www.pccomponentes.com/placas-base', 'https://www.pccomponentes.com/procesadores', 'https://www.pccomponentes.com/discos-duros', 'https://www.pccomponentes.com/tarjetas-graficas', 'https://www.pccomponentes.com/memorias-ram']

        for url in catList:
            script = """
            function main(splash, args)
                local num_scrolls = 40
                local scroll_delay = 2	

                local scroll_to = splash:jsfunc("window.scrollTo")
                local get_body_height = splash:jsfunc("function() {return document.body.scrollHeight;}")  
                assert(splash:go(splash.args.url))
                
                assert(splash:wait(2.5))
                if splash:select('.btn-more') ~= nil then
                local element = splash:select('.btn-more')
                local bounds = element:bounds()
                assert(element:mouse_click{x=bounds.width/2, y=bounds.height/2})
                end
                
                    assert(splash:wait(2.5))
                for _ = 1, num_scrolls do
                local height = get_body_height()
                for i = 1, 10 do
                    scroll_to(0, height * i/10)
                    splash:wait(scroll_delay/10)
                end
                end
                return {
                html = splash:html()
                }
            end
            """

            yield SplashRequest(url, self.parse, endpoint='execute',
                                args={'lua_source': script, 'timeout': 300})

    # Scrapes products from every page of each category
    def parse(self, response):

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