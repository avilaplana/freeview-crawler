#!/usr/local/bin/python

import re
from bs4 import BeautifulSoup  # To get everything


class Channel:
    def __init__(self, channel, language, channel_query_parameter, genre):
        self.channel_document = {}
        self.channel_document['name'] = channel.upper()
        self.channel_document['genre'] = genre
        self.channel_document['language'] = language
        self.query_parameter = channel_query_parameter

def findGenreByChannel(channel, genre_channel):
    for genre in genre_channel:
        if channel.upper() in genre_channel[genre]:
            return genre
    return "ENTERTAINMENT"

def parseToTVChannels(channel_html, genre_channel_list):
    soup = BeautifulSoup(channel_html)
    slots = soup.body.find('span', {'id': '_ctl0_main_channelList'})
    lists = slots.findAll('a', {'href': re.compile('../*')})
    channel_list = []
    for channel in lists:
        query_parameter = channel.get('href').replace("..", "")
        genre = findGenreByChannel(channel.text, genre_channel_list)
        channel_list.append(Channel(channel.text, "EN", query_parameter, genre))

    return channel_list