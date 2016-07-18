#!/usr/bin/env python
# encoding: utf-8


from scrapy import Spider, Request
from douban_movie.items import MovieItem


class PlayingMovieSpider(Spider):
    name = "now_playing_movie"
    allowed_domains = ["douban.com"]
    start_urls = [
        "https://movie.douban.com/nowplaying/guangzhou/",
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
            )

    def parse(self, response):
        selectors = response.xpath('//div[@id="nowplaying"]/div[@class="mod-bd"]/ul[@class="lists"]/li')

        for selector in selectors:
            item = MovieItem()
            item["mid"] = selector.xpath('@id')[0].extract()
            item["name"] = selector.xpath('@data-title')[0].extract().encode('utf-8')
            item["score"] = selector.xpath('@data-score')[0].extract()
            item["star"] = selector.xpath('@data-star')[0].extract()
            item["region"] = selector.xpath('@data-region')[0].extract().encode('utf-8')

            yield item
