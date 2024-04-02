from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import declarative_base

import conf

db_conf = conf.db_conf
Base = declarative_base()

engine = create_engine(
    f'mysql+pymysql://{db_conf["username"]}:{db_conf["password"]}@{db_conf["host"]}:{db_conf["port"]}/{db_conf["database"]}?charset=utf8mb4',
    max_overflow=0,
    pool_size=5,
    pool_timeout=10,
    pool_recycle=1,
    echo=False
)

Session = sessionmaker(bind=engine)
session = scoped_session(Session)


class NodeConf(Base):
    __tablename__ = 'NodeConf'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(255))


if __name__ == '__main__':
    Base.metadata.create_all(engine)
