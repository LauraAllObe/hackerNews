import requests
import json
from os import environ as env
from hackernews import app, db
from hackernews.models import News
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime, timezone

#global store the json news items (currently all from get news items)
news_items = []

def fetch_news_item(item_id):
    item_url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
    response = requests.get(item_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


@app.route("/execute_fetch")
def fetch_news_items():
    """
    function definition to fetch each news item given an Id. Iterated over by
    newsfeed function. returns json formatted news items.
    """
    api_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    response = requests.get(api_url) 
    if response.status_code == 200:
        news_item_ids = response.json()[:50]
        for item_id in news_item_ids:
            news_item = fetch_news_item(item_id)
            if news_item:
                existing_news_item = News.query.filter_by(id=news_item["id"]).first()
                if (
                    not existing_news_item
                    and all(
                        news_item.get(field) is not None
                        for field in ["title", "by", "url", "type"]
                    )
                    and news_item.get("type") == "story"
                ):
                    try:
                        news_time = news_item.get("time", 0)
                        datetime_value = datetime.utcfromtimestamp(news_time)
     
                        new_news = News(
                            id=news_item["id"],
                            by=news_item.get("by", "Unknown"),
                            title=news_item.get("title", "N/A"),
                            date=datetime_value,
                            url=news_item.get("url", "N/A")
                        )
                        db.session.add(new_news)
                        db.session.commit()
                    except IntegrityError:
                        db.session.rollback()
        return "Nothing to return here"
    else:
        error_message = f"Failed to fetch newsfeed data. Status code: {response.status_code}"
        print(error_message)
        return error_message, 500

