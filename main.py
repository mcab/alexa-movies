#!/usr/bin/env python3

"""
Webservice that acts as the glue between Amazon and MongoDB.
"""

import pymongo
import requests
import pprint

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
<<<<<<< HEAD
            MONGODB_CONNECT = True
    print(CLIENT)
=======
            try:
                CLIENT.admin.command('ismaster')
            except pymongo.errors.ConnectionFailure:
                print("Server is inaccessible.")
>>>>>>> origin/master


def nytimes_critic_movies(type="reviews", resource_type="picks", offset="0", order="by-opening-date"):
    url = "http://api.nytimes.com/svc/movies/v2/" + type + "/" + resource_type + ".json"
    payload = {"api-key": NYTIMES_API_KEY, "offset": offset, "order": order}

    try:
        r = requests.get(url, params=payload)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    return r.json()


def nytimes_search_movies(offset="0", order="by-opening-date", query=""):
    url = "http://api.nytimes.com/svc/movies/v2/reviews/movies.json"
    payload = {"api-key": NYTIMES_API_KEY, "offset": offset, "order": order, "query": query}

    try:
        r = requests.get(url, params=payload)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    return r.json()

def db_find_by_name(name):
    with open('mongodb-key') as mongodb:
            CLIENT = pymongo.MongoClient(mongodb)
    db = CLIENT['alexa']
    collection = db.movies
    result = collection.find()
    return result





def db_insert_one(entry):
    if len(entry) != 1:
        raise ValueError("Too many records trying to be put in.")
    title = entry[0]["display_title"]
    information = entry[0]
    db = CLIENT.alexa
    db.movies.count()
    db.movies.insert_one(information)


def main():
    initialize()
<<<<<<< HEAD
    #nytimes_critic_movies()
    #nytimes_search_movies(query="28 days later")   

    print(db_find_by_name("TOY STORY"))
    #   print(item)
    #print(nytimes_search_movies(query="28 days later"))
=======
    nytimes_critic_movies()
    db_insert_one(nytimes_search_movies(query="28 days later")["results"])
    db_insert_one(nytimes_search_movies(query="toy story 3")["results"])
>>>>>>> origin/master


if __name__ == '__main__':
    main()

