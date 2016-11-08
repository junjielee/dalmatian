# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy.orm import Session

from job.models import (
    Job,
    db_connect,
    create_tables,
    session_scope,
)


class JobPipeline(object):

    def __init__(self):
        engine = db_connect()
        create_tables(engine)
        self.session = Session(bind=engine)

    def process_item(self, item, spider):
        job = Job(
            position_id=int(item["position_id"]),
            position_name=item["position_name"].encode('utf-8'),
            position_detail=item["position_detail"].encode('utf-8'),
            address=item["address"].encode('utf-8'),
            salary=item["salary"].encode('utf-8'),
            work_year=item["work_year"].encode('utf-8'),
            create_time=item["create_time"],
            company_id=item["company_id"],
            company_name=item["company_name"].encode('utf-8'),
            company_size=item["company_size"].encode('utf-8'),
            publisher_id=item["publisher_id"],
        )
        with session_scope(self.session) as session:
            query_count = session.query(Job).filter_by(position_id=job.position_id).count()
            if query_count < 1:
                session.add(job)
            elif query_count > 1:
                raise
