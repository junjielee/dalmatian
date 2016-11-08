# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):
    position_id = scrapy.Field()
    position_name = scrapy.Field()
    position_detail = scrapy.Field()
    address = scrapy.Field()
    salary = scrapy.Field()
    work_year = scrapy.Field()
    create_time = scrapy.Field()
    # create_timestamp = scrapy.Field()
    company_id = scrapy.Field()
    company_name = scrapy.Field()
    company_size = scrapy.Field()
    publisher_id = scrapy.Field()
