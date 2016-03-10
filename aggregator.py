#!/usr/bin/env python

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
        else:
            content_type[tv_content_key] = []
    else:
        content_type[tv_content_key] = []


def transform_aggregate(content, type_content, aggregate_data):
    aggregate_array_keys = {'Director': 'director', 'Writer': 'writer', 'Actors': 'actors', 'Genre': 'genre',
                            'Country': 'country'}
    aggregate_single_keys = {'Plot': 'plot', 'Language': 'language', 'Year': 'year',
                             'Awards': 'awards', 'Poster': 'posterImdb', 'imdbID': 'imdbId'}

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
            if t["_id"] not in id_aggregator:
                title = t[type_content][key_title]
                aggregate_data = getDetails(title.strip(), type_content)
                if 'Error' in aggregate_data:
                    print t[type_content] + " NOT FOUND"
                    continue
                else:
                    id_aggregator.append(t["_id"])
                    transform_aggregate(t, type_content, aggregate_data)
            # else:
            #     print("%s is already aggregated" % t["_id"])
        except:
            pass


def get_chunks(list, n):
    chunks = []
    for x in range(0, len(list), n):
        chunk = list[x:x + n]
        chunks.append(chunk)
    return chunks


import sys

id_aggregator = []

providers = ['FREEVIEW', 'SKY & CABLE']

for provider in providers:

    print("before aggregator list is")
    print(len(id_aggregator))

    print("Provider is %s" % provider)

    films = find_all_films(provider)
    series = find_all_series(provider)

    print "films " + str(len(films))
    print "series " + str(len(series))

    films_splitted = get_chunks(films, 300)
    series_splitted = get_chunks(series, 300)

    print "start " + str(datetime.datetime.now())

    import threading

    threads = []

    for set_films in films_splitted:
        try:
            print "New thread with %s films" % len(set_films)
            t = threading.Thread(target=extract_tvcontent_array, args=(set_films, 'film', 'title'))
            threads.append(t)
            t.start()
        except:
            print "Unexpected error:", sys.exc_info()[0]
            print "Error: unable to start thread for films"

    for set_series in series_splitted:
        try:
            print "New thread with %s series" % len(set_series)
            t = threading.Thread(target=extract_tvcontent_array, args=(set_series, 'series', 'serieTitle'))
            threads.append(t)
            t.start()
        except:
            print "Unexpected error:", sys.exc_info()[0]
            print "Error: unable to start thread for series"

    for t in threads:
        t.join()

    print("after aggregator list is")
    print(len(id_aggregator))

    for set_films in films_splitted:
        for film in set_films:
            aggregate_extra_content(film)

    for set_series in series_splitted:
        for series in set_series:
            aggregate_extra_content(series)

    print "Finish the persistence" + str(datetime.datetime.now())


