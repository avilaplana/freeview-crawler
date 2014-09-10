#!/usr/local/bin/python

import urllib2
from tvContentParser import parseToTVContent
from tvChannelParser import parseToTVChannels

from pymongo import MongoClient
import re
from bs4 import BeautifulSoup  # To get everything

# client = MongoClient('localhost', 27017)
# db = client['freeview']
# channelCollection = db['tvChannel']
# channelCollection.drop()
#
# contentCollection = db['tvContent']
# contentCollection.drop()

tv_listing_url = 'http://tvlistings.theguardian.com/'
tv_listing_html_loaded = urllib2.urlopen(tv_listing_url).read()

tv_channels_url = 'http://www.freeview.co.uk/whats-on/channels'
channels_html_loaded = urllib2.urlopen(tv_channels_url).read()
# genre_channel = parseToChannelGenre(listing_tv_html)
soup = BeautifulSoup(channels_html_loaded)
table = soup.body.find('table', {'id': 'wrap-channels-list'})
rows = table.findAll('tr')

for row in rows:
    td = row.findAll('td')

    print "column " + str(td)

# lists = slots.findAll('a', {'href': re.compile('../*')})
# list_channels = parseToTVChannels(channels_html_loaded, tv_listing_html_loaded)

# for channel in list_channels:
#     channel_document = channel.channel_document
#     # print channel_document
#     channelCollection.insert(channel_document)
#     tv_channel_content_url = tv_channels_url + channel.query_parameter
#     channel_information = urllib2.urlopen(tv_channel_content_url).read()
#     tv_content_documents = parseToTVContent(channel_document['name'], channel_information)
#     for tv_content_document in tv_content_documents:
#         # print tv_content_document
#         contentCollection.insert(tv_content_document)











