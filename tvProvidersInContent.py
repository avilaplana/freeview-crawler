#!/usr/local/bin/python

from pymongo import MongoClient
from mongoConfiguration import load_mongo_configuration

mongo_address, mongo_port = load_mongo_configuration()
client = MongoClient(mongo_address, mongo_port)

db = client['freeview']
contentCollection = db['tvContent']
channelCollection = db['tvChannel']
all_channels = channelCollection.find()
for channel in all_channels:
    contentCollection.update({"channel": channel['name']}, {"$set": {"provider": channel['provider']}}, multi=True)


