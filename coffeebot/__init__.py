import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from coffeebot import config
from coffeebot.models import Base

database_uri = config.DATABASE_URI

print(datetime.datetime.now())
print("Creating database...")
engine = create_engine(database_uri)
Base.metadata.create_all(engine)
print("Successfully created database.")

db_session = sessionmaker(bind=engine)
session = db_session()