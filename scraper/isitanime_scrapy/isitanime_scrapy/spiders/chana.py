import scrapy

class ChanaSpider(scrapy.Spider):
    name = 'ChanaSpider'
    start_urls = ['https://boards.4chan.org/a/'] + [
        'https://boards.4chan.org/a/' + str(x) for x in range(2, 11)
    ]
    custom_settings = {
        'DOWNLOAD_DELAY': '1',
    }

    def parse(self, response):
        if 'thread' not in response.url:
            for thread_page in response.css('.replylink'):
                yield response.follow(thread_page, self.parse)

        elif 'thread' in response.url:
            for image in response.css('.fileThumb'):
                url = image.xpath('@href')[0].extract()
                url = 'http:/' + url.replace('//', '/')
                yield {
                    'url': url,
                    'prefix': 'chana'
                }
