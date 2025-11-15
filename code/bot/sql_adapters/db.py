from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sql_adapters.models import Base


def init_db(url: str):
    engine = create_engine(url)
    sess_maker = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    return sess_maker