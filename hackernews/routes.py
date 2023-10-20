import requests
import json
import pytz
from hackernews import app
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, render_template, request, jsonify, url_for, redirect, session

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime, timezone
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
    return render_template("home.html", news_items=News.query.all(), session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))


def fetch_news_items():
    """
    function definition to fetch each news item given an Id. Iterated over by
    newsfeed function. returns json formatted news items.
    """
    api_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        news_item_ids = response.json()[:50]
        saved_items=0
        for item_id in news_item_ids:
            item_url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
            response = requests.get(item_url)
            if response.status_code == 200:
                news_item = response.json()
                if news_item:
                    existing_news_item = News.query.filter_by(id=news_item["id"]).first()
                    if not existing_news_item and news_item["title"] and news_item["by"] and news_item["url"] and news_item["type"] == "story":
                        timestamp = news_item.get("time")
                        datetime_value = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                        try:
                            new_news = News(
                                id=news_item["id"],
                                by=news_item.get("by"),
                                title=news_item.get("title"),
                                date=datetime_value.strftime("%Y-%m-%d %H:%M:%S %Z"),
                                url=news_item.get("url"),
                                descendants=news_item.get("descendants")
                            )
                            db.session.add(new_news)
                            saved_items+=1
                            db.session.commit()
                        except IntegrityError:
                            db.session.rollback()
        #print(f"{saved_items} items saved to the database at {datetime.datetime.now()}")
        if news_items:
            return jsonify(news_items)
        return "Hi"
    else:
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
    latest_news_items = sorted(news_items, key=lambda item: item.id, reverse=True)[:30]
    news_json = [item.as_dict() for item in latest_news_items]
    if news_items:
        return news_json
    return "Hi"

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

