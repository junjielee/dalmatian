#!/usr/bin/env python
# encoding: utf-8


from scrapy import Spider, Request
from job.items import JobItem

import requests
import re

from urllib import urlencode
from sqlalchemy.orm import Session
from job.models import Job, session_scope, db_connect, create_tables
from job.pipelines import JobPipeline


LAGOU_POSITION_URL = "http://www.lagou.com/jobs/positionAjax.json?"
LAGOU_POSITION_DETAIL_URL_STRING = "http://www.lagou.com/jobs/{position_id}.html"

CITY = (
    ("guangzhou", "广州"),
)


class LagouJobSpider(Spider):
    """
    0. 从新查看接口还有没其他update等参数
    1. 查看create_time字段或者create_timestamp字段是不是发布时间或者是修改时间
    2. 在start_requests之前通过接口获取了所有职位，通过create_time筛选出新的出来
    3. 新职位以id为key，对应内容为值的字典，存到类里面
    4. 组装新的url扔到self.start_urls字段里面
    """
    name = "lagou_job"
    allowed_domains = ["lagou.com"]
    start_urls = []

    new_job_dict = {}

    def __init__(self, search="python", first="true", page=20):
        self.page = page
        self.first = first
        self.search_text = search

    def get_form_data(self, cur_page):
        return {
            "first": self.first,
            "pn": cur_page,
            "kd": self.search_text,
        }

    def get_query_string_parameter(self, city):
        return {
            "needAddtionalResult": "false",
            "city": city,
        }

    def filter_new_job(self):
        engine = db_connect()
        create_tables(engine)
        session_job = Session(bind=engine)
        for c in CITY:
            for page in xrange(1, self.page + 1):
                url = LAGOU_POSITION_URL + urlencode(self.get_query_string_parameter(c[1]))
                data = self.get_form_data(page)
                # TODO 添加请求头部，模仿浏览器访问
                json_response = requests.post(url, data).json()
                results = json_response['content']['positionResult']['result']
                if len(results) == 0:
                    break

                # 批量查询数据库里面有没有对应的id or id + create_time
                for i in results:
                    with session_scope(session_job) as session:
                        query_count = session.query(Job).filter_by(position_id=i["positionId"]).count()
                        if query_count < 1:
                            d = {
                                "position_id": i["positionId"],
                                "position_name": i["positionName"],
                                "salary": i["salary"],
                                "work_year": i["workYear"],
                                "create_time": i["createTime"],
                                "company_id": i["companyId"],
                                "company_name": i["companyFullName"],
                                "company_size": i["companySize"],
                                "publisher_id": i["publisherId"],
                                #  "address": "",
                                #  "position_detail": "",
                            }
                            self.new_job_dict[i["positionId"]] = d
                        elif query_count > 1:
                            raise

    def start_requests(self):
        self.filter_new_job()

        for key in self.new_job_dict:
            url = LAGOU_POSITION_DETAIL_URL_STRING.format(position_id=key)
            yield Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"}
            )

    def parse(self, response):
        # 获取当前页面的position_id
        m_id = re.match(r"http://www.lagou.com/jobs/(\d+).html", response.url)
        pipe = JobPipeline()
        if m_id:
            position_id = int(m_id.group(1))
            addr1_selectors = response.xpath('//div[@class="work_addr"]/a/text()').extract()
            addr2_selectors = response.xpath('//div[@class="work_addr"]/text()').extract()
            position_selectors = response.xpath('//dd[@class="job_bt"]/p/descendant-or-self::*/text()').extract()
            # for p_selector in position_selectors:
            #     selectors = p_selector.xpath('./descendant-or-self::*/text()').extract()
            #     s = "".join([p for p in selectors])
            #     print s
            # print len(position_selectors)
            # print position_selectors

            address = "".join([addr.strip() for addr in addr1_selectors]) + "".join([addr.strip().strip('- ') for addr in addr2_selectors])
            # print "".join([ addr.strip() for addr in position_selectors])

            # addr = address_selectors.extract().encode('utf-8')
            # print "addr: ", addr
            # position = position_selectors.encode('utf-8')
            # print "position: ", position

            self.new_job_dict[position_id]["address"] = address
            self.new_job_dict[position_id]["position_detail"] = "\n".join([s for s in position_selectors])

            item = JobItem()
            for key in self.new_job_dict[position_id]:
                item[key] = self.new_job_dict[position_id][key]

            pipe.process_item(item, self)
            return None
        else:
            print "Error: get response position id"
            return None
