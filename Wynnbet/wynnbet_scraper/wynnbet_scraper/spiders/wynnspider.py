import scrapy


class WynnspiderSpider(scrapy.Spider):
    name = "wynnspider"
    allowed_domains = ["ny.wynnbet.com"]
    start_urls = ['https://ny.wynnbet.com/sportsbook']

    def parse(self, response):
        nfl_link = response.xpath("//a[contains(text(), 'NFL')]/@href").get()
        if nfl_link:
            yield scrapy.Request(response.urljoin(nfl_link), callback=self.parse_nfl)

