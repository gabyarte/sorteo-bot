from pymongo import MongoClient
from collections import OrderedDict

from src.settings import *

class MetaDatabaseManager(type):
    @property
    def db(cls):
        return cls.get_db()

class DatabaseManager(metaclass=MetaDatabaseManager):
    _client = None

    @classmethod
    def get_db(cls):
        if cls._client is None:
            cls._client = MongoClient(DB_URI)
        return cls._client

    @classmethod
    def collection(cls, *fields):
        def wrapper(model):
            coll_name = model.__name__.lower()
            model.objects = cls.db.createCollection(coll_name)
            jsonSchema = {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': fields
                }
            }
            cmd = OrderedDict([('collMod', coll_name),
                               ('validator', jsonSchema),
                               ('validationLevel', 'moderate')])
            cls.db.command(cmd)
            return model
        return wrapper
