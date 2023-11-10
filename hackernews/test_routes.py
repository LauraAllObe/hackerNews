import json
from flask import Flask, session, jsonify, request
from sqlalchemy.exc import IntegrityError
from flask.testing import FlaskClient
import requests
from hackernews import app, db
from hackernews.models import News, Admin, User, Vote
from hackernews.routes import fetch_news_items, fetch_news_item, get_vote_color, get_vote_color_two, change_votes

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
"""
def test_admin_route():
    response = ""
    with app.app_context():
        with app.test_client() as client:
            client.get('/login')
    # Simulate a GET request to the admin route
            response = client.get('/admin')
    assert response.status_code == 200  # Check if the response status is OK

    # Simulate a POST request to add a new admin
    new_email = "new_admin@example.com"
    response = client.post('/admin', data={"new_email": new_email})
    assert response.status_code == 302  # Check if the response is a redirect
    assert Admin.query.filter_by(email=new_email).first() is not None  # Check if the admin was added

    # Simulate a POST request to delete an admin
    response = client.post('/admin', data={"deleteAdmin": new_email})
    assert response.status_code == 302  # Check if the response is a redirect
    assert Admin.query.filter_by(email=new_email).first() is None  # Check if the admin was deleted

    # Simulate a POST request to delete a user
    user_to_delete = User.query.first()
    response = client.post('/admin', data={"deleteUser": str(user_to_delete.id)})
    assert response.status_code == 302  # Check if the response is a redirect
    assert User.query.filter_by(id=user_to_delete.id).first() is None  # Check if the user was deleted

    # Test for handling IntegrityError when adding an admin
    with app.test_request_context('/admin', method='POST'):
        # Simulate a POST request to add a new admin with an IntegrityError
        db.session.rollback()  # Ensure a clean session
        new_email = "duplicate_admin@example.com"
        new_admin = Admin(email=new_email)
        db.session.add(new_admin)
        db.session.commit()  # Commit the admin with the same email
        response = client.post('/admin', data={"new_email": new_email})
        assert response.status_code == 302  # Check if the response is a redirect

    # Test for handling IntegrityError when deleting an admin
    with app.test_request_context('/admin', method='POST'):
        # Simulate a POST request to delete an admin with an IntegrityError
        db.session.rollback()  # Ensure a clean session
        admin_to_delete = Admin(email="admin@example.com")
        db.session.add(admin_to_delete)
        db.session.commit()  # Commit the admin to be deleted
        user_to_update = User.query.filter_by(email="admin@example.com").first()
        user_to_update.admin = True
        response = client.post('/admin', data={"deleteAdmin": "admin@example.com"})
        assert response.status_code == 302  # Check if the response is a redirect

    # Test for handling IntegrityError when deleting a user
    with app.test_request_context('/admin', method='POST'):
        # Simulate a POST request to delete a user with an IntegrityError
        db.session.rollback()  # Ensure a clean session
        user_to_delete = User.query.first()
        db.session.delete(user_to_delete)
        db.session.commit()  # Commit the deletion
        response = client.post('/admin', data={"deleteUser": str(user_to_delete.id)})
        assert response.status_code == 302  # Check if the response is a redirect

    # Additional checks on the rendered template
    response = client.get('/admin')
    assert b"admin.html" in response.data  # Check if the admin.html template is rendered
    assert b"Logged in as" in response.data  # Check if user information is displayed

    # Additional assertions on the context data
    assert session.get('user') is not None  # Check if user session data is set
    assert json.loads(session.get('user')) is not None  # Check if user session data is JSON parseable

    # Clean up any test data created during the test
    db.session.rollback()
"""

def test_execute_fetch_route():
    response = client.get('/execute_fetch')
    assert response.status_code == 200
    assert response.json == {"message": "OK"}

def test_callback_route():
    response = client.get('/callback')
    assert response.status_code == 400  # Expecting a redirect

def test_add_user():
    # You can add test cases for the add_user function if needed
    pass

def test_change_votes():
    with app.test_request_context():
        with app.test_client() as client:
            client.get('/login')
        news_id = 38157145
        click = True
        result = change_votes(click, news_id)
        assert result == None

def test_get_vote_color():
    with app.test_request_context():
        with app.test_client() as client:
            client.get('/login')
        news_id = 38157145
        assert get_vote_color(news_id, True, True) == "thumbs_up.png" 
        assert get_vote_color(news_id, False, True) == "#5f4747"
        assert get_vote_color(news_id, False, False) == "#5f4747"
        assert get_vote_color(news_id, True, False) == "thumbs_down.png"
        news_id = 38221121
        existing_vote = Vote.query.filter_by(news_id=news_id).first()
        assert get_vote_color_two(existing_vote, True, True) == "red_thumbs_up.png"
        assert get_vote_color_two(existing_vote, False, True) == "thumbs_down.png"
        assert get_vote_color_two(existing_vote, False, False) == "#5f4747"
        assert get_vote_color_two(existing_vote, True, False) == "#652525"

def test_get_vote_color_two():
    existing_vote = Vote(liked=True, news_id=38157145, user_id=1)
    need_image = True
    is_like = True
    result = get_vote_color_two(existing_vote, is_like, need_image)
    assert result == "red_thumbs_up.png"

ctx.pop()


