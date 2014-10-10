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


def add_type_to_channel(channels_classified, channels_by_type, key, value):
    for channel in channels_by_type:
        if channel not in channels_classified:
            channels_classified[channel] = {}
            channels_classified[channel][key] = []
            channels_classified[channel][key].append(value)
            channels_classified[channel]['name'] = channel
        else:
            if key in channels_classified[channel]:
                channels_classified[channel][key].append(value)
            else:
                channels_classified[channel][key] = []
                channels_classified[channel][key].append(value)
    return channels_classified


def findChannelClassifed(tags):
    for tag_url in tags:
        # if 'All' in tag_url:
        #     all_channels = getChannels(tag_url)
        if 'Freeview' in tag_url:
            freeview_channels = getChannels(tag_url)
        if 'Terrestrial' in tag_url:
            terrestrial_channels = getChannels(tag_url)
        if 'Sky & Cable' in tag_url:
            cable_all_channels = getChannels(tag_url)
        if 'Films' in tag_url:
            films_channels = getChannels(tag_url)
        if 'Sport' in tag_url:
            sport_channels = getChannels(tag_url)
        if 'News & Doc' in tag_url:
            news_channels = getChannels(tag_url)
        if 'Kids' in tag_url:
            kids_channels = getChannels(tag_url)
        if 'Radio' in tag_url:
            radio_channels = getChannels(tag_url)

    channels_classified = {}
    add_type_to_channel(channels_classified, freeview_channels, "provider", "FREEVIEW")
    add_type_to_channel(channels_classified, terrestrial_channels, "provider", "TERRESTRIAL")
    add_type_to_channel(channels_classified, cable_all_channels, "provider", "SKY & CABLE")

    add_type_to_channel(channels_classified, films_channels, "category", "FILMS")
    add_type_to_channel(channels_classified, sport_channels, "category", "SPORTS")
    add_type_to_channel(channels_classified, news_channels, "category", "NEWS & DOCUMENTARY")
    add_type_to_channel(channels_classified, kids_channels, "category", "KIDS")
    add_type_to_channel(channels_classified, radio_channels, "category", "RADIO")

    return channels_classified


from datetime import datetime

day = datetime.now().day
month = datetime.now().month
year = datetime.now().year

hours = ['12am', '2am', '4am', '6am', '8am', '10am', '12pm', '2pm', '4pm', '6pm', '8pm', '10pm']
channels_classified = {}
for hour in hours:
    tags = loadHtmlTags(year, month, day, hour, 'All')
    channels_classified_temp = findChannelClassifed(tags)
    print '-------- ' + hour
    for channel_temp_classified in channels_classified_temp:
        if channel_temp_classified in channels_classified:
            if channels_classified_temp[channel_temp_classified] != channels_classified[channel_temp_classified]:
                print "--------  DIFFERENT"
                print channels_classified_temp[channel_temp_classified]
                print channels_classified[channel_temp_classified]
        else:
            channels_classified[channel_temp_classified] = channels_classified_temp[channel_temp_classified]
            print channel_temp_classified + ' INSERTED'

for channel in channels_classified:
    channelCollection.insert(channels_classified[channel])