# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from lagou.models import update_positions_pid


class LagouPipeline(object):
    def process_item(self, item, spider):
        position_id = item.pop('position_id')
        if not position_id:
            return

        update_positions_pid(position_id, item)
        return item
