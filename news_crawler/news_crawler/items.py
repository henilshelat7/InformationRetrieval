# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
### Using dataclass
import scrapy

from scrapy import Item, Field


class URLItem(Item):
    url= Field()
    is_in_domain = Field()

class FetchItem(Item):
    url= Field()
    status= Field()

class VisitItem(Item):
    url= Field()
    num_out_links= Field()
    content_type= Field()
    size= Field() # bytes

    