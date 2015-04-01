#!/usr/local/bin/python

import datetime
from tvContentRepository import find_all_films, find_all_series, aggregate_extra_content
from omdbAPIConnector import getDetails
from parsingLibrary import split_string_by_comma

def transform_property(aggregate_key, tv_content_key, aggregate_data, content_type):
     if aggregate_key in aggregate_data:
        if "N/A" not in aggregate_data[aggregate_key]:
            content_type[tv_content_key] = aggregate_data[aggregate_key]

def transform_array(aggregate_key, tv_content_key, aggregate_data, content_type):
     if aggregate_key in aggregate_data:
         if "N/A" not in aggregate_data[aggregate_key]:
            content_type[tv_content_key] = split_string_by_comma(aggregate_data[aggregate_key])
         else: content_type[tv_content_key]  = []
     else: content_type[tv_content_key]  = []

def transform_aggregate(content, type_content, aggregate_data):

    aggregate_array_keys = {'Director':'director','Writer' : 'writer','Actors' : 'actors','Genre' : 'genre', 'Country' : 'country'}
    aggregate_single_keys = {'Plot' : 'plot', 'Language' : 'language','Year' : 'year',
                             'Awards' : 'awards', 'Poster' : 'poster', 'imdbID' : 'imdbId'}

    for aggregate_key in aggregate_array_keys:
        transform_array(aggregate_key, aggregate_array_keys[aggregate_key], aggregate_data, content[type_content])

    for aggregate_key in aggregate_single_keys:
        transform_property(aggregate_key, aggregate_single_keys[aggregate_key], aggregate_data, content[type_content])

    if "N/A" not in aggregate_data['imdbRating']:
        try:
            content['rating'] = float(aggregate_data['imdbRating'])
        except:
            print 'Error parsing to float:' + aggregate_data['imdbRating']


def extract_tvcontent_array(tvcontents, type_content, key_title):
    for t in tvcontents:
     try:
        title = t[type_content][key_title]
        aggregate_data = getDetails(title.strip(), type_content)
        if 'Error' in aggregate_data:
            print t[type_content] + " NOT FOUND"
            continue
        else:
            transform_aggregate(t, type_content, aggregate_data)
     except:
          print title + " can not be processed"

films = find_all_films()
series = find_all_series()

print "films " + str(len(films))
print "series " + str(len(series))

print "start " + str(datetime.datetime.now())
extract_tvcontent_array(films, 'film', 'title')
extract_tvcontent_array(series, 'series', 'serieTitle')
print "fetched all the aggreate details " + str(datetime.datetime.now())
for f in films + series:
    aggregate_extra_content(f)

print "Finish the persistence" + str(datetime.datetime.now())