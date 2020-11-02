from flask import Flask
from waitress import serve

app = Flask(__name__)

@app.route("/api/v1/hello-world-26")
def hello():
    return "<h1>Hello world 26</h1>"

if __name__ == "__main__":
    serve(app, host='127.0.0.1', port=5000)


