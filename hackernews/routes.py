import requests
import json
import pytz
from hackernews import app
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, render_template, request, jsonify, url_for, redirect, session

from flask_sqlalchemy import SQLAlchemy, get_or_404
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime, timezone
from hackernews import app, db
from hackernews.models import News, Admin


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


@app.template_filter('unix_to_datetime')
def unix_to_datetime(timestamp):
    # Convert the Unix timestamp to a datetime object
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    # Format the datetime as a string in the desired format
    formatted_dt = dt.strftime('%Y-%m-%d %H:%M:%S %Z')  # Adjust the format as needed
    return formatted_dt


@app.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    news_items = News.query.paginate(page=page, per_page=10)
    return render_template("home.html", news_items=news_items, session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))


def fetch_news_item(item_id):
    item_url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
    response = requests.get(item_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


@app.route("/execute_fetch")
def fetch_news_items():
    """
    function definition to fetch each news item given an Id. Iterated over by
    newsfeed function. returns json formatted news items.
    """
    api_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    response = requests.get(api_url) 
    if response.status_code == 200:
        news_item_ids = response.json()[:50]
        for item_id in news_item_ids:
            news_item = fetch_news_item(item_id)
            if news_item:
                existing_news_item = News.query.filter_by(id=news_item["id"]).first()
                if (
                    not existing_news_item
                    and all(
                        news_item.get(field) is not None
                        for field in ["title", "by", "url", "type"]
                    )
                    and news_item.get("type") == "story"
                ):
                    try:
                        #inews_time = news_item.get("time", 0)
                        #datetime_value = datetime.utcfromtimestamp(news_time)
     
                        new_news = News(
                            id=news_item["id"],
                            by=news_item.get("by", "Unknown"),
                            title=news_item.get("title", "N/A"),
                            time=news_item.get("time"),
                            url=news_item.get("url", "N/A"),
                            descendants=news_item.get("descendants") if "descendants" in news_item else None,
                            score=news_item.get("score") if "score" in news_item else None,
                            type=news_item.get("type"),
                            deleted=news_item.get("deleted") if "deleted" in news_item else None,
                            dead=news_item.get("dead") if "dead" in news_item else None,
                            parent=news_item.get("parent") if "parent" in news_item else None,
                            text=news_item.get("text") if "text" in news_item else None,
                            kids=json.dumps(news_item.get("kids")) if "kids" in news_item else None
                        )
                        db.session.add(new_news)
                        db.session.commit()
                    except IntegrityError:
                        db.session.rollback()
        return "Nothing to return here"
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
    title = "Newsfeed"
    news_items = News.query.all()
    latest_news_items = sorted(news_items, key=lambda item: item.id, reverse=True)[:30]
    news_json = [item.as_dict() for item in latest_news_items]
    if news_json and news_items:
        return news_json
    return "Nothing to display"


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

@app.route("/account")
def account():
    return render_template("account.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if "new_email" in request.form:
            try:
                new_email = request.form["new_email"]
                new_admin = Admin(email=new_email)
                db.session.add(new_admin)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
            return redirect(url_for("admin"))
        elif "delete" in request.form:
            try:
                email_to_delete = request.form["delete"]
                admin_to_delete = Admin.query.get_or_404(email_to_delete)
                db.session.delete(admin_to_delete)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
            return redirect(url_for("admin"))

    admins = Admin.query.all()
    admin_emails = [admin.email for admin in admins]
    return render_template("admin.html", admins=admins, admin_emails=admin_emails, session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))
