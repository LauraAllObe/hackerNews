"""
This file handles all the routes and related functions
"""
import json
import logging
from datetime import datetime, timezone
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from flask import render_template, request, url_for, redirect, session, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, func, case
import requests
from hackernews import app, db
from hackernews.models import News, Admin, User, Vote


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


app.logger.setLevel(logging.ERROR)
file_handler = logging.FileHandler("/home/lauraallobe/hackerNews/hackernews/error.log")
app.logger.addHandler(file_handler)


@app.template_filter('unix_to_datetime')
def unix_to_datetime(timestamp):
    """Formats timestamp in UTC.
    Args:
        timestamp: Integer value of time
    Kwargs: N/A
    Returns: timestamp as formatted string.
    Raises: N/A
    """
    if timestamp == "N/A":
        return timestamp
    if timestamp is not None:
        date_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        formatted_dt = date_time.strftime('%Y-%m-%d %H:%M:%S %Z')
        return formatted_dt
    timestamp = "N/A"
    return timestamp


def calculate_like_count(news_id):
    """Calculates likes for one news item.
    Args:
        news_id: news item id.
    Kwargs: N/A
    Returns: like count.
    Raises: N/A
    """
    like_count = Vote.query.filter(Vote.news_id == news_id, Vote.liked == True) \
            .count()
    return like_count


def calculate_dislike_count(news_id):
    """Calculates dislikes for one news item.
    Args:
        news_id: news item id.
    Kwargs: N/A
    Returns: like count.
    Raises: N/A
    """
    dislike_count = Vote.query.filter(Vote.news_id == news_id, Vote.liked == False)\
            .count()
    return dislike_count


def get_vote_color_two(existing_vote, is_like, need_image):
    """Gets dislike and like button and text
    color and image name.
    Args:
        existing_vote: boolean value of existing vote
        need_image: boolean True if image name
        is needed, False if color is needed.
        is_like: boolean True if is like, False
        if is dislike.
    Returns: string of color in hex or image name.
    Raises: N/A
    """
    image_or_color = ""
    if existing_vote.liked == is_like:
        if existing_vote.liked is True and need_image is True:
            image_or_color = "red_thumbs_up.png"
        elif existing_vote.liked is True:
            image_or_color = "#652525"
        elif is_like is False and need_image is True:
            image_or_color = "red_thumbs_down.png"
        elif is_like is False:
            image_or_color = "#652525"
    elif existing_vote.liked != is_like:
        if is_like is True:
            if need_image is True:
                image_or_color = "thumbs_up.png"
            else:
                image_or_color = "#5f4747"
        if is_like is False:
            if need_image is True:
                image_or_color = "thumbs_down.png"
            else:
                image_or_color = "#5f4747"
    return image_or_color


def get_vote_color(news_id, need_image, is_like):
    """Gets dislike and like button and text
    color and image name.
    Args:
        news_id: news item id
        need_image: boolean True if image name
        is needed, False if color is needed.
        is_like: boolean True if is like, False
        if is dislike.
    Returns: string of color in hex or image name.
    Raises: N/A
    """
    token = None
    userinfo = None
    if session.get('user'):
        token = session.get('user')
        if token.get('userinfo'):
            userinfo = token.get('userinfo')
    existing_vote = None
    if token and userinfo:
        current_user = User.query.filter_by(email=userinfo.get('email')).first()
        if current_user is not None:
            existing_vote = Vote.query.filter_by(news_id=news_id, user_id=current_user.id).first()    
    if existing_vote is not None:
        return get_vote_color_two(existing_vote, is_like, need_image)
    get_image_or_color = ""
    if is_like is True and need_image is True:
        get_image_or_color = "thumbs_up.png"
    elif is_like is True:
        get_image_or_color = "#5f4747"
    elif need_image is True:
        get_image_or_color = "thumbs_down.png"
    else:
        get_image_or_color = "#5f4747"
    return get_image_or_color


def change_votes(click, current_news_id):
    """Add or update likes and dislikes to database.
    Args:
        click: boolean True if clicked like and
        False if clicked dislike.
        current_news_id: Integer id of the news
        item that was liked or disliked.
    Kwargs: N/A
    Returns: None
    Raises:
        IntegrityError: if commit, add, or delete
        to database fails.
    """
    token = None
    userinfo = None
    existing_vote = None
    if session.get('user'):
        token = session.get('user')
        userinfo = token.get('userinfo')
        current_user = User.query.filter_by(email=userinfo.get('email')).first()
        if current_user is not None:
            existing_vote = Vote.query.filter_by(news_id=current_news_id, \
                    user_id=current_user.id).first()
        if click is True and current_user:
            if existing_vote is not None and existing_vote.liked is True:
                existing_vote.liked = None
            elif existing_vote is not None and existing_vote.liked in (None, False):
                existing_vote.liked = True
            else:
                existing_vote=Vote(
                    user_id=current_user.id,
                    news_id=current_news_id,
                    liked=True
                )
                db.session.add(existing_vote)
        elif click is False and current_user:
            if existing_vote is not None and existing_vote.liked is False:
                existing_vote.liked = None
            elif existing_vote is not None and existing_vote.liked in (None, True):
                existing_vote.liked = False
            else:
                existing_vote=Vote(
                    user_id=current_user.id,
                    news_id=current_news_id,
                    liked=False
                )
                db.session.add(existing_vote)
        if current_user is not None:
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


