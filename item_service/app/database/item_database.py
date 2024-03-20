from sqlalchemy import create_engine, Column, String,  Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

URL = 'postgresql://secUREusER:StrongEnoughPassword)@51.250.26.59:5432/query'

engine = create_engine(URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class ItemDB(Base):
    __tablename__ = 'items_kolmakov'

    id = Column(Integer, primary_key=True)
    item_name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
