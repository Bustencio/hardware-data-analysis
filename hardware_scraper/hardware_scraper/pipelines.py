# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class HardwareScraperPipeline:
    def process_item(self, item, spider):

        item['item_id'] = str(item['item_id']).replace("[","").replace("]","").replace("'", "")
        item['item_category'] = str(item['item_category']).replace("[","").replace("]","").replace("'", "")

        return item
