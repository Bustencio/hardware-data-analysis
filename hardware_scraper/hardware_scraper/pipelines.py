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
            
        except Exception as e: 
            print(e)

    def process_item(self, item, spider):
        sourceList = {
            'pccomponentes': {
                'doc ': {
                    "item_id" : item["item_id"],
                    "item_price" : item["item_price"],
                    "item_category" : item["item_category"],
                    "item_source" : item["item_source"],
                    "item_reviews" : item["item_reviews"],
                    "item_rating" : item["item_rating"],
                    "item_sale" : item["item_sale"],
                    "item_discount" : item["item_discount"],
                    "item_link" : item["item_link"]
                },
                'index' : 'items_pccomponentes'
            },
            'wipoid': {
                'doc ': {
                    "item_id" : item["item_id"],
                    "item_price" : item["item_price"],
                    "item_category" : item["item_category"],
                    "item_source" : item["item_source"],
                    "item_reviews" : item["item_reviews"],
                    "item_rating" : item["item_rating"],
                    "item_sale" : item["item_sale"],
                    "item_discount" : item["item_discount"],
                    "item_link" : item["item_link"]
                },
                'index' : 'items_wipoid'
            }
        }

        index = sourceList[item["item_source"]]['index']
        document = sourceList[item["item_source"]]['doc']

        res = es.index(index=index, body=document)