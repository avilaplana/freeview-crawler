#!/usr/local/bin/python

import urllib2
from tvContentParser import parseToTVContent
from tvChannelParser import parseToTVChannels
from tvChannelGenreParser import parseToChannelGenre
from tvContentGenreParser import parseToContentGenre
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['freeview']
# channelCollection = db['tvChannel']
# channelCollection.drop()
#
# genreChannelCollection = db['tvChannelGenre']
# genreChannelCollection.drop()
#
contentCollection = db['tvContent']
contentCollection.drop()
#
# genreContentCollection = db['tvContentGenre']
# genreContentCollection.drop()

import re

def parse_title(tv_content_html):
    m = re.search('<div class=\'prog_header\'>(.+?)</div>', tv_content_html['onmouseover'].replace('\\', ''))
    return m.group(1)

def parse_time(tv_content_html, tv_content):
    m = re.search('<div class=\'prog_pre_header\'>(.+?)</div>', tv_content_html['onmouseover'].replace('\\', ''))
    start = str(month) + ' ' + str(day) + ' ' + str(year) + ' ' + m.group(1).split('-')[0]
    end = str(month) + ' ' + str(day) + ' ' + str(year) + ' ' + m.group(1).split('-')[1]
    tv_content['start'] = datetime.strptime( start, '%m %d %Y %I.%M%p')
    tv_content['end'] = datetime.strptime( end, '%m %d %Y %I.%M%p')

def parseActors(actors):
    import numpy as np
    array_actors = actors.replace(' and ',', ').split(', ')
    return np.array(array_actors).tolist()


def parse_content(tv_content_html, title, tv_content):
    m = re.search('<div class=\'prog_pre_content\'>(.+?)</div>', tv_content_html['onmouseover'].replace('\\', ''))
    match = m.group(1)

    if ('Episode' in match and 'Series' in match):
        series(match, title, tv_content)
    else:
        if 'FILM: ' in (title):
            tv_content['film'] = {}
            title_film_details(tv_content['film'], title)
            content_details(match, tv_content['film'])
        else:
            tv_content['program'] = {}
            tv_content['program']['title'] = title
            content_details(match, tv_content['program'])

def parse_series_details(tv_content_series, tv_content_series_html):
    if 'of' in tv_content_series_html.split('- Episode ')[1]:
            episode_nummber = tv_content_series_html.split('- Episode ')[1].split(' of ')[0]
            total_number = tv_content_series_html.split('- Episode ')[1].split(' of ')[1]
            tv_content_series['episodeNumber'] = episode_nummber
            tv_content_series['totalNumber'] = total_number
    else:
        episode_nummber = tv_content_series_html.split('- Episode ')[1].split(' of ')[0]
        tv_content_series['episodeNumber'] = episode_nummber

def series(match, serie_title, tv_content):

    import re
    tv_content['series'] = {}
    if '<br>' in match:
        episode_title = match.split('<br /><br /> ')[0].split('<br>')[0]
        season_number = match.split('<br /><br /> ')[0].split('<br>')[1].split('- Episode ')[0].split('Series ')[1]
        tv_content['series']['serieTitle'] = serie_title
        tv_content['series']['episodeTitle'] = episode_title
        tv_content['series']['seasonNumber'] = season_number
        parse_series_details(tv_content['series'], match.split('<br /><br /> ')[0].split('<br>')[1])
    else:
        season_number = match.split('<br /><br /> ')[0].split('- Episode ')[0].split('Series ')[1]
        tv_content['series']['seasonNumber'] = season_number
        parse_series_details(tv_content['series'], match.split('<br /><br /> ')[0])

    description = match.split('<br /><br /> ')[1]
    a  = re.findall('\. Starring.*',description)
    if len(a) == 0:
        tv_content['series']['description'] = description
    else: content_details(description, tv_content['series'])

def title_film_details(tv_film_content, title):
    film_title = str(re.sub('FILM: ','',title))
    year_in_parenthesis = re.match('.*(\([0-9]+\))', film_title).group(1)
    tv_film_content['year'] = re.match('\(([0-9]+)\)', year_in_parenthesis).group(1)
    title_without_date = re.sub('(\([0-9]+\))','',film_title)
    tv_film_content['title'] = str(title_without_date)

def content_details(match, tv_type_content):
    import re
    if len(match) > 0:
        a = re.findall('\. Starring.*',match)
        if len(a) > 0:
            tv_type_content['description'] = re.sub('\. Starring.*', '', match)
            actors = re.sub('\. Starring ','',a[0])
            tv_type_content['actors'] = parseActors(actors)
        else:
            b = re.findall('\..*, starring.*',match)
            if len(b) > 0:
                tv_type_content['description'] = re.sub('\..*, starring.*', '', match)
                tv_type_content['category'] = re.match('\. (.*),', b[0].split(' starring ')[0]).group(1)
                ac = b[0].split(' starring ')[1]
                if '.' in ac:
                    actors = re.match('(.*)\..*', ac).group(1)
                    tv_type_content['actors'] = parseActors(actors)

                else:
                    tv_type_content['actors'] = parseActors(ac)
            else: tv_type_content['description'] = match



def findContent(year, month, day, time_to_search, channels_content_start_time, tabName = 'All'):
    date_to_search = str(year) + '-' + str(month) + '-' + str(day)
    telegraph_url = 'http://tvguideuk.telegraph.co.uk/grid.php?&day=' + date_to_search + '&oclock='+ time_to_search + '&tabname=' + tabName
    print telegraph_url
    all_content_html = urllib2.urlopen(telegraph_url).read()

    soup = BeautifulSoup(all_content_html)
    slots = soup.findAll("div", { "class" : "channel" })

    content_in_interval = []

    for slot in slots:
        channel = slot.find("div", { "class" : "channel_name" }).text
        programs = slot.findAll("div", {'class' : re.compile('programme')})

        for program in programs:
            tv_content = {}
            tv_content["channel"] = channel
            parse_time(program, tv_content)
            title = parse_title(program)
            parse_content(program, title, tv_content)
            if channel in channels_content_start_time:
                if tv_content['start'] not in channels_content_start_time[channel]:
                    channels_content_start_time[channel].append(tv_content['start'])
                    content_in_interval.append(tv_content)
                # else: print 'duplicated ' + str(tv_content)
            else:
                channels_content_start_time[channel] = []
                channels_content_start_time[channel].append(tv_content['start'])
                content_in_interval.append(tv_content)

    return content_in_interval

from datetime import datetime

day = datetime.now().day
month = datetime.now().month
year = datetime.now().year

hours = ['12am','2am','4am', '6am','8am', '10am','12pm', '2pm', '4pm', '6pm', '8pm', '10pm']
# hours = ['8pm', '10pm']
# findContent(year, month, day,'8pm')
channels_contenr_start_time = {}
content_in_interval = []
for hour in hours:
    print "------------------------" + hour
    partial_content = findContent(year, month, day, hour, channels_contenr_start_time)
    for content in partial_content:
        contentCollection.insert(content)












