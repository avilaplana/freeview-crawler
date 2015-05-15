#!/usr/bin/env python

import urllib2, urllib
import json

def getDetails(title, type_content = 'none'):
    if type_content == 'series':
        type = '&type=series'
    else:
        if type_content == 'film':
            type = '&type=movie'
        else:
            print "Type " + type_content + " unknown"
            type = ''

    query_title = { 't' : title.encode('utf-8')}
    query_encoded = urllib.urlencode(query_title)
    request = urllib2.Request("http://www.omdbapi.com/?" + query_encoded + "&y=&r=json" + type, headers={"Accept" : "application/json"})
    return json.loads(urllib2.urlopen(request).read())


