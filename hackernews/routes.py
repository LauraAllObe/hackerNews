import requests
import json
from hackernews import app
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, render_template, request, jsonify, url_for, redirect, session

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
from hackernews.models import News
from hackernews import db

#configure Authlib to handle application's authentication with Auth0
oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

#global store the json news items (currently all from get news items)
news_items = []

@app.route("/")
def home():
    #return render_template('home.html', news_items=news_items, session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))
    return render_template("home.html", news_items=News.query.all(), session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))


def remove_old():
    items_to_delete = News.query.count() - 30
    oldest_items = News.query.order_by(News.date.asc()).limit(items_to_delete).all()
        for item in oldest_items:
            db.session.delete(item)
            db.session.commit()


def fetch_news_items():
    """
    function definition to fetch each news item given an Id. Iterated over by
    newsfeed function. returns json formatted news items.
    """
    if News.query.count() > 30:
        remove_old()
    api_url = "https://hacker-news.firebaseio.com/v0/newstories.json"
    response = requests.get(api_url)

    if response.status_code == 200:
        news_item_ids = response.json()
        for item_id in news_item_ids:
            item_url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
            response = requests.get(item_url)
            if response.status_code == 200:
                news_item = response.json()
                if news_item:
                    existing_news_item = News.query.filter_by(id=news_item["id"]).first()
                    if not existing_news_item:
                        try:
                            new_news = News(
                                id=news_item["id"],
                                by=news_item.get("by", "Unknown"),
                                title=news_item.get("title", "No Title"),
                                date=news_item.get("time", 0),
                                url=news_item.get("url", "")
                            )
                            db.session.add(new_news)
                            db.session.commit()
                        except IntegrityError:
                            db.session.rollback()
        return None  # No specific error to return
    error_message = f"Failed to fetch newsfeed data. Status code: {response.status_code}"
    print(error_message)
    return error_message, 500


@app.route("/newsfeed")
def newsfeed():
    """
    Function definition to fetch news items, sort them by date, and return the 30 latest 
    news items in JSON format.
    """
    fetch_news_items()
    title = "Newsfeed"
    news_items = News.query.all()
    sorted_news_items = sorted(news_items, key=lambda item: item.date, reverse=True)
    latest_news_items = sorted_news_items[:30]
    news_json = [item.as_dict() for item in latest_news_items]
    return render_template('newsfeed.html', news_json=news_json, title=title)

#place for auth0
@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

#auth0 callback (finished logging in), redirect to home
@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

#auth0 logout, clears session & redirect to home
@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

