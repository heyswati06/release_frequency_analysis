"""MongoDB connection helper"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(MONGO_URI)
        _db = _client[MONGO_DB]
    return _db

def get_collection(name):
    return get_db()[name]
