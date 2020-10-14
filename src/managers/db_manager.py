from pymongo import MongoClient

import settings

class DatabaseManager:
    _client = MongoClient(settings.DB_URI)
    _db = _client.sorteo

    @classmethod
    def _insert(cls, table, data):
        collection = cls._db[table]
        return collection.insert_many(data) if isinstance(data, list) else collection.insert_one(data)

    @classmethod
    def create_raffle(cls, data):
        return cls._insert('raffle', data)
