""" ALEXA, ASK CRITICS REVIEW """

import logging
import pymongo
import random
import requests
import urllib
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

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

    return r.json()


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


def db_update(entry, data, flag):
    db = CLIENT.alexa
    if flag == 0:
        db.movies.find_one_and_update(
            {"display_title": entry},
            {'$set': {"ratings": data}}
        )
    else:
        db.movies.find_one_and_update(
            {"display_title": entry},
            {'$set': {"genre": data.split(", ")}}
        )


def update_ratings():
    db = CLIENT.alexa

    if db_find_one("Creepy")["ratings"] != None:
       return 0

    movies = db.movies.find()
    for movie in movies:
        title = movie["display_title"]
        if verify_title(title):
            data = omdb_movie_lookup(title)
            if data != None:
                db_update(title, data["Ratings"], 0)
                db_update(title, data["Genre"], 1)


def verify_title(title):
    bad_characters = ["’"]
    for character in bad_characters:
        if character in title:
            return False
    return True


def count_genre():
    db = CLIENT.alexa
    movies = db.movies.find()
    all_genres = {}
    for movie in movies:
        try:
            movie["genre"]
        except KeyError:
            continue
        genres = movie["genre"]
        for genre in genres:
            if genre not in all_genres:
                all_genres[genre] = 1
            else:
                all_genres[genre] += 1
    print(all_genres)


def get_random(genre):
    db = CLIENT.alexa
    movies = db.movies.find()
    movies_set = []
    for movie in movies:
        try:
            movie["genre"]
        except KeyError:
            continue
        if genre in movie["genre"]:
            movies_set.append(movie)

    return random.choice(movies_set)

app = Flask(__name__)
ask = Ask(app, '/')
#logging.getLogger('flask_ask').setLevel(logging.DEBUG)

@ask.launch
def welcome():
    welcome_message = render_template('welcome')
    return question(welcome_message)

@ask.intent('MyGenreChoice', mapping={'genre': 'Genre'})
def genre_call(genre):
    mv = get_random(genre.capitalize())
    movie_prompt = render_template('movie_info', mv=movie["display_name"])
    return question(movie_prompt).simple_card("Movie Selection", movie_prompt)

@ask.intent('AMAZON.CancelIntent')
def cancel():
    return question("cancel")

@ask.intent('AMAZON.NoIntent')
def no():
    return question("no")

@ask.intent('AMAZON.StopIntent')
def stop():
    return question("stop")

@ask.intent('AMAZON.YesIntent')
def yes():
    return question("yes")


if __name__ == '__main__':
    initialize()
    update_ratings()
    app.run(debug=True)

