import requests
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, render_template, request, jsonify, url_for, redirect, session

#auth0 .env file recognition
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
#set auth0 secret key
app.secret_key = env.get("APP_SECRET_KEY")

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
@app.route("/home")
def hello():
    return render_template('home.html', news_items=news_items, session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))


def fetch_news_item(item_id):
    item_url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
    response = requests.get(item_url)

    if response.status_code == 200:
        return response.json()
    else:
        return None

@app.route("/newsfeed")
def newsfeed():
    api_url = "https://hacker-news.firebaseio.com/v0/newstories.json"
    response = requests.get(api_url)

    if response.status_code == 200:
        news_item_ids = response.json()

        global news_items
        for item_id in news_item_ids:
            news_item = fetch_news_item(item_id)
            if news_item:
                news_items.append(news_item)

        return jsonify(news_items)
    else:
        error_message = f"Failed to fetch newsfeed data. Status code: {response.status_code}"
        print(error_message)
        return error_message, 500

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

if __name__ == '__main__':
    app.run(host='192.155.90.192', port=env.get("PORT", 5000), debug=True)
