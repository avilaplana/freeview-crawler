#!/usr/local/bin/python

import urllib2
from tvContentParser import parseToTVContent
from tvChannelParser import parseToTVChannels
from tvChannelGenreParser import parseToChannelGenre
from tvContentGenreParser import parseToContentGenre

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['freeview']
channelCollection = db['tvChannel']
channelCollection.drop()

genreChannelCollection = db['tvChannelGenre']
genreChannelCollection.drop()

contentCollection = db['tvContent']
contentCollection.drop()

genreContentCollection = db['tvContentGenre']
genreContentCollection.drop()



tv_listing_url = 'http://tvlistings.theguardian.com/'
tv_listing_html_loaded = urllib2.urlopen(tv_listing_url).read()

tv_channels_url = 'http://tvlistings.theguardian.com/text-only'
channels_html_loaded = urllib2.urlopen(tv_channels_url).read()
genre_channel_list = parseToChannelGenre(tv_listing_html_loaded)
list_channels = parseToTVChannels(channels_html_loaded, genre_channel_list)
all_tv_content_genres = set()
for channel in list_channels:
    channel_document = channel.channel_document
    # print channel_document
    channelCollection.insert(channel_document)
    tv_channel_content_url = tv_channels_url + channel.query_parameter
    channel_information = urllib2.urlopen(tv_channel_content_url).read()
    tv_content_documents = parseToTVContent(channel_document['name'], channel_information)
    for tv_content_document in tv_content_documents:
        # print tv_content_document
        contentCollection.insert(tv_content_document)
    tv_content_genres_channel = parseToContentGenre(tv_content_documents)
    all_tv_content_genres = all_tv_content_genres.union(tv_content_genres_channel)

for genre_channel in genre_channel_list.keys():
     genre_channel_dict = {}
     genre_channel_dict['genre'] = genre_channel
     genreChannelCollection.insert(genre_channel_dict)

for genre_content in all_tv_content_genres:
     genre_content_dict = {}
     genre_content_dict['genre'] = genre_content
     genreContentCollection.insert(genre_content_dict)














