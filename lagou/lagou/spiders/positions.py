# -*- coding: utf-8 -*-

"""
通过接口，请求所有职位信息
~~~~~~~~~~~~~~~~~~~~~~~
接口链接参数：
    city: 城市名称（中文名）
    needAddtionalResult: 是否需要额外结果(待验证)

body参数：
    first:
    pn: 第几页（1开始）
    kd: 搜索关键词

result结果字段：
    businessZones, companyFullName, companyId, companyLabelList, companyLogo,
    companyShortName, companySize, create_time, district, education,
    financeStage, firstType, formatCreateTime, industryField, industryLables,
    isSchoolJob, jobNature, lastLogin, latitude, longitude, linestaion,
    positionAdvantage, positionId, positionLables, positionName, salary
    secondType, stationname, subwayline, workYear
"""

import requests
from itertools import product
from urllib.parse import urlencode
from lagou.models import new_position
from lagou import utils


#: ajax接口获取职位
LAGOU_POSITION_URL = "https://www.lagou.com/jobs/positionAjax.json"

SEARCH_CONTENT = ["Python", "Go", "后端", "后台", "数据挖掘", "数据", "机器学习"]
CITY = (
    ("beijing", "北京"),
    ("shanghai", "上海"),
    ("guangzhou", "广州"),
    ("shenzhen", "深圳"),
    ("chengdu", "成都"),
)


def get_body_data(cur_page, search_content, first="true"):
    return {
        "first": first,
        "pn": cur_page,
        "kd": search_content
    }


def get_query_string_parameter(city):
    return {
        "needAddtionalResult": "false",
        "city": city,
    }


def request_jobs(city_name, search_content, page, proxy_ip=None):
    """ 发起请求，返回成功，则返回content内容，否则返回None """
    url = "{0}?{1}".format(LAGOU_POSITION_URL, urlencode(get_query_string_parameter(city_name)))
    body_data = get_body_data(page, search_content)

    headers = utils.get_ajax_headers()
    try:
        proxy_ip = utils.get_proxies_ip()
        proxies = {'http': proxy_ip} if proxy_ip else {}
        json_response = requests.post(url, body_data, headers=headers, proxies=proxies).json()
        print('return josn')
        if 'code' not in json_response or int(json_response['code']) != 0:
            # TODO write log
            return None
        return json_response['content']
    except Exception as e:
        # TODO write log
        print(e)
        return None


def get_jobs():
    for elem in product(SEARCH_CONTENT, CITY):
        #: 当前页
        page = 1
        try:
            res = requests.get('http://123.207.35.36:5010/get/')
            proxy_ip = res.content
            if ':' not in proxy_ip or '.' not in proxy_ip:
                proxy_ip = None
        except Exception as e:
            print(e)
            proxy_ip = None

        while page:

            content = request_jobs(elem[1][1], elem[0], page, proxy_ip)
            if content is None:
                break

            page = content['pageNo']
            #: 每页数
            page_size = content['pageSize']
            #: 当前页面职位数量
            # cur_page_size = content['positionResult']['resultSize']
            #: 总职位数
            total_size = content['positionResult']['totalCount']

            results = content['positionResult']['result']
            for r in results:
                # 根据positionId判断是否已经存在这个职位，没有则创建记录 if not is_position_exist(r['positionId']):
                position_data = struct_data(r)
                new_position(position_data)

            # 解析返回的结果，如果每一页的结果小于page_size，则设置page=0
            if page * page_size > total_size:
                page = 0
            else:
                page += 1


def struct_data(content):
    """ 构建数据库键值对参数 """
    result = {}
    data_keys = [
        'businessZones', 'companyFullName', 'companyId', 'companyLabelList', 'companyLogo',
        'companyShortName', 'companySize', 'create_time', 'district', 'education',
        'financeStage', 'firstType', 'formatCreateTime', 'industryField', 'industryLables',
        'isSchoolJob', 'jobNature', 'lastLogin', 'latitude', 'longitude', 'linestaion',
        'positionAdvantage', 'positionId', 'positionLables', 'positionName', 'salary'
        'secondType', 'stationname', 'subwayline', 'workYear',
    ]
    for dk in data_keys:
        if dk in {'businessZones', 'companyLabelList', 'industryLables', 'positionLables'}:
            result[dk] = content.get(dk, [])
        elif dk in {'companyId', 'lastLogin', 'positionId', 'publisherId'}:
            result[dk] = int(content.get(dk, 0))
        else:
            result[dk] = content.get(dk, '')

        return result


if __name__ == "__main__":
    content = request_jobs("广州", "Python", 1)
    if content is None:
        print('fuck')
    else:
        print(content)
