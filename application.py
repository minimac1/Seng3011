from flask import Flask, render_template, Blueprint
from flask_restful import Resource, Api, reqparse, fields, marshal
from v1_0 import application as api_v1
from v2_0 import application as api_v2
application = Flask(__name__)

application.register_blueprint(api_v1, url_prefix='/newsapi/v1.0')
application.register_blueprint(api_v2, url_prefix='/newsapi/v2.0')

@application.route('/newsapi')
@application.route('/newsapi/homepage')
##@app.route('/News/<name>')
def base():
    return render_template('homepage.html')

def apiIndex():
    return render_template('homepage.html')

# change homepage to gui implementation
def gui():
    return render_template('homepage.html')

@application.route('/newsapi/changes')
def changesPage():
    return render_template('changes.html')

@application.route('/newsapi/documentation')
def featuresPage():
    return render_template('documentation.html')

@application.route('/newsapi/test')
def testPage():
    return render_template('test.html')

# this will change with a gui
application.add_url_rule('/', 'index', (lambda: base()))
application.add_url_rule('/gui/', 'guiIndex', (lambda: gui()))
application.add_url_rule('/newsapi/', 'apiIndex', (lambda: apiIndex()))

if __name__ == '__main__':
    application.run(debug=True)
