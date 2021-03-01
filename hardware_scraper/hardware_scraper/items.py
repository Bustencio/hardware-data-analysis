import scrapy


class Product(scrapy.Item):
    # define the fields for your item here like:
    item_id = scrapy.Field()
    item_price = scrapy.Field()
    item_category = scrapy.Field()
