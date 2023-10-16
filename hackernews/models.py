from hackernews import db
from datetime import datetime

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    by = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    url = db.Column(db.String(1000), nullable=False)

    def __repr__(self):
        return f"News('{self.title}','{self.date}')"

