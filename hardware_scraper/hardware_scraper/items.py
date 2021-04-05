import scrapy


class Product(scrapy.Item):
    # define the fields for your item here like:
    item_id = scrapy.Field()
    item_price = scrapy.Field()
    item_category = scrapy.Field()
    item_source = scrapy.Field()
    item_rating = scrapy.Field()
    item_reviews = scrapy.Field()
    item_sale = scrapy.Field()
    item_discount = scrapy.Field()
    item_link = scrapy.Field()
    item_available = scrapy.Field()
