#-*-coding:utf-8-*-

from server import app
from flask import render_template, make_response, request, redirect, abort

@app.route('/', methods=['GET'])
def index():
    headers = request.headers
    host = headers['Host']
    if host.startswith('2016'):
        return render_template('index.2016.html')
    elif host == 'ms-multimedia-challenge.com':
        return redirect('http://2017.ms-multimedia-challenge.com')
    else:
        return render_template('index.2017.html')

@app.route('/people', methods=['GET'])
def people():
    headers = request.headers
    host = headers['Host']
    if host.startswith('2016'):
        return render_template('people.2016.html')
    elif host == 'ms-multimedia-challenge.com':
        return redirect('http://2017.ms-multimedia-challenge.com/people')
    else:
        return render_template('people.2017.html')

@app.route('/challenge', methods=['GET'])
def challenge():
    headers = request.headers
    host = headers['Host']
    if host.startswith('2016'):
        return render_template('challenge.2016.html')
    elif host == 'ms-multimedia-challenge.com':
        return redirect('http://2017.ms-multimedia-challenge.com/challenge')
    else:
        return render_template('challenge.2017.html')

@app.route('/dataset', methods=['GET'])
def dataset():
    headers = request.headers
    host = headers['Host']
    if host.startswith('2016'):
        return render_template('dataset.2016.html')
    elif host == 'ms-multimedia-challenge.com':
        return redirect('http://2017.ms-multimedia-challenge.com/dataset')
    else:
        return render_template('dataset.2017.html')

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    headers = request.headers
    host = headers['Host']
    if host.startswith('2016'):
        return render_template('leaderboard.2016.html')
    else:
        abort(404)

@app.route('/contact', methods=['GET'])
def external():
    headers = request.headers
    host = headers['Host']
    if host.startswith('2016'):
        return render_template('contact.2016.html')
    elif host == 'ms-multimedia-challenge.com':
        return redirect('http://2017.ms-multimedia-challenge.com/contact')
    else:
        return render_template('contact.2017.html')

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

@app.route('/reset', methods=['GET'])
def reset():
    args = request.args
    if not 'token' in args or not 'challenge_type' in args:
        return ''
    token = args['token']
    challenge_type = args['challenge_type']
    return render_template('reset.html', token=token, challenge_type=challenge_type)
