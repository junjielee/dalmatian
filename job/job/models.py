# -*- coding: utf-8 -*-

"""
job.models
~~~~~~~~~~

使用Sqlalchemy模块，定义表格模型
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from contextlib import contextmanager

from job.settings import DATABASE

#: 创建Mapper对象基类
Base = declarative_base()

mysql_url = "mysql://{username}:{password}@{host}:{port}/{database}?charset=utf8".format(
    username=DATABASE["username"],
    password=DATABASE["password"],
    host=DATABASE["host"],
    port=DATABASE["port"],
    database=DATABASE["database"]
)


class Job(Base):
    """工作表对象"""

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

    def __repr__(self):
        return "<Job(position_name='{position}', company_name='{company}')>".format(
            position=self.position_name, company=self.company_name
        )


def db_connect():
    """初始化数据库连接"""

    return create_engine(mysql_url)


def create_tables(engine):
    """创建表格模式信息到数据库

    会先检查表格是否存在，若存在，则不会CREATE
    """

    Base.metadata.create_all(engine)


@contextmanager
def session_scope(session):
    """session上下文管理器"""

    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
