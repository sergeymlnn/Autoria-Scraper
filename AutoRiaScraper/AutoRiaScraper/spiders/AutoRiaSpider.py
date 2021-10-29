import scrapy


class AutoriaSpider(scrapy.Spider):
    name = 'autoria_spider'
    allowed_domains = ['auto.ria.com']
    start_urls = ['https://auto.ria.com/uk/']

    def parse(self, response):
        pass
