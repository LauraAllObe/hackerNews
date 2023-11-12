import pytest
from flask import Flask
from hackernews import app, db  # Import your Flask application's database module
from hackernews.models import News, Admin, User, Vote  # Import your database models


def test_news_as_dict():
    news = News(id=1, by='John Doe', title='Test News', time=1234567890)
    result = news.as_dict()
    expected = {
        'id': 1,
        'by': 'John Doe',
        'title': 'Test News',
        'time': 1234567890
    }
    assert result == expected

def test_news_get_by():
    news = News(id=1, by='John Doe', title='Test News', time=1234567890)
    result = news.get_by()
    assert result == 'John Doe'

def test_admin_as_dict():
    admin = Admin(email='admin@example.com')
    result = admin.as_dict()
    expected = {
        'email': 'admin@example.com'
    }
    assert result == expected

def test_admin_get_email():
    admin = Admin(email='admin@example.com')
    result = admin.get_email()
    assert result == 'admin@example.com'

def test_user_as_dict():
    user = User(id=1, email='user@example.com', name='Test User', admin=True, nickname='tester')
    result = user.as_dict()
    expected = {
        'id': 1,
        'email': 'user@example.com',
        'name': 'Test User',
        'admin': True,
        'nickname': 'tester'
    }
    assert result == expected

def test_user_get_name():
    user = User(id=1, email='user@example.com', name='Test User', admin=True, nickname='tester')
    result = user.get_name()
    assert result == 'Test User'

def test_vote_as_dict():
    vote = Vote(id=1, user_id=1, news_id=1, liked=False)
    result = vote.as_dict()
    expected = {
        'id': 1,
        'user_id': 1,
        'news_id': 1,
        'liked': False
    }
    assert result == expected

def test_vote_get_news_id():
    vote = Vote(id=1, user_id=1, news_id=1, liked=False)
    result = vote.get_news_id()
    assert result == 1

if __name__ == '__main__':
    pytest.main()

