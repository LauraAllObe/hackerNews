from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "<h1>Hacker News home page!</h1>"

if __name__ == '__main__':
    app.run(host='192.155.90.192', debug=True)
