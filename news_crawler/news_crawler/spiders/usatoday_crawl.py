from urllib.parse import urlparse
from scrapy import Spider
import scrapy
from url_normalize import url_normalize
from news_crawler.items import URLItem, FetchItem, VisitItem

class usatoday_crawl(Spider):
    name = 'usatoday'
    allowed_domains = ['usatoday.com']
     
    def start_requests(self):
        yield scrapy.Request(f'https://www.{self.domain}', self.parse)
    
    def __init__(self, domain=None, *args, **kwargs):
        super(usatoday_crawl, self).__init__(*args, **kwargs)
        self.domain = 'usatoday.com'
        self.fetched = 0
        self.visited_urls = set()
        
    def _is_in_domain(self, url):
        
        parsed_url = urlparse(url)
        
        if str(parsed_url.netloc).startswith(self.domain):
            return True
        elif str(parsed_url.netloc).startswith(f"www.{self.domain}"):
            return True
        else:
            return False
       
    
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
                                
                            else:
                                url_result = URLItem(url = url, is_in_domain = False)
                                responses.append(url_result)
                               
                    visit_result = VisitItem(url = response.url, num_out_links = num_out_links, content_type = content_type, size = size)
                    responses.append(visit_result)
                    
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