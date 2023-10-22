from hackernews import db
from datetime import datetime

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    by = db.Column(db.String(100), nullable=False, default="Anonymous")
    title = db.Column(db.String(500), nullable=False, default="N/A")
    date = db.Column(db.DateTime, default=datetime.utcnow)
    url = db.Column(db.String(1000), nullable=False, default="N/A")
    descendants = db.Column(db.Integer, nullable=True)
    score = db.Column(db.Integer, nullable=True)
    type = db.Column(db.String(50), nullable=True)
    deleted = db.Column(db.Boolean, nullable=True)
    dead = db.Column(db.Boolean, nullable=True)
    parent = db.Column(db.Integer, nullable=True)
    text = db.Column(db.String(2000), nullable=True)
    kids = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"News('{self.title}','{self.date}')"

    def as_dict(self):
        return {
                'id': self.id,
                'by': self.by,
                'title': self.title,
                'date': self.date,
                'url': self.url,
                'descendants': self.descendants,
                'score': self.score,
                'type': self.type,
                'deleted': self.deleted,
                'dead': self.dead,
                'parent': self.parent,
                'text': self.text,
                'kids': self.kids
            }
