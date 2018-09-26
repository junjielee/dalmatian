# -*- coding: utf-8 -*-

from pymongo import MongoClient


mongo_client = MongoClient(host='localhost', port=27017)
lagou_collection = mongo_client['positions']['lagou']


def new_position(pdata):
    """ 更新职位信息，如果不存在，则创建 """
    if not is_position_exist(pdata['positionId']):
        lagou_collection.insert(pdata)
        return True

    return False


def is_position_exist(pid):
    """ 根据positionId判断职位是否已存在 """
    result = lagou_collection.find_ond({"positionId": pid})
    if result:
        return True

    return False


def find_positions_not_detail():
    result = lagou_collection.find({"$or": [{"positionDetail": {"$ne": ""}}, {"positionDetail": {"$exists": False}}]},
                                   {"positionId": True})

    return result


def update_positions_pid(position_id, params):
    lagou_collection.update({"positionId": position_id}, {"$set": params})
