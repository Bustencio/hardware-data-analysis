import scrapy
from hardware_scraper.items import Product


class PccomponentesSpider(scrapy.Spider):
    name = 'pccomponentes'
    allowed_domains = ['pccomponentes.com']
    start_urls = ['https://www.pccomponentes.com/componentes']
