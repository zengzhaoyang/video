#-*-coding:utf-8-*-

from server import app
from flask import render_template, make_response, request, redirect

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/people', methods=['GET'])
def people():
    return render_template('people.html')

@app.route('/challenge', methods=['GET'])
def challenge():
    return render_template('challenge.html')

@app.route('/dataset', methods=['GET'])
def dataset():
    return render_template('dataset.html')

@app.route('/contact', methods=['GET'])
def external():
    return render_template('contact.html')

@app.route('/browse', methods=['GET'])
def browse():
    args = request.args
    if not 'token' in args:
        return ''
    token = args['token']
    if token == 'msramsmbest':
        return render_template('browse.html')
    else:
        return ''