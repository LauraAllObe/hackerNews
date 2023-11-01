"""
This file contains the models of the flask application.
"""
from hackernews import db

class News(db.Model):
    """
    Represents a news item in the application.
    Args:
        db.Model: The base class for all SQLAlchemy models.
    Kwargs: N/A
    Attributes:
        id (int): The unique identifier for the news item.
        by (str): The author of the news item.
        title (str): The title of the news item.
        time (int): The timestamp when the news item was created.
        url (str): The URL of the news item.
        descendants (int): The number of descendants (comments) for the news item.
        score (int): The score of the news item.
        type (str): The type of the news item.
        deleted (bool): Whether the news item is deleted.
        dead (bool): Whether the news item is dead.
        parent (int): The parent news item ID.
        text (str): The text content of the news item.
        kids (str): JSON text representing child comments of the news item.
    """
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

    def get_by(self):
        """getter for by attribute of News class.
        Args:
            self: instance of News class.
        Kwargs: N/A
        Returns: by attribute of News class.
        Raises: N/A
        """
        return self.by


class Admin(db.Model):
    """
    Represents an admin user in the application.
    Args:
        db.Model: The base class for all SQLAlchemy models.
    Kwargs: N/A
    Attributes:
        email (str): The email address of the admin user (primary key).
    """
    email = db.Column(db.String(500), primary_key=True)

    def as_dict(self):
        """json of Admin class.
        Args:
            self: instance of Admin class.
        Kwargs: N/A
        Returns: Admin class data as json formatted.
        Raises: N/A
        """
        return {
                'email': self.email
        }

    def get_email(self):
        """getter for email attribute of Admin class.
        Args:
            self: instance of Admin class.
        Kwargs: N/A
        Returns: email attribute of Admin class.
        Raises: N/A
        """
        return self.email


class User(db.Model):
    """
    Represents a user in the application.
    Args:
        db.Model: The base class for all SQLAlchemy models.
    Kwargs: N/A
    Attributes:
        id (int): The unique identifier for the user.
        email (str): The email address of the user.
        name (str): The name of the user.
        admin (bool): Indicates whether the user is an admin.
        nickname (str): The user's nickname.
    """
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
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'admin': self.admin,
            'nickname': self.nickname
        }

    def get_name(self):
        """getter for name attribute of User class.
        Args:
            self: instance of User class.
        Kwargs: N/A
        Returns: name attribute of User class.
        Raises: N/A
        """
        return self.name


class Vote(db.Model):
    """
    Represents a user's dislikes in the application.
    Args:
        db.Model: The base class for all SQLAlchemy models.
    Kwargs: N/A
    Attributes:
        id (int): The unique identifier for the dislike.
        user_id (int): The user ID associated with the dislike.
        news_id (int): The news item ID associated with the dislike.
        liked (bool): Indicates whether the dislike is for a liked item.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    liked = db.Column(db.Boolean, nullable=True)

    def as_dict(self):
        """json of Vote class.
        Args:
            self: instance of Vote class.
        Kwargs: N/A
        Returns: Vote class data as json formatted.
        Raises: N/A
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'news_id': self.news_id,
            'liked': self.liked
        }

    def get_news_id(self):
        """getter for news_id attribute of Vote class.
        Args:
            self: instance of Vote class.
        Kwargs: N/A
        Returns: news_id attribute of Vote class.
        Raises: N/A
        """
        return self.news_id
