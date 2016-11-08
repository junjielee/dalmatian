#!/usr/bin/env python
# -*- coding: utf-8 -*-


from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from contextlib import contextmanager

from job.settings import DATABASE

Base = declarative_base()

mysql_url = "mysql://{username}:{password}@{host}:{port}/{database}".format(
    username=DATABASE["username"],
    password=DATABASE["password"],
    host=DATABASE["host"],
    port=DATABASE["port"],
    database=DATABASE["database"]
)


class Job(Base):
    """工作表"""

    __tablename__ = "job"

    id = Column(Integer, primary_key=True)
    position_id = Column(Integer())
    position_name = Column(String(128))
    position_detail = Column(String(4096))
    address = Column(String(128))
    salary = Column(String(32))
    work_year = Column(String(32))
    create_time = Column(DateTime())
    # create_timestamp = Column(Integer())
    company_id = Column(Integer())
    company_name = Column(String(128))
    company_size = Column(String(128))
    publisher_id = Column(Integer())


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
