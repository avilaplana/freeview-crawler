#!/usr/local/bin/python

def parseToContentGenre(all_tv_content):
    tv_content_genre = set()
    for tv_content in all_tv_content:
        tv_content_genre = tv_content_genre.union(tv_content["category"])
    return tv_content_genre