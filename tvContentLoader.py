#!/usr/local/bin/python

import urllib2
from bs4 import BeautifulSoup
from parsingLibrary import loadHtmlTags, parseChannel, calculate_24_format
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


def calculate_time(time, delta):
    date = datetime(year, month, day, int(time.split('.')[0]), int(time.split('.')[1]))
    date_time = date + timedelta(days = delta)
    tz = pytz.timezone('Europe/London')
    date_uk_time = tz.localize(date_time)
    return date_uk_time


def parse_time(tv_content_html, tv_content, after_noon):
    m = re.search('<div class=\'prog_pre_header\'>(.+?)</div>', tv_content_html['onmouseover'].replace('\\', ''))
    start_hour = m.group(1).split('-')[0]
    end_hour = m.group(1).split('-')[1]
    tv_content['start'] = calculate_24_format(start_hour)
    tv_content['end'] = calculate_24_format(end_hour)


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
    else:
        tv_film_content['title'] = film_title


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

def parse_provider(tag_url):
    return re.match('.*&tabname=(.*)&.*', tag_url).group(1)


def find_content_interval_by_provider(telegraph_url, is_after_noon):
    all_content_html = urllib2.urlopen(telegraph_url).read()

    soup = BeautifulSoup(all_content_html)
    channels_html = soup.findAll("div", {"class": "channel"})

    content_in_interval = {}
    for channel_html in channels_html:
        channel = channel_html.find("div", {"class": "channel_name"}).text
        channel_formatted = parseChannel(channel)
        if channel_formatted in channel_already_crawled:
            continue

        programs = channel_html.findAll("div", {'class': re.compile('programme')})
        for program in programs:
            tv_content = {}
            tv_content["channel"] = channel_formatted
            tv_content["provider"] = parse_provider(tag_url).upper()   
            parse_time(program, tv_content, is_after_noon)
            title = parse_title(program)

            parse_content(program, title, tv_content)
            if not channel_formatted in content_in_interval:
                content_in_interval[channel_formatted] = []
            content_in_interval[channel_formatted].append(tv_content)

    return content_in_interval

def fix_date_in_dat(content_in_channel_provider):
    current_day = False
    after_noon = False
    for content in content_in_channel_provider:
        if not current_day:
            if int(content['start'].split('.')[0]) > 12:
                content['start'] = calculate_time(content['start'], -1)
            else:
                content['start'] = calculate_time(content['start'], 0)
                current_day = True
        else:
            if not after_noon:
                if int(content['start'].split('.')[0]) < 12:
                    content['start'] = calculate_time(content['start'],0)
                else:
                    after_noon = True
                    content['start'] = calculate_time(content['start'], 0)
            else:
                if after_noon:
                    if int(content['start'].split('.')[0]) < 12:
                        content['start'] = calculate_time(content['start'], 1)
                    else:
                        content['start'] = calculate_time(content['start'], 0)

        if not current_day:
            if int(content['end'].split('.')[0]) > 12:
                content['end'] = calculate_time(content['end'], -1)
            else:
                content['end'] = calculate_time(content['end'], 0)
                current_day = True
        else:
            if not after_noon:
                if int(content['end'].split('.')[0]) < 12:
                    content['end'] = calculate_time(content['end'],0)
                else:
                    after_noon = True
                    content['end'] = calculate_time(content['end'],0)
            else:
                if after_noon:
                    if int(content['end'].split('.')[0]) < 12:
                        content['end'] = calculate_time(content['end'],1)
                    else:
                        content['end'] = calculate_time(content['end'],0)

from datetime import datetime

day = datetime.now().day
month = datetime.now().month
year = datetime.now().year

tags = loadHtmlTags(year, month, day, '12am', 'All')
channel_already_crawled = set()
for tag_url in tags:
    if 'Freeview' in tag_url or 'Terrestrial' in tag_url or 'Sky & Cable' in tag_url:
    # if 'Sky & Cable' in tag_url:
        hours = ['12am', '2am', '4am', '6am', '8am', '10am', '12pm', '2pm', '4pm', '6pm', '8pm', '10pm']
        # hours = ['12am']
        all_channels_provider = {}
        for hour in hours:
            url = re.sub('[0-9]*am', hour, tag_url)
            telegraph_url = 'http://tvguideuk.telegraph.co.uk/' + url
            print telegraph_url
            partial_content = find_content_interval_by_provider(telegraph_url,
                                                                'pm' in hour)
            for channel in partial_content:
                if not channel in all_channels_provider:
                    all_channels_provider[channel] = []
                all_channels_provider[channel].extend(partial_content[channel])

        for channel in all_channels_provider:
            channel_already_crawled.add(channel)
            content_in_channel_provider = []
            [content_in_channel_provider.append(x) for x in all_channels_provider[channel] if
             x not in content_in_channel_provider]

            fix_date_in_dat(content_in_channel_provider)
            for content in content_in_channel_provider:
                contentCollection.insert(content)











