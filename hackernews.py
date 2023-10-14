from flask import Flask, render_template, request, jsonify, url_for
import requests

app = Flask(__name__)

news_items = []

@app.route("/")
@app.route("/home")
def hello():
    return render_template('home.html', news_items=news_items)


def fetch_news_item(item_id):
    item_url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
    response = requests.get(item_url)

    if response.status_code == 200:
        return response.json()
    else:
        return None

@app.route("/newsfeed")
def newsfeed():
    api_url = "https://hacker-news.firebaseio.com/v0/newstories.json"
    response = requests.get(api_url)

    if response.status_code == 200:
        news_item_ids = response.json()

        global news_items
        for item_id in news_item_ids:
            news_item = fetch_news_item(item_id)
            if news_item:
                news_items.append(news_item)

        return jsonify(news_items)
    else:
        error_message = f"Failed to fetch newsfeed data. Status code: {response.status_code}"
        print(error_message)
        return error_message, 500

if __name__ == '__main__':
    app.run(host='192.155.90.192', debug=True)
