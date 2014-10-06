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

