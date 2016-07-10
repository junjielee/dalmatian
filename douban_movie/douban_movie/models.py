#!/usr/bin/env python
# encoding: utf-8


from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from contextlib import contextmanager

from douban_movie.settings import DATABASE

Base = declarative_base()

mysql_url = "mysql://{username}:{password}@{host}:{port}/{database}".format(
    username=DATABASE["username"],
    password=DATABASE["password"],
    host=DATABASE["host"],
    port=DATABASE["port"],
    database=DATABASE["database"]
)


class Movie(Base):
    """电影表"""

    __tablename__ = "movie"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    score = Column(Numeric(precision=3, scale=1))
    star = Column(Integer())
    region = Column(String(50))
    crawl_time = Column(DateTime())


def db_connect():
    return create_engine(mysql_url)


def create_tables(engine):
    Base.metadata.create_all(engine)


@contextmanager
def session_scope(session):
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
