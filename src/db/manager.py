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
    def collection(cls, *slots):
        def init(self, **fields):
            for key, value in fields.items():
                if key in slots:
                    setattr(self, key, value)

        def wrapper(model):
            model.__init__ = init
            model.documents = Documents(cls.db[model.__name__.lower()], model)
            return model
        return wrapper


class Documents:
    def __init__(self, collection, model):
        self._collection = collection
        self._model = model

    def insert(self, data):
        logging.info(f'model - {self._model}')
        result = self._collection.insert_one(data)
        logging.info(f'insert - {result}\ninserted_id - {result.inserted_id}')
        return self._model(**data) if result.inserted_id else None

    def delete(self, document):
        delete_query = {'_id': document} if isinstance(document, int) else document
        return self._collection.delete_one(delete_query) 

    def find(self, query):
        return {self._model(**document) for document in self._collection.find(query, self.fields)}

    def values_list(self, query, value):
        return [getattr(document, value) for document in self.find(query)]

    def update(self, query, data):
        return self._collection.replace_one(query, data)
