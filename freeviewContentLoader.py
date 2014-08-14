#!/usr/local/bin/python

import urllib2
import re
from tvContentParser import parseToTVContent
from bs4 import BeautifulSoup  # To get everything
from pymongo import MongoClient

def create_channel_document(name, language):
    channel = {}
    channel['name'] = name
    channel['language'] = language
    return channel

client = MongoClient('localhost', 27017)
db = client['freeview']
channelCollection = db['tvChannel']
channelCollection.drop()

contentCollection = db['tvContent']
contentCollection.drop()

tv_source_url = 'http://tvlistings.theguardian.com/text-only'
body_xml = urllib2.urlopen(tv_source_url).read()
# with open('dataset/list_channels.html', 'r') as content_file:
#     body_xml = content_file.read()
soup = BeautifulSoup(''.join(body_xml))
slots = soup.body.find('span', {'id': '_ctl0_main_channelList'})
lists = slots.findAll('a', {'href': re.compile('../*')})

for channel in lists:
    channel_document = create_channel_document(channel.text, "EN")
    channelCollection.insert(channel_document)

    query_parameter = channel.get('href').replace("..", "")
    url_channel = tv_source_url + query_parameter
    channel_information = urllib2.urlopen(url_channel).read()
    tv_content_documents = parseToTVContent(channel.text, channel_information)
    for tv_content_document in tv_content_documents:
        contentCollection.insert(tv_content_document)











