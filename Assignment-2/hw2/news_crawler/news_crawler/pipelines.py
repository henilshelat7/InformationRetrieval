# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from news_crawler.items import FetchItem

class Assignment2CrawlerPipeline:
    def __init__(self):
        self.counter = 0
    def process_item(self, item, spider):
        if isinstance(item, FetchItem):
            self.counter += 1
            if self.counter % 100 == 0:
                print(f"{self.counter} fetches completed...")
        return item
