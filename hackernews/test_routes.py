import json
from flask import Flask, session
from flask.testing import FlaskClient
import requests
from hackernews import app, db
from hackernews.models import News, Admin, User, Vote
from hackernews.routes import fetch_news_item, get_vote_color, get_vote_color_two

app.testing = True
client = app.test_client()
ctx = app.app_context()
ctx.push()

def test_home_route():
    response = client.get('/')
    assert response.status_code == 200

def test_fetch_news_item():
    item_id = 38157145  # Replace with a valid item ID
    result = fetch_news_item(item_id)
    assert result != "Nothing here"

def test_newsfeed_route():
    response = client.get('/newsfeed')
    assert response.status_code == 200
    assert response.json is not None

def test_login_route():
    response = client.get('/login')
    assert response.status_code == 302  # Expecting a redirect to Auth0 login

def test_logout_route():
    response = client.get('/logout')
    assert response.status_code == 302  # Expecting a redirect
"""
def test_account_route():
    with app.test_request_context():
        with app.test_client() as client:
            client.get('/login')
            response = client.get('/account')
            assert response.status_code == 485
"""
def test_admin_route():
    response = client.get('/admin')
    assert response.status_code == 200
"""
def test_execute_fetch_route():
    response = client.get('/execute_fetch')
    assert response.status_code == 200
"""

def test_callback_route():
    response = client.get('/callback')
    assert response.status_code == 400  # Expecting a redirect

def test_add_user():
    # You can add test cases for the add_user function if needed
    pass

def test_change_votes():
    # You can add test cases for the change_votes function if needed
    pass

def test_get_vote_color():
    with app.test_request_context():
        with app.test_client() as client:
            client.get('/login')
        news_id = 38157145
        need_image = True
        is_like = True
        result = get_vote_color(news_id, need_image, is_like)
        assert result == "thumbs_up.png" 

def test_get_vote_color_two():
    existing_vote = Vote(liked=True, news_id=38157145, user_id=1)
    need_image = True
    is_like = True
    result = get_vote_color_two(existing_vote, is_like, need_image)
    assert result == "red_thumbs_up.png"

ctx.pop()

