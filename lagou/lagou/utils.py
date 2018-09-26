# -*- coding: utf-8 -*-

import requests
from uuid import uuid4
from fake_useragent import UserAgent


COOKIE = (
    "_ga=GA1.2.1290483677.1527083843; "
    "user_trace_token={0}; "
    "LGUID={1}; "
    "index_location_city=%E5%85%A8%E5%9B%BD; "
    "JSESSIONID={2}; "
    "Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1527083843,1527644950; "
    "Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1527644950; "
    "_gid=GA1.2.149288306.1527644950; "
    "_gat=1; "
    "LGSID={3}; "
    "PRE_UTM=; PRE_HOST=; PRE_SITE=; "
    "PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; "
    "LGRID={4}; "
    "TG-TRACK-CODE=index_search; "
    "SEARCH_ID={5}"
)
ua_obj = UserAgent()


def generate_user_agent():
    return ua_obj.random


def get_proxies_ip():
    try:
        res = requests.get('http://123.207.35.36:5010/get/')
        proxy_ip = res.content
        if ':' not in proxy_ip or '.' not in proxy_ip:
            proxy_ip = None

    except Exception as e:
        print(e)
        proxy_ip = None

    return proxy_ip


def get_uuid():
    return str(uuid4())


def get_cookie():
    cookie = COOKIE.format(get_uuid(), get_uuid(), get_uuid(),
                           get_uuid(), get_uuid(), get_uuid())
    return cookie


def get_ajax_headers():
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,fr;q=0.6",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": generate_user_agent(),
        "Host": "www.lagou.com",
        "Origin": "https://www.lagou.com",
        "Referer": "https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput=",
        # "Cookie": COOKIE,
        "Cookie": get_cookie(),
        "X-Requested-With": "XMLHttpRequest",
    }
    return headers


def get_detail_headers():
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,fr;q=0.6",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": generate_user_agent(),
        "Host": "www.lagou.com",
        "Origin": "https://www.lagou.com",
        # "Cookie": COOKIE,
        "Cookie": get_cookie(),
        "X-Requested-With": "XMLHttpRequest",
    }
    return headers
