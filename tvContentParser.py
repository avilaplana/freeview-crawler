#!/usr/local/bin/python

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

def parseDateTime(startTime):
    hour = int(startTime.split(':')[0])
    minute = int(startTime.split(':')[1])
    tv_start_time = datetime.now().replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
    tz = pytz.timezone('Europe/London')
    tv_start_uk_time = tz.localize(tv_start_time)

    return tv_start_uk_time


def parseSerie(episode_title, serie_title, tv_content, description, category):
    tv_content['serie'] = {}
    tv_content['serie']['serieTitle'] = serie_title

    if len(description) > 0:
        category_joined = '/'.join(category)
        tv_content['serie']['description'] = description[0].text.replace(category_joined, '.')
    if 'Series' in episode_title and 'Episode' in episode_title:
        split_episode = episode_title.split('.')
        season_number = split_episode[0]
        split_episode2 = split_episode[1].split(':')
        episode_number = split_episode2[0]

        tv_content['serie']['seasonNumber']=season_number.split(" ")[1]
        en = episode_number.strip().split(" ")[1].split("/")
        tv_content['serie']['episodeNumber']=en[0]
        tv_content['serie']['totalNumber']=en[1]
        if len(split_episode2) == 2:
            episode_title2 = split_episode2[1]
            tv_content['serie']['episodeTitle']= episode_title2
        else:
            tv_content['serie']['episodeTitle']= serie_title
    else:
        tv_content['serie']['episodeTitle'] = episode_title

def parseProgram(program_title, tv_content, description, category):
    tv_content['program'] = {}
    tv_content['program']['title'] = program_title
    if len(description) > 0:
        category_joined = '/'.join(category)
        tv_content['program']['description'] = description[0].text.replace(category_joined, '.')

def parseCategory(category):
    return category.split('/')

def parseAccessibility(tv_content, flags):
    if len(flags) > 0:
        tv_content["accessibility"] = []
        if "SUB" in flags:
            tv_content["accessibility"].append("Subtitles")
        if "AD" in flags:
            tv_content["accessibility"].append("Audio described")
        if "HD" in flags:
            tv_content["accessibility"].append("High definition")
        # if "BW" in flags: //TODO find out what this is
        #     tv_content["accessibility"].append("highDefinition")

def parseToTVContent(channel, data):

    soup = BeautifulSoup(data)
    slots = soup.body.findAll('span',{'class':'tvg_show'})
    programs = []

    for slot in slots:
        tv_content = {}
        tv_content['channel'] = channel

        start_time = slot.findAll('span',{'class':'tvg_show_start'})
        start_date_time = parseDateTime(start_time[0].text)
        tv_content['startTime']= start_date_time
        end_date_time = (datetime.now() + timedelta(days=1)).replace(hour=2, minute=0, second=0, microsecond=0)
        tv_content['endTime'] = end_date_time

        show_title =  slot.findAll('span',{'class':'tvg_show_title'})
        episode_title =  slot.findAll('div',{'class':'tvg_show_episode_title'})

        category = slot.findAll('span',{'class':'tvg_show_category'})
        if len(category) > 0:
            tv_content['category'] = parseCategory(category[0].text)

        description = slot.findAll('div',{'class':'tvg_show_description'})
        if len(episode_title) > 0:
            parseSerie(episode_title[0].text, show_title[0].text, tv_content, description, tv_content['category'])
        else:
            parseProgram(show_title[0].text, tv_content, description, tv_content['category'])

        flags =  slot.findAll('span',{'class':'tvg_show_flags'})
        if len(flags) > 0:
            parseAccessibility(tv_content, flags[0].text)
            # tv_content['flags'] = flags[0].text



        programs.append(tv_content)

        if (len(programs) > 1):
            programs[len(programs) - 2]['endTime'] = programs[len(programs) - 1]['startTime']

    return programs


