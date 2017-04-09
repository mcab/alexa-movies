#!/usr/bin/env python3

"""
Database script that helps us aggregate information.
"""

import pymongo
import requests
import urllib

NYTIMES_API_KEY = None
CLIENT = None

def initialize():
    global NYTIMES_API_KEY, MONGODB_CONNECT, CLIENT

    if not NYTIMES_API_KEY:
        with open('nytimes-key') as nytimes:
            NYTIMES_API_KEY = nytimes.read()

    if not CLIENT:
        with open('mongodb-key') as mongodb:
            CLIENT = pymongo.MongoClient(mongodb)
            try:
                CLIENT.admin.command('ismaster')
            except pymongo.errors.ConnectionFailure:
                print("Server is inaccessible.")

    if db_find_one("Barry"):
        pass
    else:
        for x in range(1, 51):
            db_insert(nytimes_critic_movies(offset=20 * x))


def omdb_movie_lookup(title=""):
    url = "http://www.omdbapi.com/"
    title = urllib.parse.quote_plus(title).replace("%E2%80%99", "%27")
    payload = {"t": title}

    try:
        r = requests.get(url, params=payload)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    if r.json()["Response"] == "False":
        return None

    try:
        r.json()["Ratings"]
    except KeyError:
        return None

    return r.json()["Ratings"]


def nytimes_critic_movies(type="reviews", resource_type="picks", offset="0", order="by-opening-date"):
    url = "http://api.nytimes.com/svc/movies/v2/" + type + "/" + resource_type + ".json"
    payload = {"api-key": NYTIMES_API_KEY, "offset": offset, "order": order}

    try:
        r = requests.get(url, params=payload)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    return r.json()["results"]


def nytimes_search_movies(offset="0", order="by-opening-date", query=""):
    url = "http://api.nytimes.com/svc/movies/v2/reviews/movies.json"
    payload = {"api-key": NYTIMES_API_KEY, "offset": offset, "order": order, "query": query}

    try:
        r = requests.get(url, params=payload)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    return r.json()["results"]


def db_find_one(name):
    db = CLIENT.alexa
    collection = db.movies
    result = collection.find_one({"display_title": name})
    return result


def db_insert(entries):
    db = CLIENT.alexa
    for entry in entries:
        title = entry["display_title"]
        if not db_find_one(title):
            db.movies.insert_one(entry)


def db_update(entry, data):
    db = CLIENT.alexa
    db.movies.find_one_and_update(
        {"display_title": entry},
        {'$set': {"ratings": data}}
    )


def update_ratings():
    db = CLIENT.alexa

    if db_find_one("Barry")["ratings"] != None:
        return 0

    movies = db.movies.find()
    for movie in movies:
        title = movie["display_title"]
        if verify_title(title):
            db_update(title, omdb_movie_lookup(title))


def verify_title(title):
    bad_characters = ["’"]
    for character in bad_characters:
        if character in title:
            return False
    return True


def main():
    initialize()
    update_ratings()


if __name__ == '__main__':
    main()

