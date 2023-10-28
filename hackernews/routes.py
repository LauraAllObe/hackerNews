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
from hackernews import app, db
from hackernews.models import News, Admin, User, disLikes
import logging


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


app.logger.setLevel(logging.ERROR)  # Set the minimum log level to write to the file

# Create a FileHandler to write logs to a file
file_handler = logging.FileHandler("/home/lauraallobe/hackerNews/hackernews/error.log")
app.logger.addHandler(file_handler)


#global store the json news items (currently all from get news items)
news_items = []


@app.template_filter('unix_to_datetime')
def unix_to_datetime(timestamp):
    # Convert the Unix timestamp to a datetime object
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    # Format the datetime as a string in the desired format
    formatted_dt = dt.strftime('%Y-%m-%d %H:%M:%S %Z')  # Adjust the format as needed
    return formatted_dt


def calculate_like_count(news_id):
    like_count = disLikes.query.filter(disLikes.newsId == news_id, disLikes.liked == True).count()
    return like_count


def calculate_dislike_count(news_id):
    dislike_count = disLikes.query.filter(disLikes.newsId == news_id, disLikes.liked == False).count()
    return dislike_count

def get_vote_color(news_id, click, needUrl, isLike):
    token = None
    userinfo = None
    if session.get('user'):
        token = session.get('user')
        if token.get('userinfo'):
            userinfo = token.get('userinfo')
    existing_vote = None
    if token and userinfo:
        current_user = User.query.filter_by(email=userinfo.get('email')).first()
        existing_vote = disLikes.query.filter_by(newsId=news_id, userId=current_user.id).first()
    
    if existing_vote != None:# and click != isLike:
        if existing_vote.liked == isLike:
            if existing_vote.liked == True:
                if needUrl == True:
                    return "https://drive.google.com/uc?id=1hbRpgYvIUnqQQMs7XcZ0iAYd-x6Sfuxt"
                else:
                    return "#652525"
            elif isLike == False:
                if needUrl == True:
                    return "https://drive.google.com/uc?id=1SLvPE0JxqZCLdjKHHy9Rk2IT37C-Lupi"
                else:
                    return "#652525"
        elif existing_vote.liked != isLike:
            if isLike == True:
                if needUrl == True:
                    return "https://drive.google.com/uc?id=1YdJMSLQbmVxhA_w-GCxIljy-z9piaIHC"
                else:
                    return "#5f4747"
            elif isLike == False:
                if needUrl == True:
                    return "https://drive.google.com/uc?id=1ieW0zHZrqfPyaW7XU1pjoWAfaZ-FQABZ"
                else:
                    return "#5f4747"
    else:
        if isLike == True:
            if needUrl == True:
                return "https://drive.google.com/uc?id=1YdJMSLQbmVxhA_w-GCxIljy-z9piaIHC"
            else:
                return "#5f4747"
        else:
            if needUrl == True:
                return "https://drive.google.com/uc?id=1ieW0zHZrqfPyaW7XU1pjoWAfaZ-FQABZ"
            else:
                return "#5f4747"


def changeVotes(click, current_news_id):
    token = None
    userinfo = None
    if session.get('user'):
        token = session.get('user')
        if token.get('userinfo'):
            userinfo = token.get('userinfo')
    existing_vote = None
    if token and userinfo:
        current_user = User.query.filter_by(email=userinfo.get('email')).first()
        existing_vote = disLikes.query.filter_by(newsId=current_news_id, userId=current_user.id).first()
        if click == True and current_user:
            if existing_vote != None and existing_vote.liked == True:
                existing_vote.liked = None
            elif existing_vote != None and (existing_vote.liked == None or existing_vote.liked == False):
                existing_vote.liked = True
            else:
                existing_vote=disLikes(
                    id=disLikes.query.count()+1,
                    userId=current_user.id,
                    newsId=current_news_id,
                    liked=True
                )
                db.session.add(existing_vote)
        elif click == False and current_user:
            if existing_vote != None and existing_vote.liked == False:
                existing_vote.liked = None
            elif existing_vote != None and (existing_vote.liked == None or existing_vote.liked == True):
                existing_vote.liked = False
            else:
                existing_vote=disLikes(
                    id=disLikes.query.count()+1,
                    userId=current_user.id,
                    newsId=current_news_id,
                    liked=False
                )
                db.session.add(existing_vote)
        if current_user:
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
    return None


