from flask import Flask
from dotenv import load_dotenv
from os import getenv
from os.path import join as join_path
from flask_pymongo import PyMongo

load_dotenv()

BASE_DIR = getenv('BASE_DIR') or ''

DB_HOST = getenv('DB_HOST') or ''
DB_NAME = getenv('DB_NAME') or ''
DB_URI = join_path(DB_HOST, DB_NAME)

app = Flask('testing')
app.config['MONGO_URI'] = DB_URI
db = PyMongo(app).db


def load():
    from apps.user.views import UserAPI, register_user

    app.add_url_rule('/user', view_func=UserAPI.as_view('user'))

    register_user.methods = ['POST']
    app.add_url_rule('/user/register', view_func=register_user)
