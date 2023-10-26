import requests
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, render_template, request, jsonify, url_for, redirect, session

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
import logging

#auth0 .env file recognition
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)

app.logger.setLevel(logging.ERROR)  # Set the minimum log level to write to the file

# Create a FileHandler to write logs to a file
file_handler = logging.FileHandler("/home/lauraallobe/hackerNews/hackernews/error.log")
app.logger.addHandler(file_handler)

#set auth0 secret key
app.secret_key = env.get("APP_SECRET_KEY")
#app.config['SECRET_KEY'] = '8fa763ec394817a3c0e382b5a5f3470be1f295204990741a92f7aaf1ed06f75a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


from hackernews import routes
