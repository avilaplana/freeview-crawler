#!/usr/local/bin/python

import datetime
from tvContentRepository import find_all_films, find_all_series, aggregate_extra_content
from omdbAPIConnector import getDetails

details_array = []
def extract_details(title_key, tvcontent):
    t = tvcontent[title_key].strip()
    details_content = {}
    details_content['_id'] = tvcontent['_id']
    details_content['extra'] = getDetails(t)
    return details_content



f = find_all_films()
s = find_all_series()

print "films " + str(len(f))
print "series " + str(len(s))

print datetime.datetime.now()

# for film in f:
#     details_array.append(extract_details('title', film))
#
# for serie in s:
#     details_array.append(extract_details('serieTitle', serie))
details_array.append(extract_details('title', f[0]))
for d in details_array:
    print d['_id']
    aggregate_extra_content(d['_id'], d['extra'])


print datetime.datetime.now()



