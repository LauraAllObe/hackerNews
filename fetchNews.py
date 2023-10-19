from hackernews import app

# Import necessary modules and setup Flask app

with app.app_context():
    from hackernews.routes import fetch_news_items

fetch_news_items()
