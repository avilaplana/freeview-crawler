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
    content['start'] = long(start)
    content['end'] = long(end)
    content['typeProgram'] = type_program
    return content

client = MongoClient('localhost', 27017)
db = client['freeview']
channelCollection = db['tvChannel']
channelCollection.drop()

programCollection = db['tvContent']
programCollection.drop()


def print_day_information(channel, data):

    soup = BeautifulSoup(data)
    slots = soup.body.findAll('span',{'class':'tvg_show'})
    for slot in slots:
        a = {}
        a['channel']=channel
        start_time = slot.findAll('span',{'class':'tvg_show_start'})
        a['startTime']=start_time[0].text
        show_title =  slot.findAll('span',{'class':'tvg_show_title'})
        flags =  slot.findAll('span',{'class':'tvg_show_flags'})
        episode_title =  slot.findAll('div',{'class':'tvg_show_episode_title'})
        description = slot.findAll('div',{'class':'tvg_show_description'})

        if len(episode_title) > 0:
            a['serie'] = {}
            a['serie']['title']=show_title[0].text
            if 'Series' in episode_title[0].text and 'Episode' in episode_title[0].text:
                split_episode = episode_title[0].text.split('.')
                season_number = split_episode[0]
                split_episode2 = split_episode[1].split(':')
                episode_number = split_episode2[0]

                a['serie']['seasonNumber']=season_number.split(" ")[1]
                en = episode_number.strip().split(" ")[1].split("/")
                a['serie']['episodeNumber']=en[0]
                a['serie']['totalNumber']=en[1]
                if len(split_episode2) == 2:
                    episode_title2 = split_episode2[1]
                    a['serie']['episodeTitle']= episode_title2
                    programCollection.insert(create_program_document(channel, episode_title2, 0, 1, "serie"))
            else:
                a['serie']['episodeTitle']=episode_title[0].text
                programCollection.insert(create_program_document(channel, episode_title[0].text, 0, 1, "serie"))
        else:
            a['program'] = {}
            a['program']['title']=show_title[0].text
            programCollection.insert(create_program_document(channel, show_title[0].text, 0, 1, "program"))

        if len(flags) > 0:
            a['flags']=flags[0].text
        if len(description) > 0:
            a['description']=description[0].text
        print "--------------"
        print json.dumps(a)
        # collection.insert(a)



tv_source_url = 'http://tvlistings.theguardian.com/text-only'
body_xml = urllib2.urlopen(tv_source_url).read()
# with open('dataset/list_channels.html', 'r') as content_file:
#     body_xml = content_file.read()
soup = BeautifulSoup(''.join(body_xml))
slots = soup.body.find('span', {'id': '_ctl0_main_channelList'})
lists = slots.findAll('a', {'href': re.compile('../*')})

for channel in lists:
    channelCollection.insert(create_channel_document(channel.text, "EN"))
    query_parameter = channel.get('href').replace("..", "")
    url_channel = tv_source_url + query_parameter
    channel_information = urllib2.urlopen(url_channel).read()
    print_day_information(channel.text, channel_information)










