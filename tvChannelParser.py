#!/usr/local/bin/python

import re
from bs4 import BeautifulSoup  # To get everything

class Channel:
    def __init__(self, channel, language, channel_query_parameter):
        self.channel_document = {}
        self.channel_document['name'] = channel
        self.channel_document['language'] = language
        self.query_parameter = channel_query_parameter

def parseToTVChannels(data):
    soup = BeautifulSoup(data)
    slots = soup.body.find('span', {'id': '_ctl0_main_channelList'})
    lists = slots.findAll('a', {'href': re.compile('../*')})
    channel_list = []
    for channel in lists:
        query_parameter = channel.get('href').replace("..", "")
        channel_list.append(Channel(channel.text, "EN", query_parameter))

    return channel_list