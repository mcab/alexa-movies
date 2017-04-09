#!/usr/bin/env python3

"""
Database script that helps us aggregate information.
"""

import pymongo
import requests

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


def omdb_movie_lookup(title=""):
    url = "http://www.omdbapi.com/"
    payload = {"t": title.replace(" ", "+")}

    try:
        r = requests.get(url, params=payload)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

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


def main():
    initialize()
    db_insert(nytimes_critic_movies())
    db_insert(nytimes_search_movies(query="28 days later"))
    db_insert(nytimes_search_movies(query="toy story 3"))
    db_update("Toy Story 3", omdb_movie_lookup("toy story 3"))


if __name__ == '__main__':
    main()

