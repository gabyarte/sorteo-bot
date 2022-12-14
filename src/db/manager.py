import logging

from pymongo import MongoClient
from bson import ObjectId

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
                if key in slots or key == '_id':
                    setattr(self, key, value)

        def wrapper(model):
            model.__init__ = init
            model.documents = Documents(cls.db[model.__name__.lower()], model, slots)
            return model
        return wrapper


class Documents:
    def __init__(self, collection, model, fields):
        self._collection = collection
        self._model = model
        self._fields = fields

    def _to_model(self, documents):
        return (self._model(**document) for document in documents)

    def all(self):
        return self.find({})

    def get(self, _id, key='_id'):
        value = _id if key != '_id' or isinstance(_id, ObjectId) else ObjectId(_id)
        return self._model(**self.find_one({key: value}))

    def insert(self, data):
        result = self._collection.insert_one(data)
        _id = result.inserted_id
        logging.info(f'[MANAGER insert] insert - {result}\ninserted_id - {_id}')
        if _id:
            data.update({'_id': _id})
            return self._model(**data)
        return None

    def get_or_insert(self, query):
        document = self.find_one(query)
        return self._model(**document) if document else self.insert(query)

    def delete(self, document):
        return self._collection.delete_many(document) 

    def find(self, query):
        return self._to_model(self._collection.find(query, self._fields))

    def distinct(self, query, distinct_key):
        return self._collection.distinct(distinct_key, query)

    def update(self, query, data):
        return self._collection.update_many(query, data)

    def count(self, query):
        return self._collection.count_documents(query)

    def __getattr__(self, name):
        return getattr(self._collection, name)
