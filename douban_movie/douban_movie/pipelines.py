# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime

from sqlalchemy.orm import Session

from douban_movie.models import (
    Movie,
    db_connect,
    create_tables,
    session_scope,
)


class MoviePipeline(object):

    def __init__(self):
        engine = db_connect()
        create_tables(engine)
        self.session = Session(bind=engine)

    def process_item(self, item, spider):
        movie = Movie(id=int(item["mid"]),
                      name=item["name"],
                      score=float(item["score"]) if item["score"] != "" else 0.0,
                      star=int(item["star"]),
                      region=item["region"],
                      crawl_time=datetime.utcnow())
        with session_scope(self.session) as session:
            query_count = session.query(Movie).filter_by(id=movie.id).count()
            if query_count < 1:
                session.add(movie)
            elif query_count > 1:
                raise
