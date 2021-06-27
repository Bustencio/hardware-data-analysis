import scrapy
import logging

from hardware_scraper.items import Product


class WipoidSpider(scrapy.Spider):
    name = 'wipoid'
    allowed_domains = ['wipoid.com']
    start_urls = ['https://www.wipoid.com/componentes/']
    all_categories = []
    catList = ['https://www.wipoid.com/placas-base/', 'https://www.wipoid.com/procesadores/', 'https://www.wipoid.com/discos-duros/', 'https://www.wipoid.com/tarjetas-graficas/', 'https://www.wipoid.com/memoria-ram/']

    def yield_category(self):
        if self.all_categories:
            url = self.all_categories.pop()
            logging.warning("Scraping category %s " % (url))
            return scrapy.Request(url, self.parse_item_list)

    def parse(self, response):
        # Extraemos las categorías de producto de la página inicial y las recorremos una a una
        categories = response.xpath('//a[contains(@class,"cat_name")]/@href')
        for category in categories:
            if str(category.extract()) in catList:
                self.all_categories.append(response.urljoin(category.extract()))
        yield self.yield_category()

    def parse_item_list(self, response):
        # Identificamos los artículos
        products = response.xpath('//div[contains(@class,"prd")]')
        for product in products:
            item = Product()
            # Nombre del artículo
            item['item_id'] = product.xpath('.//a[contains(@class,"product-name")]/@title').get()
            # Precio del artículo
            price = product.xpath('.//span[contains(@class,"price product-price")]/@content').get()
            if price is None:
                item['item_price'] = 0
            else:
                item['item_price'] = float(str(price).replace(' ',''))
            # Categoría de producto
            item['item_category'] = response.xpath('//h2[contains(@class,"category-name")]/text()').get().strip()
            # Página de origen
            item['item_source'] = 'wipoid'   
            # Enlace directo al producto
            item['item_link'] = product.xpath('.//a[contains(@class,"product-name")]/@href').get()
            # Comprobamos si el artículo está en oferta
            sale = product.xpath('.//span[contains(@class,"old-price")]/text()').get()
            if sale is None:
                item['item_sale'] = False
                item['item_discount'] = 0
            else:
                item['item_sale'] = True
                # Calculamos el porcentaje de descuento
                salePrice = float(str(sale.replace(',','.').replace(' ','').strip())[:-2])
                item['item_discount'] = int(100-(item['item_price']*100//salePrice))
            # Comprobamos si el artículo está disponible
            stock = product.xpath('.//a[contains(@class,"btn-addtocart")]').get()
            stockText = product.xpath('./span/text()').get()
            if stock is None or stockText == 'Sin stock':
                item['item_available'] = False
            else:
                item['item_available'] = True

            yield item

        # URL de la siguiente página
        next_page = response.xpath('//div[contains(@class,"pagination")]//li[contains(@class,"pagination_next")]//a/@href').get()
        if next_page:
            next_url = response.urljoin(next_page)
            yield scrapy.Request(next_url, self.parse_item_list)
        else:
            logging.warning("All pages of this category scraped, scraping next category")
            yield self.yield_category()
