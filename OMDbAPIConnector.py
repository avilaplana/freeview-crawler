#!/usr/local/bin/python

import urllib2, urllib
import json

def getDetails(title):
    query_title = { 't' : title}
    query_encoded = urllib.urlencode(query_title)
    request = urllib2.Request("http://www.omdbapi.com/?" + query_encoded + "&y=&r=json", headers={"Accept" : "application/json"})
    return json.loads(urllib2.urlopen(request).read())








