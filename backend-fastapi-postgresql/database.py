from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# URL_DATABASE = 'postgresql://postgres:duje@localhost:5432/web2_projekt1'
URL_DATABASE = 'postgresql://duje:m3noAZUCBMOibRxI1s8r8CuakhdsIpzF@dpg-csf3q6u8ii6s739bb1r0-a.oregon-postgres.render.com/dujejuric_web2_projekt1_baza'

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()