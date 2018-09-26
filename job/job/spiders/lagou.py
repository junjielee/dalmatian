# -*- coding: utf-8 -*-

from scrapy import Spider, Request
from job.items import JobItem

import requests
import re

from urllib import urlencode
from sqlalchemy.orm import Session
from job.models import Job, session_scope, db_connect
from job.pipelines import JobPipeline


#: 配置爬虫地址以及搜索关键字
LAGOU_POSITION_URL = "https://www.lagou.com/jobs/positionAjax.json?"
LAGOU_POSITION_DETAIL_URL_STRING = "https://www.lagou.com/jobs/{position_id}.html"

CITY = (
    ("guangzhou", "广州"),
)
SEARCH_CONTENT = ["python"]


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

    def __init__(self, first="true", page=20):
        self.page = page
        self.first = first

    def get_form_data(self, cur_page, search_content):
        return {
            "first": self.first,
            "pn": cur_page,
            "kd": search_content
        }

    def get_query_string_parameter(self, city):
        return {
            "needAddtionalResult": "false",
            "city": city,
        }

    def filter_new_job(self):
        engine = db_connect()
        session_job = Session(bind=engine)
        for search_content in SEARCH_CONTENT:
            for c in CITY:
                for page in xrange(1, self.page + 1):
                    url = LAGOU_POSITION_URL + urlencode(self.get_query_string_parameter(c[1]))
                    data = self.get_form_data(page, search_content)
                    # TODO 添加请求头部，模仿浏览器访问
                    headers = {
                        "Accept": "application/json",
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
                        "Cookie": "user_trace_token=20160611162556-63fd5d702fab4eacb4f2f1aff4ae4a0f; LGUID=20160611162556-1e9dc580-2fae-11e6-a334-5254005c3644; pgv_pvi=1623250944; tencentSig=9492166656; JSESSIONID=9BC0D44A5E8CE7B038AA7DD802C884F9; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; index_location_city=%E5%B9%BF%E5%B7%9E; TG-TRACK-CODE=index_search; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1487853509; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1487853607; _ga=GA1.2.1528192005.1465633556; LGSID=20170223203820-f53ed936-f9c4-11e6-9018-5254005c3644; LGRID=20170223203957-2f508a11-f9c5-11e6-9018-5254005c3644; SEARCH_ID=9fcfb815a69843cca653ec937b3e53ce"
                    }
                    json_response = requests.post(url, data, headers=headers).json()
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
        # TODO 更好的正则，或者去掉后面部分可以不?
        m_id = re.match(r"https://www.lagou.com/jobs/(\d+).html", response.url)
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
