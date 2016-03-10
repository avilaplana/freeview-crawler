#!/usr/bin/env python
from pymongo import MongoClient
from mongoConfiguration import load_mongo_configuration

mongo_address, mongo_port = load_mongo_configuration()
client = MongoClient(mongo_address, mongo_port)

db = client['freeview']
contentCollection = db['tvContent']

def _find_all(type, provider):
    co = contentCollection.find({"provider": { "$in": [provider]} ,type: { "$exists": True }})
    content = []
    for c in co:
        content.append(c)
    return content

def find_all_films(provider):
    return _find_all("film", provider)

def find_all_series(provider):
    return _find_all("series", provider)

def aggregate_extra_content(aggregate):
    contentCollection.update({'_id':aggregate['_id']}, {"$set": aggregate}, upsert=False)