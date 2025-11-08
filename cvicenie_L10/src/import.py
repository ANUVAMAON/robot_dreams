import pandas as pd
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
collection = db["mycollection"]


def import_data_from_mongo(query={}, projection=None):
    """
    Import data from MongoDB collection into a pandas DataFrame
    """
    cursor = collection.find(query, projection)
    data = list(cursor)
    return pd.DataFrame(data)
