"""
Webservice that acts as the glue between Amazon and MongoDB.
"""

import pymongo
import requests

NYTIMES_API_KEY = None
MONGODB_CONNECT = False
CLIENT = None

def initialize():
    global NYTIMES_API_KEY, MONGODB_CONNECT, CLIENT

    if not NYTIMES_API_KEY:
        with open('nytimes-key') as nytimes:
            NYTIMES_API_KEY = nytimes.read()

    if not MONGODB_CONNECT:
        with open('mongodb-key') as mongodb:
            CLIENT = pymongo.MongoClient(mongodb)
            MONGODB_CONNECT = True


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


def main():
    initialize()
    nytimes_critic_movies()
    nytimes_search_movies(query="28 days later")


if __name__ == '__main__':
    main()

