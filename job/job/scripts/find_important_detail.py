#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
job.scripts.find_import_detail
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

对职位的详细描述做分词，对关键词的次数排序
"""

import MySQLdb
import jieba
import string

from collections import defaultdict


IGNORE = ["\t", "\n", "\r", ".", "(", ")", "，", "。", "（", "）", "：", "；", " ", "、", "和", "等", "有", "的", " "]
IGNORE.extend(list(string.digits))

db = MySQLdb.connect("localhost", "", "", "")


def get_pure_detail(position_detail):
    for i in IGNORE:
        position_detail = position_detail.replace(i, "").lower()

    return position_detail


if __name__ == "__main__":
    words = defaultdict(int)

    cursor = db.cursor()
    cursor.execute("SELECT * from job")

    for c in cursor:
        detail = get_pure_detail(c[3].strip(" \t\r\n"))
        for s in jieba.cut(detail):
            words[s] += 1

    word_items = sorted(words.items(), key=lambda x: x[1], reverse=True)

    for item in word_items[:50]:
        print item[0], item[1]

    db.close()
