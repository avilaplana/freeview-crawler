#!/usr/local/bin/python

import urllib2
import re
import json
from bs4 import BeautifulSoup  # To get everything
from pymongo import MongoClient

def create_channel_document(name, language):
    channel = {}
    channel['name'] = name
    channel['language'] = language
    return channel

def create_program_document(channel, program, start, end, type_program):
    content = {}
    content['channelName'] = channel
    content['programName'] = program
    content['start'] = start
    content['end'] = end
    content['typeProgram'] = type_program
    return content

client = MongoClient('localhost', 27017)
db = client['freeview']
channelCollection = db['tvChannel']
channelCollection.drop()

programCollection = db['tvContent']
programCollection.drop()

url = 'http://tvlistings.theguardian.com/text-only'
body_xml = urllib2.urlopen(url).read()
# with open('dataset/list_channels.html', 'r') as content_file:
#     body_xml = content_file.read()
soup = BeautifulSoup(''.join(body_xml))
slots = soup.body.find('span', {'id': '_ctl0_main_channelList'})
lists = slots.findAll('a', {'href': re.compile('../*')})

for channel in lists:
    channelCollection.insert(create_channel_document(channel.text, "EN"))










