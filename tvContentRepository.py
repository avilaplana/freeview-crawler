#!/usr/local/bin/python
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['freeview']
contentCollection = db['tvContent']

def _find_all(type):
    co = contentCollection.find({"provider": { "$in": ["FREEVIEW"]} ,type: { "$exists": True }})
    content = []
    for c in co:
        content.append(c)
    return content

def find_all_films():
    return _find_all("film")

def find_all_series():
    return _find_all("series")

def aggregate_extra_content(aggregate):
    contentCollection.update({'_id':aggregate['_id']}, {"$set": aggregate}, upsert=False)