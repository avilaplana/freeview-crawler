#!/usr/local/bin/python

import urllib2
from bs4 import BeautifulSoup
from parsingLibrary import loadHtmlTags, parseChannel

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['freeview']
contentCollection = db['tvContent']
contentCollection.drop()

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
    print tv_content['start']

def parseActors(actors):
    import numpy as np
    array_actors = actors.replace(' and ',', ').split(', ')
    return np.array(array_actors).tolist()


def parse_content(tv_content_html, title, tv_content):
    m = re.search('<div class=\'prog_pre_content\'>(.+?)</div>', tv_content_html['onmouseover'].replace('\\', ''))
    description_html = m.group(1).strip()

    if ('Episode' in description_html and 'Series' in description_html):
        tv_content['series'] = {}
        series(description_html, title, tv_content['series'])
    else:
        if 'FILM: ' in (title):
            tv_content['film'] = {}
            title_film_details(tv_content['film'], title)
            content_details(description_html, tv_content['film'])
        else:
            tv_content['program'] = {}
            tv_content['program']['title'] = title
            content_details(description_html, tv_content['program'])

def parse_series_details(tv_content_series, tv_content_series_html):
    episode_numbers = tv_content_series_html.split('- Episode ')[1]
    if 'of' in episode_numbers:
            episode_nummber = episode_numbers.split(' of ')[0]
            total_number = episode_numbers.split(' of ')[1]
            tv_content_series['episodeNumber'] = episode_nummber
            tv_content_series['totalNumber'] = total_number
    else:
        episode_nummber = episode_numbers.split(' of ')[0]
        tv_content_series['episodeNumber'] = episode_nummber

def series(description_html, serie_title, tv_content_series):

    import re
    description_html_parts = description_html.split('<br /><br /> ')
    episode_html = description_html_parts[0]
    if '<br>' in description_html:
        episode_title = episode_html.split('<br>')[0]
        episode_details_html = episode_html.split('<br>')[1]
        season_number = episode_details_html.split('- Episode ')[0].split('Series ')[1]
        tv_content_series['serieTitle'] = serie_title
        tv_content_series['episodeTitle'] = episode_title
        tv_content_series['seasonNumber'] = season_number.strip()
        parse_series_details(tv_content_series, episode_details_html)
    else: # no episode name
        season_number = episode_html.split('- Episode ')[0].split('Series ')[1]
        tv_content_series['seasonNumber'] = season_number.strip()
        tv_content_series['serieTitle'] = serie_title
        parse_series_details(tv_content_series, episode_html)

    if len(description_html_parts) == 2:
        description = description_html_parts[1]
        a  = re.findall('\. Starring.*',description)
        if len(a) == 0:
            tv_content_series['description'] = description
        else: content_details(description, tv_content_series)

def title_film_details(tv_film_content, title):
    film_title = str(re.sub('FILM: ','',title))
    year_in_parenthesis = re.match('.*(\([0-9]+\))', film_title).group(1)
    tv_film_content['year'] = re.match('\(([0-9]+)\)', year_in_parenthesis).group(1)
    title_without_date = re.sub('(\([0-9]+\))','',film_title)
    tv_film_content['title'] = str(title_without_date)

def content_details(description_html, tv_type_content):
    import re
    if len(description_html) > 0:
        a = re.findall('\. Starring.*',description_html)
        if len(a) > 0:
            tv_type_content['description'] = re.sub('\. Starring.*', '', description_html).strip()
            actors = re.sub('\. Starring ','',a[0])
            tv_type_content['actors'] = parseActors(actors)
        else:
            b = re.findall('\..*, starring.*',description_html)
            if len(b) > 0:
                tv_type_content['description'] = re.sub('\..*, starring.*', '', description_html).strip()
                tv_type_content['category'] = re.match('\. (.*),', b[0].split(' starring ')[0]).group(1).upper()
                ac = b[0].split(' starring ')[1]
                if '.' in ac:
                    actors = re.match('(.*)\..*', ac).group(1)
                    tv_type_content['actors'] = parseActors(actors)

                else:
                    tv_type_content['actors'] = parseActors(ac)
            else: tv_type_content['description'] = description_html.strip()

# { Bug there is no title and it is compulsory
# 	"_id" : ObjectId("5435beb5ad921d5ac0c4c57b"),
# 	"start" : ISODate("2014-10-08T01:00:00Z"),
# 	"end" : ISODate("2014-10-08T01:30:00Z"),
# 	"channel" : "BBC THREE",
# 	"series" : {
# 		"episodeNumber" : "1",
# 		"serieTitle" : "The Revolution Will Be Televised",
# 		"description" : "Dale Maily gets inside the story of guns in America, while James and Barnaby attend a Republican Party Conference",
# 		"actors" : [
# 			"Heydon Prowse",
# 			"Jolyon Rubinstein"
# 		],
# 		"totalNumber" : "6",
# 		"seasonNumber" : "3"
# 	}
# }

def findContent(channels_content_start_time, telegraph_url):
    all_content_html = urllib2.urlopen(telegraph_url).read()

    soup = BeautifulSoup(all_content_html)
    slots = soup.findAll("div", { "class" : "channel" })

    content_in_interval = []

    for slot in slots:
        channel = slot.find("div", { "class" : "channel_name" }).text
        programs = slot.findAll("div", {'class' : re.compile('programme')})

        for program in programs:
            tv_content = {}
            tv_content["channel"] = parseChannel(channel)
            parse_time(program, tv_content)
            title = parse_title(program)
            if title == 'Homes Under the Hammer':
                print 'FOUND'
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

tags = loadHtmlTags(year, month, day, '12am', 'All')

for tag_url in tags:
    if 'All' in tag_url:
        all_content_url = tag_url

hours = ['12am','2am','4am', '6am','8am', '10am','12pm', '2pm', '4pm', '6pm', '8pm', '10pm']
# hours = ['10pm']
# # findContent(year, month, day,'8pm')
channels_contenr_start_time = {}
for hour in hours:
    url = re.sub('[0-9]*am',hour, all_content_url)
    telegraph_url = 'http://tvguideuk.telegraph.co.uk/' + url
    print telegraph_url
    partial_content = findContent(channels_contenr_start_time, telegraph_url)
    for content in partial_content:
        # if 'series' in content and 'category' in content['series']: print content['series']['category']
        # if 'film' in content and 'category' in content['film']: print content['film']['category']
        # if 'program' in content: print content['program']['category']

        contentCollection.insert(content)












