import pickle
import logging
import datetime

from itemadapter import ItemAdapter
from sklearn.base import TransformerMixin
from elasticsearch import Elasticsearch, ElasticsearchException



class ItemIndexerPipeline:

    def open_spider(self, spider):
        try:
            # Inicializamos la conexión de manera global para que pueda ser usada por el resto de funciones
            global es
            # No es necesario especificar la IP o el puerto ya que por defecto Elasticsearch 
            # busca una instancia disponible en localhost:9200
            es = Elasticsearch(timeout = 300, retry_on_timeout = True)
            
        except Exception as e: 
            logging.error("Error opening connection to Elasticsearch %s " % (e))


    def process_item(self, item, spider):
        try:
            source = item["item_source"]
            now = datetime.datetime.now()

            if source is 'pccomponentes':
                index = 'items_pccomponentes'
                doc = {
                        "item_id" : item["item_id"],
                        "item_price" : item["item_price"],
                        "item_category" : item["item_category"],
                        "item_source" : item["item_source"],
                        "item_reviews" : item["item_reviews"],
                        "item_rating" : item["item_rating"],
                        "item_sale" : item["item_sale"],
                        "item_discount" : item["item_discount"],
                        "item_link" : item["item_link"],
                        "item_date" : now.strftime("%Y-%m-%d")
                }

            elif source is 'wipoid':
                index = 'items_wipoid'
                doc = {
                        "item_id" : item["item_id"],
                        "item_price" : item["item_price"],
                        "item_category" : item["item_category"],
                        "item_source" : item["item_source"],
                        "item_sale" : item["item_sale"],
                        "item_discount" : item["item_discount"],
                        "item_link" : item["item_link"],
                        "item_available" : item["item_available"],
                        "item_date" : now.strftime("%Y-%m-%d")
                    }
            elif source is 'coolmod':
                index = 'items_coolmod'
                doc = {
                        "item_id" : item["item_id"],
                        "item_price" : item["item_price"],
                        "item_category" : item["item_category"],
                        "item_source" : item["item_source"],
                        "item_sale" : item["item_sale"],
                        "item_discount" : item["item_discount"],
                        "item_link" : item["item_link"],
                        "item_available" : item["item_available"],
                        "item_date" : now.strftime("%Y-%m-%d")
                    }
            elif source is 'alternate':
                index = 'items_alternate'
                doc = {
                        "item_id" : item["item_id"],
                        "item_price" : item["item_price"],
                        "item_category" : item["item_category"],
                        "item_source" : item["item_source"],
                        "item_sale" : item["item_sale"],
                        "item_discount" : item["item_discount"],
                        "item_link" : item["item_link"],
                        "item_available" : item["item_available"],
                        "item_date" : now.strftime("%Y-%m-%d")
                    }
            else:
                index = 'items_life-informatica'
                doc = {
                        "item_id" : item["item_id"],
                        "item_price" : item["item_price"],
                        "item_category" : item["item_category"],
                        "item_source" : item["item_source"],
                        "item_sale" : item["item_sale"],
                        "item_discount" : item["item_discount"],
                        "item_link" : item["item_link"],
                        "item_available" : item["item_available"],
                        "item_date" : now.strftime("%Y-%m-%d")
                    }

            res = es.index(index=index, body=doc)

        except ElasticsearchException as err:
            logging.error("Elasticsearch Error %s " % (err))
