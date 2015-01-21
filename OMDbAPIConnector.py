#!/usr/local/bin/python

import urllib2, urllib

import datetime

from tvContentRepository import find_all_films, find_all_series

def getDetails(title):
    request = urllib2.Request("http://www.omdbapi.com/?" + title + "&y=&r=json", headers={"Accept" : "application/json"})
    urllib2.urlopen(request).read()


f = find_all_films()
s = find_all_series()

print "films " + str(len(f))
print "series " + str(len(s))

print datetime.datetime.now()
for film in f:
    t = film['title'].strip()
    f = { 't' : t}
    getDetails(urllib.urlencode(f))

for serie in s:
    t = serie['serieTitle'].strip().encode('utf-8')
    f = { 't' : t}
    getDetails(urllib.urlencode(f))

print datetime.datetime.now()






