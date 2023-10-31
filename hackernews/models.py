"""
This file contains the models of the flask application.
"""
from hackernews import db
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    by = db.Column(db.String(100), nullable=False, default="Anonymous")
    title = db.Column(db.String(500), nullable=False, default="N/A")
    time = db.Column(db.Integer, nullable=True)
    url = db.Column(db.String(1000), nullable=False, default="N/A")
    descendants = db.Column(db.Integer, nullable=True)
    score = db.Column(db.Integer, nullable=True)
    type = db.Column(db.String(50), nullable=True)
    deleted = db.Column(db.Boolean, nullable=True)
    dead = db.Column(db.Boolean, nullable=True)
    parent = db.Column(db.Integer, nullable=True)
    text = db.Column(db.String(2000), nullable=True)
    kids = db.Column(db.Text, nullable=True)

    def as_dict(self):
        """json of News class.
        Args:
            self: instance of News class.
        Kwargs: N/A
        Returns: News class data as json formatted.
        Raises: N/A
        """
        data = {
            'id': self.id,
            'by': self.by,
            'title': self.title,
            'time': self.time,
            'url': self.url,
            'descendants': self.descendants,
            'score': self.score,
            'type': self.type,
            'deleted': self.deleted,
            'dead': self.dead,
            'parent': self.parent,
            'text': self.text,
            'kids': self.kids,
        }
        keys_to_exclude = [key for key, value in data.items() if value is None]
        for key in keys_to_exclude:
            del data[key]
        return data

class Admin(db.Model):
    email = db.Column(db.String(500), primary_key=True)

    def as_dict(self):
        """json of Admin class.
        Args:
            self: instance of Admin class.
        Kwargs: N/A
        Returns: Admin class data as json formatted.
        Raises: N/A
        """
        data = {
                'email': self.email,
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(500), nullable=False, default="N/A")
    name = db.Column(db.String(500), nullable=False, default="N/A")
    admin = db.Column(db.Boolean, nullable=False, default=False)
    nickname = db.Column(db.String(500), nullable=True)

    def as_dict(self):
        """json of User class.
        Args:
            self: instance of User class.
        Kwargs: N/A
        Returns: User class data as json formatted.
        Raises: N/A
        """
        data = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'admin': self.admin,
            'nickname': self.nickname
        }

class disLikes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    newsId = db.Column(db.Integer, db.ForeignKey('news.id'))
    liked = db.Column(db.Boolean, nullable=True)

    def as_dict(self):
        """json of disLikes class.
        Args:
            self: instance of disLikes class.
        Kwargs: N/A
        Returns: disLikes class data as json formatted.
        Raises: N/A
        """
        data = {
            'id': self.id,
            'userId': self.userId,
            'newsId': self.newsId,
            'liked': self.liked
        }
