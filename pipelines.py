# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo

class MegaddcrawlerPipeline:
    def __init__(self):
        self.db_conn = pymongo.MongoClient(
            'localhost',
            27017
        )
        database = self.db_conn['series']
        self.collection_series = database['series_table']
        self.collection_capitulos = database['capitulos_table']
        self.collection_external = database['externalLink_table']

    def process_item(self, item, spider):
        if 'cap_id' in item:
            self.collection_capitulos.insert(dict(item))
        elif 'external_link' in item:
            self.collection_external.insert(dict(item))
        else:
            self.collection_series.insert(dict(item))

        return item
