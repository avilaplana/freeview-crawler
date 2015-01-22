#!/usr/local/bin/python

import datetime
from tvContentRepository import find_all_films, find_all_series, aggregate_extra_content
from omdbAPIConnector import getDetails
from parsingLibrary import split_string_by_comma

details_array = []
def _extract_details_by_title(title, id):
    details_content = {}
    details_content['_id'] = id
    details_content['extra'] = getDetails(title)
    return details_content


def extract_tvcontent_array(tvcontents, title_key):
    for t in tvcontents:
     try:
        details = _extract_details_by_title(t[title_key].strip(), t['_id'])
        if 'Error' in details['extra']:
            print t[title_key] + " NOT FOUND"
            continue
        if 'Actors' in details['extra']:
            details['extra']['Actors'] = split_string_by_comma(details['extra']['Actors'])
        if 'Genre' in details['extra']:
            details['extra']['Genre'] = split_string_by_comma(details['extra']['Genre'])
        details_array.append(details)
     except:
         print t[title_key] + " can not be processed"

f = find_all_films()
s = find_all_series()

print "films " + str(len(f))
print "series " + str(len(s))

print "start " + str(datetime.datetime.now())
extract_tvcontent_array(f, 'title')
extract_tvcontent_array(s, 'serieTitle')
print "fetched all the aggreate details " + str(datetime.datetime.now())
for d in details_array:
    aggregate_extra_content(d['_id'], d['extra'])
print "Finish the persistence" + str(datetime.datetime.now())



