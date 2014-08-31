#!/usr/local/bin/python

from bs4 import BeautifulSoup

def parseToChannelGenre(data):

    soup = BeautifulSoup(data)
    slots = soup.body.find('select', {'id': 'tvgChannelsSelect'})
    lists = slots.findAll('option')
    tv_channel_genre = {}
    current_channel_genre = ''
    for element in lists:
        value = element.get('class')[0]
        if 'tvg_channel_genre' == value:
            tv_channel_genre[element.text.upper()] = []
            current_channel_genre = element.text.upper()
        else:
            channelSplitted = element.text.split('-')
            channel = channelSplitted[1].lstrip()
            tv_channel_genre[current_channel_genre].append(channel.upper())


    filter_tv_channel_genre = dict((k, v) for k, v in tv_channel_genre.iteritems() if len(v) > 0)
    return filter_tv_channel_genre









