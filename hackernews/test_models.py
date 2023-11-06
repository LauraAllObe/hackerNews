"""
This file contains the models of the flask application.
"""
from hackernews import db
from hackernews.models import News, Admin, User, Vote

def test_News_as_dict(self):
    assert News.as_dict(self).id == News.self.id
    assert News.as_dict(self).by == News.self.by
    assert News.as_dict(self).title == News.self.title
    assert News.as_dict(self).time == News.self.time
    assert News.as_dict(self).url == News.self.url
    assert News.as_dict(self).descendants == News.self.descendants
    assert News.as_dict(self).score == News.self.score
    assert News.as_dict(self).type == News.self.type
    assert News.as_dict(self).deleted == News.self.deleted
    assert News.as_dict(self).dead == News.self.dead
    assert News.as_dict(self).parent == News.self.parent
    assert News.as_dict(self).text == News.self.text
    assert News.as_dict(self).kids == News.self.kids
    
def test_News_get_by(self):
    assert News.get_by(self) == News.self.by

"""
def test_as_dict(self):
    assert as_dict(self).email == self.email

def test_get_email(self):
    assert get_email(self) == self.email

def test_as_dict(self):
    assert as_dict(self).id == self.id
    assert as_dict(self).email == self.email
    assert as_dict(self).name == self.name
    assert as_dict(self).admin == self.admin
    assert as_dict(self).nickname == self.nickname

def test_get_name(self):
    assert get_name(self) == self.name

def test_as_dict(self):
    assert as_dict(self).id == self.id
    assert as_dict(self).user_id == self.user_id
    assert as_dict(self).news_id == self.news_id
    assert as_dict(self).liked == self.liked

def test_news_id(self):
    assert get_news_id(self) == self.news_id
"""