@app.route("/", methods=["GET", "POST"])
def home():
    """renders / route and appropriately calls
    functions on POST methods.
    Args: N/A
    Kwargs: N/A
    Returns: rendered home.html template given
    the paginated and sorted news items, admin
    emails, users, auth0 user information accessors
    session and pretty, and dictionaries of key
    news item ids to value forbutton  image names,
    button colors, and like and dislike counts.
    Raises: N/A
    """
    page = request.args.get('page', 1, type=int)
    if request.method == "POST":
        page = request.form.get("page", type=int)
        app.logger.error("page: %d\n", page)
    
    likes_dislikes_subq = Vote.query.with_entities(
        Vote.news_id.label('news_id'),
        func.coalesce(func.sum(case((Vote.liked == True, 1), else_=0)), 0).label('total_likes'),
        func.coalesce(func.sum(case((Vote.liked == False, 1), else_=0)), 0).label('total_dislikes')
    ).group_by(Vote.news_id).subquery()

    news_items = News.query.join(
        likes_dislikes_subq, likes_dislikes_subq.c.news_id == News.id
    ).order_by(
        desc(likes_dislikes_subq.c.total_likes),
        desc(likes_dislikes_subq.c.total_dislikes),
        desc(News.time)
    ).paginate(page=page, per_page=10)
    #news_items = News.query \
    #.order_by(desc(News.time)) \
    #.paginate(page=page, per_page=10)
    if request.method == "POST":
        action = request.form.get("action")
        current_news_id = request.form.get("news_item_id")
        app.logger.error("action: %s\n current_news_id: %s\n", \
                str(action), str(current_news_id))
        if action:
            if action == "like":
                change_votes(True, current_news_id)
                app.logger.error("got to like")
            elif action == "dislike":
                change_votes(False, current_news_id)
                app.logger.error("got to dislike, news_id is %d\n", str(current_news_id))
    admins = Admin.query.all()
    admin_emails = [admin.email for admin in admins]
    like_count = {news_item.id: calculate_like_count(news_item.id) \
            for news_item in news_items.items}
    dislike_count = {news_item.id: calculate_dislike_count(news_item.id) \
            for news_item in news_items.items}
    users=User.query.all()
    for news in news_items.items:
        app.logger.error("id: %s\nby: %s\ntime: %s\ntitle: %s\nurl: %s\n\n", \
                str(news.id), str(news.by), str(news.time), \
                str(news.title), str(news.url))
    like_image_url = {news.id: get_vote_color(news.id, True, True) \
            for news in news_items.items}
    like_font_color = {news.id: get_vote_color(news.id, False, True) \
            for news in news_items.items}
    dislike_image_url = {news.id: get_vote_color(news.id, True, False) \
            for news in news_items.items}
    dislike_font_color = {news.id: get_vote_color(news.id, False, False) \
            for news in news_items.items}
    return render_template("home.html", users=users, like_font_color=like_font_color, \
            like_image_url=like_image_url, dislike_font_color=dislike_font_color, \
            dislike_image_url=dislike_image_url, like_count=like_count, \
            dislike_count=dislike_count, admin_emails=admin_emails, \
            news_items=news_items, session=session.get('user'), \
            pretty=json.dumps(session.get('user'), indent=4))


def fetch_news_item(item_id):
    """fetch news item as json.
    Args:
        item_id: the id of the news
        item to retrieve.
    Kwargs: N/A
    Returns: json of news item.
    Raises: N/A
    """
    item_url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
    response = requests.get(item_url, timeout=60)
    if response.status_code == 200:
        return response.json()
    return "Nothing here"


