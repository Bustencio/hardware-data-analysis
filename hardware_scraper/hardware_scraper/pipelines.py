# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from elasticsearch import Elasticsearch


class HardwareScraperPipeline:
    def process_item(self, item, spider):

        item['item_id'] = str(item['item_id']).replace("[","").replace("]","").replace("'", "")
        item['item_category'] = str(item['item_category']).replace("[","").replace("]","").replace("'", "")

        return item


class ItemIndexerPipeline:
    def open_spider(self, spider):
        try:
            global es
            es = Elasticsearch(timeout = 300, retry_on_timeout = True)
            
            print(es)
        except Exception as e: 
            print(e)

    def process_item(self, item, spider):
        doc = {
            "item_id" : item["item_id"],
            "item_price" : item["item_price"],
            "item_category" : item["item_category"],
            "item_source" : item["item_source"]
        }

        res = es.index(index='items_pccomponentes', body=doc)
        #print(res)