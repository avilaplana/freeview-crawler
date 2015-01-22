#!/usr/local/bin/python
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['freeview']
contentCollection = db['tvContent']

def _find_all(type, title):
    films = contentCollection.find({type: { "$exists": True }})
    films_array = []
    for film in films:
        film_reduced = {}
        film_reduced[title] = film[type][title]
        film_reduced["_id"] = film["_id"]
        films_array.append(film_reduced)
    return films_array

def find_all_films():
    return _find_all("film", "title")

def find_all_series():
    return _find_all("series", "serieTitle")

def aggregate_extra_content(id, extra):
    contentCollection.update({"_id":id},{"$set": {"extra": extra}}, multi = True)
