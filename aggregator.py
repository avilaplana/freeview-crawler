#!/usr/local/bin/python

import datetime
from tvContentRepository import find_all_films, find_all_series, aggregate_extra_content
from omdbAPIConnector import getDetails
from parsingLibrary import split_string_by_comma

def transform_aggregate(content_type, aggreate_data):
    if 'Director' in aggreate_data:
        content_type['director'] = split_string_by_comma(aggreate_data['Director'])
    if 'Writer' in aggreate_data:
        content_type['writer'] = split_string_by_comma(aggreate_data['Writer'])
    if 'Actors' in aggreate_data:
        content_type['actor'] = split_string_by_comma(aggreate_data['Actors'])
    if 'Genre' in aggreate_data:
        content_type['genre'] = split_string_by_comma(aggreate_data['Genre'])
    if 'Plot' in aggreate_data:
        content_type['plot'] = aggreate_data['Plot']
    if 'Language' in aggreate_data:
        content_type['language'] = aggreate_data['Language']
    if 'Country' in aggreate_data:
        content_type['country'] = aggreate_data['Country']
    if 'imdbRating' in aggreate_data:
        content_type['rating'] = aggreate_data['imdbRating']
    if 'Year' in aggreate_data:
        content_type['year'] = aggreate_data['Year']
    if 'Awards' in aggreate_data:
        content_type['awards'] = aggreate_data['Awards']
    if 'Poster' in aggreate_data:
        content_type['poster'] = aggreate_data['Poster']
    if 'imdbID' in aggreate_data:
        content_type['imdbId'] = aggreate_data['imdbID']


    return content_type


def extract_tvcontent_array(tvcontents, type_content, key_title):
    for t in tvcontents:
     try:
        title = t[type_content][key_title]
        aggregate_data = getDetails(title.strip())
        if 'Error' in aggregate_data:
            print t[type_content] + " NOT FOUND"
            continue
        else:
            transform_aggregate(t[type_content], aggregate_data)
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