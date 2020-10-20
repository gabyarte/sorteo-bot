import logging

from pymongo import MongoClient
from collections import OrderedDict

from src.settings import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


class MetaDatabaseManager(type):
    @property
    def db(cls):
        return cls.get_db()

class DatabaseManager(metaclass=MetaDatabaseManager):
    _db = None

    @classmethod
    def get_db(cls):
        if cls._db is None:
            _client = MongoClient(DB_URI)
            cls._db = _client.sorteo
        return cls._db

    @classmethod
    def collection(cls, *fields):
        def wrapper(model):
            coll_name = model.__name__.lower()
            model.objects = cls.db[coll_name] if coll_name in cls.db.list_collection_names() \
                                              else cls.db.create_collection(coll_name)
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
