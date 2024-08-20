import os

import certifi
from dotenv import load_dotenv
from fastapi import Depends
from pymongo import MongoClient
from pymongo.database import Database

load_dotenv()

database_url = os.getenv("DATABASE_URL")
database_name = os.getenv("DATABASE_NAME")

mongo = MongoClient(database_url, tlsCAFile=certifi.where())


def get_mongo_database_instance() -> Database:
    return mongo[database_name]


MongoDatabaseDependency = Depends(get_mongo_database_instance)
