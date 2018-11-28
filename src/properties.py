import os
import telebot
from flask import Flask
from pymongo import MongoClient

VERSION = "3.5.4"
KNOWN_COMMANDS = ('/start', '/about', '/login', '/me',
                  '/lists', '/caps <insert text>')

LOCAL_ENV = False

if LOCAL_ENV:
    from dev_env import *
else:
    WEBHOOK_URL = 'https://zv-chatbot-hepir.herokuapp.com/'

    # picked up from heroku configs
    PORT = int(os.environ['PORT'])
    TOKEN = os.environ['TOKEN']
    MONGODB_URI = os.environ['MONGODB_URI']
    BOT_USERNAME = os.environ['BOT_USERNAME']
    VIVID_USER = os.environ['VIVID_USER']
    VIVID_PASSWORD = os.environ['VIVID_PASSWORD']

# hardcoded constants because we decided not to use heroku environment variables for these things
MONGODB_COLLECTION = 'users'
# last element at end of URI
MONGODB_DBNAME = MONGODB_URI.split('/')[-1]

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DBNAME]
user_collection = db[MONGODB_COLLECTION]

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
