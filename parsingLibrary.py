#!/usr/local/bin/python

import urllib2
import re
from bs4 import BeautifulSoup

def loadHtmlTags(year, month, day, time_to_search, tabName):
    date_to_search = str(year) + '-' + str(month) + '-' + str(day)
    telegraph_url = 'http://tvguideuk.telegraph.co.uk/grid.php?&day=' + date_to_search + '&oclock=' + time_to_search + '&tabname=' + tabName
    all_content_html = urllib2.urlopen(telegraph_url).read()

    soup = BeautifulSoup(all_content_html)
    tags_html = soup.findAll("li", {"class": re.compile("tabs")})
    tags = []
    for tag_html in tags_html:
        tags.append(tag_html.find("a")['href'])
    return tags


def parseChannel(channel):
    c_1 = channel.replace('(','')
    c_2 = c_1.replace(')','')
    return c_2.upper()

def remove_duplicate_elements(list_elements):
    unique_set = set()
    uniq = [x for x in list_elements if x not in unique_set and not unique_set.add(x)]
    return uniq


def calculate_24_format(time):
    if 'am' in time:
        time = time.replace('am', '')
        time_hour = int(time.split('.')[0])
        time_minute = time.split('.')[1]
        if time_hour == 12:
            time_hour = time_hour - 12
        return str(time_hour) + '.' + time_minute

    if 'pm' in time:
        time = time.replace('pm', '')
        time_hour = int(time.split('.')[0])
        time_minute = time.split('.')[1]
        if time_hour < 12:
            time_hour = time_hour + 12
        return str(time_hour) + '.' + time_minute

def split_string_by_comma(my_string):
    return [x.strip() for x in my_string.split(',')]
