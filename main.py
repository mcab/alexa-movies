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


def main():
    initialize()


if __name__ == '__main__':
    main()

