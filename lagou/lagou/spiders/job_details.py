# -*- coding: utf-8 -*-

import re
import utils
from scrapy import Spider, Request
from lagou.spiders.positions import get_jobs
from lagou.models import find_positions_not_detail
from lagou.pipelines import LagouPipeline


LAGOU_POSITION_DETAIL_URL_STRING = "https://www.lagou.com/jobs/{position_id}.html"


class JobDetailsSpider(Spider):
    name = 'job_details'
    # name = 'woodenrobot'
    # allowed_domains = ['woodenrobot.com']
    start_urls = []

    def start_requests(self):
        get_jobs()

        need_detail_jobs = find_positions_not_detail()

        for j in need_detail_jobs:
            url = LAGOU_POSITION_DETAIL_URL_STRING.format(position_id=j['positionId'])
            req = Request(
                url,
                headers=utils.get_detail_headers()
            )
            proxy_ip = utils.get_proxies_ip()
            if proxy_ip:
                req.meta['proxy'] = proxy_ip

            yield req

    def parse(self, response):
        # 获取当前页面的position_id
        # TODO 更好的正则，或者去掉后面部分可以不?
        m_id = re.match(r"https://www.lagou.com/jobs/(\d+).html", response.url)
        if m_id:
            d = {"positionId": int(m_id.group(1))}
            addr1_selectors = response.xpath('//div[@class="work_addr"]/a/text()').extract()
            addr2_selectors = response.xpath('//div[@class="work_addr"]/text()').extract()
            position_selectors = response.xpath('//dd[@class="job_bt"]/p/descendant-or-self::*/text()').extract()

            address = "".join([addr.strip() for addr in addr1_selectors]) + \
                "".join([addr.strip().strip('- ') for addr in addr2_selectors])
            d["address"] = address
            d["details"] = "\n".join([s for s in position_selectors])

            LagouPipeline().process_item(d, self)
            return None
        else:
            print "Error: get response position id"
            return None
