from flask import Flask

app=Flask(__name__)

@app.route('/')
def default_page():
    return '<h1>Starting page</h1>'

@app.route('/api/v1/hello-world-26')
def hello_world():
    return '<h1>Hello world 26</h1>'

if __name__=='__main__':
    app.run(host="localhost",port=5000,debug=True)