@app.route("/execute_fetch")
def fetch_news_items():
    """fetches all of the news items and
    adds them to the News database.
    Args: N/A
    Kwargs: N/A
    Returns: error message or basic string.
    Raises:
        IntegrityError: if failed to commit
        or add to the database.
    """
    api_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    response = requests.get(api_url, timeout=60) 
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
                        new_news = News(
                            id=news_item["id"],
                            by=news_item.get("by", "Unknown"),
                            title=news_item.get("title", "N/A"),
                            time=news_item.get("time"),
                            url=news_item.get("url", "N/A"),
                            descendants=news_item.get("descendants") \
                                    if "descendants" in news_item else None,
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
    return jsonify(message="OK"), 200


@app.route("/newsfeed")
def newsfeed():
    """returns last 30 news items sorted
    newest to oldest.
    Args: N/A
    Kwargs: N/A
    Returns: json of sorted news items.
    Raises: N/A
    """
    news_items = News.query.all()
    latest_news_items = sorted(news_items, key=lambda item: item.id, reverse=True)[:30]
    news_json = [item.as_dict() for item in latest_news_items]
    if news_json and news_items:
        return news_json
    return "Nothing here"


@app.route("/login")
def login():
    """redirects to auth0 handled login page.
    Args: N/A
    Kwargs: N/A
    Returns: redirect to auth0 login page
    Raises: N/A
    """
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    """assigns user session values and redirects
    back to domain after login. Calls addUser if
    successfully returned login session info
    Args: N/A
    Kwargs: N/A
    Returns: redirect to / route of domain
    Raises: N/A
    """
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    if session.get('user'):
        add_user(token)
    return redirect("/")


@app.route("/logout")
def logout():
    """clears login session handled by auth0
    and redirects to home route of domain
    Args: N/A
    Kwargs: N/A
    Returns: redirect to home route of domain
    Raises: N/A
    """
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
    """Return the user's account information.
    Args: N/A
    Kwargs: N/A
    Returns: template to render given users and admin database,
    admin email's, and auth0 user data as session and pretty
    as parameters
    Raises: N/A
    """
    admins = Admin.query.all()
    admin_emails = [admin.email for admin in admins]
    users = User.query.all()
    if session.get('user'):
        return render_template("account.html", users=users, \
                admin_emails=admin_emails, session=session.get('user'), \
                pretty=json.dumps(session.get('user'), indent=4))
    return redirect("/")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Adds and deletes admins and deletes users
    on button click (post) and renders admin template
    Args: N/A
    Kwargs: N/A
    Returns: renders template admin.html given the user
    and admin database, admin emails, and auth0 information
    accessors session and pretty as parameters.
    Raises:
        IntegrityError: if unable to commit to the db.session.
    """
    if request.method == "POST":
        if "new_email" in request.form:
            try:
                new_email = request.form["new_email"]
                new_admin = Admin(email=new_email)
                if not Admin.query.filter_by(email=new_email).first():
                    db.session.add(new_admin)
                    user_to_update = User.query.filter_by(email=new_email).first()
                if user_to_update:
                    user_to_update.admin = True
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
            return redirect(url_for("admin"))
        if "deleteAdmin" in request.form:
            try:
                email_to_delete = request.form["deleteAdmin"]
                admin_to_delete = Admin.query.get_or_404(email_to_delete)
                if admin_to_delete:
                    db.session.delete(admin_to_delete)
                    user_to_update = User.query.filter_by(email=email_to_delete).first()
                if user_to_update:
                    user_to_update.admin = False
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
            return redirect(url_for("admin"))
        if "deleteUser" in request.form:
            id_to_delete = request.form["deleteUser"]
            user_to_delete = User.query.get_or_404(id_to_delete)
            if user_to_delete:
                try:
                    db.session.delete(user_to_delete)
                    votes_to_delete = Vote.query.filter_by(user_id=id_to_delete).all()
                    for vote in votes_to_delete:
                        db.session.delete(vote)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
    admins = Admin.query.all()
    admin_emails = [admin.email for admin in admins]
    users = User.query.all()
    if session.get('user'):
        if not session.get('user').get('userinfo').get('email') in admin_emails:
            return redirect("/")
        return render_template("admin.html", users=users, admins=admins, \
                admin_emails=admin_emails, session=session.get('user'), \
                pretty=json.dumps(session.get('user'), indent=4))
    return redirect("/")


def add_user(token):
    """Add user to User database.
    Args:
        token: login session info.
    Kwargs: N/A
    Returns: None
    Raises:
        IntegrityError: if failed to
        commit or add to the database
    """
    userinfo = token.get('userinfo')
    add_email = "N/A"
    add_name = "N/A"
    add_nickname = None
    if userinfo.get('email'):
        add_email = userinfo.get('email')
    if userinfo.get('name'):
        add_name = userinfo.get('name')
    if userinfo.get('nickname'):
        add_nickname = userinfo.get('nickname')
    user_exists = User.query.filter_by(email=userinfo.get("email")).first()
    admin_exists = Admin.query.filter_by(email=userinfo.get("email")).first()
    new_user = []
    if admin_exists and not user_exists:
        new_user = User(
            email=add_email,
            name=add_name,
            admin=True,
            nickname=add_nickname
        )
    elif not user_exists:
        new_user = User(
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
            app.logger.error("Id: %s\nEmail: %s\nName: %s\nAdmin: %s\nNickname: %s\n", \
                    str(new_user.id), str(new_user.email), str(new_user.name), \
                    str(new_user.admin), str(new_user.nickname))
            db.session.rollback()
