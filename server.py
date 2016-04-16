#-*-coding:utf-8-*-
from flask import Flask
from api import api

app = Flask(__name__, template_folder='web/templates')
app.debug = True
app.register_blueprint(api, url_prefix='/api')

from web import *

if __name__ == '__main__':
    app.run('0.0.0.0', 5000)