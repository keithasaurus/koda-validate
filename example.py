from flask import Flask
from simple_html import render, h1

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render(h1("Hello World!"))