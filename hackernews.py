from flask import Flask

app = Flask(__name__)

@app.route("/")
def hacker_news():
    return "<h1>Hacker News home page!</h1>"

@app.route("/test")
def test():
    return "<h1>Test Page</h1>"

if __name__ == '__main__':
    app.run(debug=True)
