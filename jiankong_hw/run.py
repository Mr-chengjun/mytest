#-*- coding:utf-8 -*-
from flask import Flask, render_template, request, jsonify
from bokeh.util.session_id import random
import psutil
app = Flask(__name__)


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index_test.html')


@app.route('/addnumber')
def add():
    print(psutil.cpu_percent(1))
    return jsonify({'dat':psutil.cpu_percent(1)})

if __name__ == "__main__":
    app.run(debug=True)