@app.route("/", methods=["GET", "POST"])
def home():
    page = request.args.get('page', 1, type=int)
    news_items = News.query.paginate(page=page, per_page=10)
    click = {news_item.id: False for news_item in news_items.items}
    if request.method == "POST":
        action = request.form.get("action")
        current_news_id = request.form.get("news_item_id")
        app.logger.error("action: %s\n current_news_id: %s\n", str(action), str(current_news_id))
        if action:
            if action == "like":
                changeVotes(True, current_news_id)
                #click[current_news_id] = True
            elif action == "dislike":
                changeVotes(False, current_news_id)
                #click[current_news_id] = False
    like_image_url = {news_item.id: get_vote_color(news_item.id, click[news_item.id], True, True) for news_item in news_items.items}
    like_font_color = {news_item.id: get_vote_color(news_item.id, click[news_item.id], False, True) for news_item in news_items.items}
    dislike_image_url = {news_item.id: get_vote_color(news_item.id, click[news_item.id], True, False) for news_item in news_items.items}
    dislike_font_color = {news_item.id: get_vote_color(news_item.id, click[news_item.id], False, False) for news_item in news_items.items}
    admins = Admin.query.all()
    admin_emails = [admin.email for admin in admins]
    like_count = {news_item.id: calculate_like_count(news_item.id) for news_item in news_items.items}
    dislike_count = {news_item.id: calculate_dislike_count(news_item.id) for news_item in news_items.items}
    users=User.query.all()
    return render_template("home.html", users=users, like_font_color=like_font_color, like_image_url=like_image_url, dislike_font_color=dislike_font_color,dislike_image_url=dislike_image_url, like_count=like_count, dislike_count=dislike_count, admin_emails=admin_emails, news_items=news_items, session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))


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
    if session.get('user'):
        addUser(token)
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
    admins = Admin.query.all()
    admin_emails = [admin.email for admin in admins]
    users = User.query.all()
    return render_template("account.html", users=users, admin_emails=admin_emails, session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if "new_email" in request.form:
            try:
                new_email = request.form["new_email"]
                new_admin = Admin(email=new_email)
                db.session.add(new_admin)
                db.session.commit()
                user_to_update = User.query.filter_by(email=new_email).first()
                if user_to_update:
                    user_to_update.admin = True
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
                user_to_update = User.query.filter_by(email=email_to_delete).first()
                if user_to_update:
                    user_to_update.admin = False
                    db.session.commit()
            except IntegrityError:
                db.session.rollback()
            return redirect(url_for("admin"))

    admins = Admin.query.all()
    admin_emails = [admin.email for admin in admins]
    users = User.query.all()
    return render_template("admin.html", users=users, admins=admins, admin_emails=admin_emails, session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

def addUser(token):
    userinfo = token.get('userinfo')
    add_email = "N/A"
    add_name = "N/A"
    add_nickname = None
    if userinfo.email:
        add_email = userinfo.email
    if userinfo.name:
        add_name = userinfo.name
    if userinfo.nickname:
        add_nickname = userinfo.nickname
    user_exists = User.query.filter_by(email=userinfo.get("email")).first()
    admin_exists = Admin.query.filter_by(email=userinfo.get("email")).first()
    new_user = []
    if admin_exists:
        new_user = User(
            id=User.query.count()+1,
            email=add_email,
            name=add_name,
            admin=True,
            nickname=add_nickname
        )
    else:
        new_user = User(
            id=User.query.count()+1,
            email=add_email,
            name=add_name,
            admin=False,
            nickname=add_nickname
        )
    if not user_exists:
        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            app.logger.error("IntegrityError: %s", str(e))
            app.logger.error("Id: %s\nEmail: %s\nName: %s\nAdmin: %s\nNickname: %s\n", str(new_user.id), str(new_user.email), str(new_user.name), str(new_user.admin), str(new_user.nickname))
            db.session.rollback()
    return None
