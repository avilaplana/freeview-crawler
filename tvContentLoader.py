#!/usr/local/bin/python

import urllib2
from bs4 import BeautifulSoup
from parsingLibrary import loadHtmlTags, parseChannel
from datetime import timedelta
from pymongo import MongoClient
import pytz

client = MongoClient('localhost', 27017)
db = client['freeview']
contentCollection = db['tvContent']
contentCollection.drop()

import re


def parse_title(tv_content_html):
    m = re.search('<div class=\'prog_header\'>(.+?)</div>', tv_content_html['onmouseover'].replace('\\', ''))
    return m.group(1)


def parse_time(tv_content_html, tv_content, after_noon):
    m = re.search('<div class=\'prog_pre_header\'>(.+?)</div>', tv_content_html['onmouseover'].replace('\\', ''))
    start_hour = m.group(1).split('-')[0]
    end_hour = m.group(1).split('-')[1]
    start = str(month) + ' ' + str(day) + ' ' + str(year) + ' ' + start_hour
    end = str(month) + ' ' + str(day) + ' ' + str(year) + ' ' + end_hour
    start_datetime = datetime.strptime(start, '%m %d %Y %I.%M%p')
    end_datetime = datetime.strptime(end, '%m %d %Y %I.%M%p')

    if not after_noon and 'pm' in start_hour and 'am' in end_hour:
        start_datetime = start_datetime - timedelta(days = 1)
    else:
        if after_noon and 'pm' in start_hour and 'am' in end_hour:
            end_datetime = end_datetime + timedelta(days = 1)
        else:
            if after_noon and 'am' in start_hour and 'am' in end_hour:
                start_datetime = start_datetime + timedelta(days = 1)
                end_datetime = end_datetime + timedelta(days = 1)

    tz = pytz.timezone('Europe/London')
    tv_start_uk_time = tz.localize(start_datetime)
    tv_end_uk_time = tz.localize(start_datetime)
    tv_content['start'] = tv_start_uk_time
    tv_content['end'] = tv_end_uk_time

def parse_actors(actors):
    import numpy as np

    array_actors = actors.replace(' and ', ', ').split(', ')
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
    else:  # no episode name
        season_number = episode_html.split('- Episode ')[0].split('Series ')[1]
        tv_content_series['seasonNumber'] = season_number.strip()
        tv_content_series['serieTitle'] = serie_title
        parse_series_details(tv_content_series, episode_html)

    if len(description_html_parts) == 2:
        description = description_html_parts[1]
        a = re.findall('\. Starring.*', description)
        if len(a) == 0:
            tv_content_series['description'] = description
        else:
            content_details(description, tv_content_series)

def title_film_details(tv_film_content, title):
    film_title = re.sub('FILM: ', '', title)
    if '(' in film_title and ')' in film_title:
        year_in_parenthesis = re.match('.*(\([0-9]+\))', film_title).group(1)
        tv_film_content['year'] = re.match('\(([0-9]+)\)', year_in_parenthesis).group(1)
        title_without_date = re.sub('(\([0-9]+\))', '', film_title)
        tv_film_content['title'] = title_without_date
    else: tv_film_content['title'] = film_title

def content_details(description_html, tv_type_content):
    import re

    if len(description_html) > 0:
        a = re.findall('\. Starring.*', description_html)
        if len(a) > 0:
            tv_type_content['description'] = re.sub('\. Starring.*', '', description_html).strip()
            actors = re.sub('\. Starring ', '', a[0])
            tv_type_content['actors'] = parse_actors(actors)
        else:
            b = re.findall('\..*, starring.*', description_html)
            if len(b) > 0:
                tv_type_content['description'] = re.sub('\..*, starring.*', '', description_html).strip()
                tv_type_content['category'] = re.match('\. (.*),', b[0].split(' starring ')[0]).group(1).upper()
                ac = b[0].split(' starring ')[1]
                if '.' in ac:
                    actors = re.match('(.*)\..*', ac).group(1)
                    tv_type_content['actors'] = parse_actors(actors)

                else:
                    tv_type_content['actors'] = parse_actors(ac)
            else:
                tv_type_content['description'] = description_html.strip()

def find_content(channels_content_start_time, telegraph_url, is_after_noon):
    all_content_html = urllib2.urlopen(telegraph_url).read()

    soup = BeautifulSoup(all_content_html)
    slots = soup.findAll("div", {"class": "channel"})

    content_in_interval = []
    for slot in slots:
        channel = slot.find("div", {"class": "channel_name"}).text
        programs = slot.findAll("div", {'class': re.compile('programme')})

        for program in programs:
            tv_content = {}
            tv_content["channel"] = parseChannel(channel)
            parse_time(program, tv_content, is_after_noon)
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

tags = loadHtmlTags(year, month, day, '12am', 'All')
channels_contenr_start_time = {}
for tag_url in tags:
    if 'Freeview' in tag_url or 'Terrestrial' in tag_url or 'Sky & Cable' in tag_url:
        hours = ['12am', '2am', '4am', '6am', '8am', '10am', '12pm', '2pm', '4pm', '6pm', '8pm', '10pm']
        # hours = ['12am']
        for hour in hours:
            url = re.sub('[0-9]*am', hour, tag_url)
            telegraph_url = 'http://tvguideuk.telegraph.co.uk/' + url
            print telegraph_url
            partial_content = find_content(channels_contenr_start_time, telegraph_url, 'pm' in hour)

            for content in partial_content:
                contentCollection.insert(content)












