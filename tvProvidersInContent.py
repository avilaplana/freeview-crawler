#!/usr/local/bin/python

from datetime import timedelta
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['freeview']
contentCollection = db['tvContent']
channelCollection = db['tvChannel']
all_channels = channelCollection.find()
for channel in all_channels:
    contentCollection.update({"channel":channel['name']},{"$set": {"provider":channel['provider']}}, multi = True)


