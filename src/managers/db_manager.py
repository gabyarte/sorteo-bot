from pymongo import MongoClient

import settings

class MetaDatabaseManager(type):
    @property
    def db(cls):
        return cls.get_db()

class DatabaseManager(metaclass=type):
    _client, _db = None, None

    @classmethod
    def get_db(cls):
        if cls._client is None:
            cls._client = MongoClient(settings.DB_URI)
            cls._db = cls._client.sorteo
        return cls._db

    @classmethod
    def _insert(cls, table, data):
        collection = cls.db[table]
        return collection.insert_many(data) if isinstance(data, list) else collection.insert_one(data)

    @classmethod
    def create_raffle(cls, data):
        return cls._insert('raffle', data)
