#!/usr/local/bin/python

import urllib2
import json

print " aaa "
request = urllib2.Request("http://www.omdbapi.com/?t=Friends&y=&r=json", headers={"Accept" : "application/json"})
series = urllib2.urlopen(request).read()
# data = json.load(series)
print " sss " + str(type(series))