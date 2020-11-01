from flask import Flask
from waitress import serve


app = Flask(__name__)

@app.route("/")
def hello():
    return "<h1>Hello world 26</h1>"

if __name__ == "__main__":

    serve(app, host="localhost", port=5000, url_scheme='https')

