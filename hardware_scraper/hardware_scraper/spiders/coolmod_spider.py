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
                self.all_categories.append(response.urljoin(category.extract()))
        yield self.yield_category()


    # Scrapes products from every page of each category
    def load_items(self, response, item_url):
        script = """
        function main(splash, args)
            assert(splash:go(args.url))
            assert(splash:wait(5))

            // Localizamos el anuncio del pop-up y clickeamos en la pantalla para cerrarlo
            if splash:select('.sweet-overlay') ~= nil then
                local element = splash:select('.sweet-overlay')
                local bounds = element:bounds()
                assert(element:mouse_click{x=10, y=100})
            end   

            // Pulsamos el botón de carga hasta que no exista y esperamos que carguen los objetos
            assert(splash:wait(1))
            while splash:select('.button-load-more') do
                local element = splash:select('.button-load-more')
                local bounds = element:bounds()
                assert(element:mouse_click{x=bounds.width/2, y=bounds.height/2})
                assert(splash:wait(2))
            end
            return {
                html = splash:html()
            }
        end
        """
        
        yield SplashRequest(item_url, self.parse_item_list, endpoint='execute',
                            args={'lua_source': script, 'timeout': 300})


    def parse_item_list(self, response):
        # Identificamos cada artículo por un div con nombre item-product
        products = response.xpath('//div[contains(@class,"item-product")]')
        for product in products:
            item = Product()
            # Eliminamos símbolos innecesarios y extraemos la primera parte del nombre
            item_id = str(product.xpath('.//div[contains(@class,"product-name")]//a/@title').get()).replace("<span class='trademark_name'>®</span>", '')
            item['item_id'] = item_id.split(' - ')[0]
            # Precio del producto sin divisa ni puntos o comas
            item['item_price'] = float(str(product.xpath('.//div[contains(@class,"mod-product-price")]/text()').get()).replace('.','').replace(',','.').strip()[:-1])
            # Categoría del producto
            item['item_category'] = str(response.xpath('//span[contains(@class,"category-title")]/text()').get()).strip()
            # Página de origen
            item['item_source'] = 'coolmod'
            # Enlace al producto
            item['item_link'] = response.urljoin(product.xpath('.//div[contains(@class,"product-name")]//a/@href').get())

            # Comprobamos si el artículo está en promoción y el descuento 
            sale = product.xpath('.//div[contains(@class,"mod-product-discount-container")]/text()').get()
            if sale is None:
                item['item_sale'] = False
                item['item_discount'] = 0
            else:
                item['item_sale'] = True
                saleDiscount = str(sale).strip()
                item['item_discount'] = int(saleDiscount[1:-1])

            # Comprobamos si el artículo está disponible
            stock = product.xpath('.//div[contains(@class,"cat-product-availability")]').get()
            stockText = str(product.xpath('.//div[contains(@class,"cat-product-availability")]/text()').get()).strip()
            if stockText == 'Sin Stock':
                item['item_available'] = False
            else:
                item['item_available'] = True

            yield item

    
        logging.warning("All pages of this category scraped, scraping next category")
        yield self.yield_category()