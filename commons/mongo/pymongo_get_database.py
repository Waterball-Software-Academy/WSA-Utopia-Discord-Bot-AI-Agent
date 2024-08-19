import os
from typing import Any, Mapping

import certifi
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

load_dotenv()


def get_database() -> Database[Mapping[str, Any] | Any]:
    database_url = os.getenv("DATABASE_URL")
    database_name = os.getenv("DATABASE_NAME")

    client = MongoClient(database_url, tlsCAFile=certifi.where())

    return client[database_name]


if __name__ == "__main__":
    dbname = get_database()
