from flask import Flask
from dotenv import load_dotenv
from os import getenv as get_env, getcwd as get_current_directory
from os.path import join as join_path
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from datetime import timedelta
from logging import handlers
import logging

load_dotenv()

APP_NAME = get_env('APP_NAME') or 'testing'
SECRET_KEY = get_env('SECRET_KEY') or ''
BASE_DIR = get_env('BASE_DIR') or get_current_directory()

DB_HOST = get_env('DB_HOST') or ''
DB_NAME = get_env('DB_NAME') or ''
DB_URI = join_path(DB_HOST, DB_NAME)

JWT_HEADER_TYPE = get_env('JWT_HEADER_TYPE') or ''
JWT_EXPIRATION_DELTA = timedelta(days=int(get_env('JWT_EXPIRATION_DELTA_IN_DAYS') or 1))

DEV_ENVIRONMENT = get_env('DEV_ENVIRONMENT') or ''
PRD_ENVIRONMENT = get_env('PRD_ENVIRONMENT') or ''
CURRENT_ENVIRONMENT = get_env('FLASK_ENV') or ''

CERT_FILE_NAME = get_env('CERT_FILE_NAME') or ''
CERT_FILE_PATH = join_path(BASE_DIR, CERT_FILE_NAME)
KEY_FILE_NAME = get_env('KEY_FILE_NAME') or ''
KEY_FILE_PATH = join_path(BASE_DIR, KEY_FILE_NAME)

LOG_FILE_RELATIVE_PATH = get_env('LOG_FILE_RELATIVE_PATH') or 'logs/general.log'
LOG_FILE_PATH = join_path(BASE_DIR, LOG_FILE_RELATIVE_PATH)
LOG_FILE_MAX_BYTES = 10485760  # 10 Mib
LOGGER = logging.getLogger(APP_NAME)


app = Flask(APP_NAME)
app.config['MONGO_URI'] = DB_URI
app.config['SECRET_KEY'] = SECRET_KEY
app.config['JWT_HEADER_TYPE'] = JWT_HEADER_TYPE
app.config['JWT_EXPIRATION_DELTA'] = JWT_EXPIRATION_DELTA
db = PyMongo(app).db
JWTManager(app)


def config_logging():
    global LOGGER
    LOGGER.handlers.clear()
    file_handler = handlers.RotatingFileHandler(LOG_FILE_PATH, maxBytes=LOG_FILE_MAX_BYTES, backupCount=5)
    date_time_format = '%Y-%m-%d %H:%M:%S'  # YYYY-MM-DD HH:MM:SS
    formatter = logging.Formatter('%(asctime)s|%(levelname)s| %(message)s', datefmt=date_time_format)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    LOGGER.addHandler(file_handler)
    LOGGER.addHandler(console_handler)
    LOGGER.setLevel(logging.INFO)


def load():
    config_logging()

    from apps.user.views import (get_users, register_user,
                                 authenticate, check_login, exchange_for_tokens,
                                 check_response, login_with_google)

    check_login.methods = ['GET']
    app.add_url_rule('/check', view_func=check_login)

    authenticate.methods = ['GET']
    app.add_url_rule('/auth', view_func=authenticate)

    get_users.methods = ['GET']
    app.add_url_rule('/user', view_func=get_users)

    register_user.methods = ['POST']
    app.add_url_rule('/user/register', view_func=register_user)

    app.add_url_rule('/login-via-google', view_func=login_with_google)
    app.add_url_rule('/token-exchange', view_func=exchange_for_tokens)

    check_response.methods = ['GET']
    app.add_url_rule('/check-response', view_func=check_response)

