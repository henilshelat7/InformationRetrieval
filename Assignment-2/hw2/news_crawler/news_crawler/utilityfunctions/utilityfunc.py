from urllib.parse import urlparse

class utility_func:
    def _is_in_domain(self, url):
        parsed_url = urlparse(url)
        if parsed_url.netloc in self.allowed_domains:
            return True
        elif f"www.{parsed_url.netloc}" in self.allowed_domains:
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
        return [url_normalize(response.urljoin(url)) for url in scraped_urls if not url.startswith('mailto')] 