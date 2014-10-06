#!/usr/local/bin/python

import urllib2
from bs4 import BeautifulSoup
from parsingLibrary import loadHtmlTags, parseChannel
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['freeview']
channelCollection = db['tvChannel']
channelCollection.drop()


def getChannels(url):
    url_channels = 'http://tvguideuk.telegraph.co.uk/' + url
    print url
    a = BeautifulSoup(urllib2.urlopen(url_channels).read())
    channels = a.findAll("div", {"class": "channel_name"})
    list_channels = []
    for channel in channels:
        list_channels.append(channel.text)
    return list_channels

def findChannelClassifed(tags):
    for tag_url in tags:
        if 'All' in tag_url:
            all_channels = getChannels(tag_url)
        if 'Freeview' in tag_url:
            freeview_channels = getChannels(tag_url)
        if 'Terrestrial' in tag_url:
            terrestrial_channels = getChannels(tag_url)
        if 'Sky & Cable' in tag_url:
            cable_all_channels = getChannels(tag_url)

    channels_classified = []
    for channel in all_channels:
        channel_u = parseChannel(channel)
        channel_provided_by = {}
        channel_provided_by['name'] = channel_u
        channel_provided_by['provider'] = []
        if channel in freeview_channels:
            channel_provided_by['provider'].append("FREEVIEW")
        if channel in terrestrial_channels:
            channel_provided_by['provider'].append("TERRESTRIAL")
        if channel in cable_all_channels:
            channel_provided_by['provider'].append("SKY-CABLE")
        channels_classified.append(channel_provided_by)

    return channels_classified

from datetime import datetime

day = datetime.now().day
month = datetime.now().month
year = datetime.now().year

tags = loadHtmlTags(year, month, day, '12am', 'All')
channels_classified = findChannelClassifed(tags)
for channel in channels_classified:
    channelCollection.insert(channel)













