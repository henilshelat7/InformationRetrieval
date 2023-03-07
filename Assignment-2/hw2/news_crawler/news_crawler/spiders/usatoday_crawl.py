from urllib.parse import urlparse
from scrapy import Spider
import scrapy
from url_normalize import url_normalize
from news_crawler.items import URLItem, FetchItem, VisitItem
#from assignment2_crawler.utilityfunctions.utilityfunc import utility_func


#_get_content_type, _get_scraped_urls, _get_size, _is_in_domain

class usatoday_crawl(Spider):
    name = 'usatoday'
    allowed_domains = ['usatoday.com']
    
    # custom_settings = {
    #     'ROBOTSTXT_OBEY': False,
    #     'DEPTH_LIMIT': 16,
    #     'DOWNLOAD_DELAY': 1,
    #     'CONCURRENT_REQUESTS': 16,
    #     'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
    #     'REDIRECT_ENABLED': True,
    #     'COOKIES_ENABLED': False,
    #     'HTTPERROR_ALLOW_ALL': True,
    #     'LOG_LEVEL': 'INFO',
    #     'ITEM_PIPELINES': {
    #         'news_crawler.pipelines.Assignment2CrawlerPipeline': 300
    #     },
    #     'FEEDS': {
    #         './data/urls_usatoday.csv': {
    #             'format': 'csv',
    #             'item_classes': [URLItem],
    #             'fields': ['url', 'is_in_domain']
    #         },
    #         './data/fetch_usatoday.csv': {
    #             'format': 'csv',
    #             'item_classes': [FetchItem],
    #             'fields': ['url', 'status']
    #         },
    #         './data/visit_usatoday.csv': {
    #             'format': 'csv',
    #             'item_classes': [VisitItem],
    #             'fields': ['url', 'content_type', 'size', 'num_out_links']
    #         }
    #     }
    # }
    
    def start_requests(self):
        yield scrapy.Request(f'https://www.{self.domain}', self.parse)
    
    def __init__(self, domain=None, *args, **kwargs):
        super(usatoday_crawl, self).__init__(*args, **kwargs)
        self.domain = 'usatoday.com'
        self.fetched = 0
        self.visited_urls = set()
        # self._is_in_domain = utility_func._is_in_domain
        # self._get_content_type = utility_func._get_content_type
        # self._get_size = utility_func._get_size
        # self._get_scraped_urls = utility_func._get_scraped_urls

    def _is_in_domain(self, url):
        #return f'://{self.domain}' in url or f'://www.{self.domain}' in url
        parsed_url = urlparse(url)
        
        if str(parsed_url.netloc).startswith(self.domain):
            return True
        elif str(parsed_url.netloc).startswith(f"www.{self.domain}"):
            return True
        else:
            return False
        #print(parsed_url.netloc)
        # if self.domain in parsed_url.netloc:
        #     return True
        # elif f"www.{self.domain}" in parsed_url.netloc:
        #     return True
        # else:
        #     return False
    
    def _get_content_type(self, response):
        content_type = response.headers.get('Content-Type', b'').decode('utf-8')
        return content_type.split(';')[0]
    
    def _get_size(self, response):
        content_length = response.headers.get('Content-Length')
        if content_length:
            return int(content_length)
        else:
            return len(response.body) // 8
    
    def _get_scraped_urls(self, response):
        scraped_urls = response.css('a::attr(href)').getall()
        return [url_normalize(response.urljoin(url)) for url in scraped_urls if "mailto" not in url and "javascript:;" not in url]

    def parse(self, response):
        if response.url not in self.visited_urls:
            self.fetched += 1
            self.visited_urls.add(response.url)
            responses, request = [], []
            if self.fetched <= self.crawler.settings.getint('CLOSESPIDER_PAGECOUNT'):
                url_result = URLItem(url = response.url, is_in_domain = self._is_in_domain(response.url))
                responses.append(url_result)
                #yield url_result
                fetch_result = FetchItem(url = response.url, status = response.status)
                responses.append(fetch_result)
                #yield fetch_result
                if 200 <= response.status < 300:
                    content_type = self._get_content_type(response)
                    size = self._get_size(response)
                    num_out_links = 0
                    if content_type == 'text/html':
                        scraped_urls = self._get_scraped_urls(response)
                        num_out_links = len(scraped_urls)
                        for url in scraped_urls:
                            if self._is_in_domain(url):
                                request.append(url)
                                #yield response.follow(url=url, callback=self.parse)
                            else:
                                url_result = URLItem(url = url, is_in_domain = False)
                                responses.append(url_result)
                                #yield url_result
                    visit_result = VisitItem(url = response.url, num_out_links = num_out_links, content_type = content_type, size = size)
                    responses.append(visit_result)
                    #yield visit_result
                for res in responses:
                    yield res
                for req in request:
                    yield response.follow(url = req, callback = self.parse)
            else:
                url_result = URLItem(url = response.url, is_in_domain = self._is_in_domain(response.url))
                yield url_result
        else:
            url_result = URLItem(url = response.url, is_in_domain = self._is_in_domain(response.url))
            yield url_result