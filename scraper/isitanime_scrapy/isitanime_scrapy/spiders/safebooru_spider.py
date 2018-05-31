import scrapy

class SafebooruSpider(scrapy.Spider):
    name = 'SafebooruSpider'
    start_urls = ['https://safebooru.org/index.php?page=post&s=list&tags=-comic&pid=14000']
    custom_settings = {
        'DOWNLOAD_DELAY': '1',
    }

    def __init__(self, start_pid=0, **kwargs):
        self.start_urls = [
            'https://safebooru.org/index.php?page=post&s=list&tags=-comic&pid={start_pid}'.format(
                start_pid=str(start_pid)
            )
        ]
        super().__init__(**kwargs)

    def parse(self, response):
        if 's=list' in response.url:
            for image_page in response.css('.content .thumb a'):
                yield response.follow(image_page, self.parse)

            for next_page in response.css('a[alt="next"]'):
                yield response.follow(next_page, self.parse)

        elif 's=view' in response.url:
            for image in response.css('#image'):
                url = image.xpath('@src')[0].extract()
                url = 'http:/' + url.replace('//', '/')
                yield {
                    'url': url,
                    'prefix': 'safebooru',
                }
