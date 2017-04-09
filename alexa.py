import database
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

app = Flask(__name__)
ask = Ask(app, '/')

@ask.launch
def welcome():
    welcome_message = render_template('welcome')
    return statement(welcome).simple_card('Welcome to Movie Information.')

@ask.intent('YesIntent')
def look_up():
    text = render_template('hello', firstname=firstname)
    return statement(text).simple_card('Hello', text)

if __name__ == '__main__':
    app.run(debug=True)