from flask import Flask, render_template, Blueprint, session, request
from flask_restful import Resource, Api, reqparse, fields, marshal
from v1_0 import application as api_v1
from v2_0 import application as api_v2
import requests
import os

application = Flask(__name__)
application.secret_key = os.urandom(24)

application.register_blueprint(api_v1, url_prefix='/newsapi/v1.0')
application.register_blueprint(api_v2, url_prefix='/newsapi/v2.0')


@application.route('/')
##@app.route('/News/<name>')
def base():
    return render_template('homepage.html')

def apiIndex():
    return render_template('homepage.html')
    
@application.route('/newsapi')
def apiHome():
    return render_template('apiHome.html')

@application.route('/newsapi/gui')
def gui():
    sDate = ""
    eDate = ""
    names = ""
    tags = ""
    if 'guisDate' in session:
        sDate = session['guisDate']
    if 'guieDate' in session:
        eDate = session['guieDate']
    if 'guicId' in session:
        names = session['guicId']
    if 'guitags' in session:
        tags = session['guitags']
    return render_template('gui.html', sdate = sDate, edate = eDate, names = names, tags = tags)

@application.route('/newsapi/gui/go', methods=['GET','POST'])
def gogui():
    sDate = request.args.get('startDate')
    session['guisDate'] = sDate
    sDate +="T00:00:00.000Z"
    eDate = request.args.get('endDate')
    session['guieDate'] = eDate
    eDate += "T00:00:00.000Z"
    names = request.args.get('companyId')
    tags = request.args.get('topic')
    ourApiUrl= "http://seng3011-turtle.ap-southeast-2.elasticbeanstalk.com/newsapi/v2.0/query"
    url = (ourApiUrl 
    + '?startDate=' + sDate 
    + '&endDate=' + eDate )
    if names is not "":
        url += ('&companyId=' + names)
    session['guicId'] = names
    if tags is not "":      
        url += ('&topic=' + tags)
    session['guitags'] = tags
    if 'guisDate' in session:
        sDate = session['guisDate']
    if 'guieDate' in session:
        eDate = session['guieDate']
    response = requests.get(url).json()
    return render_template('interface.html', url = url, re = response, sdate = sDate, edate = eDate, names = names, tags = tags)

def start():
    return render_template('int.html')
# change homepage to gui implementation
#def gui():
#    return render_template('homepage.html')

@application.route('/newsapi/changes')
def changesPage():
    return render_template('changes.html')

@application.route('/newsapi/documentation')
def featuresPage():
    return render_template('documentation.html')

@application.route('/newsapi/test')
def testPage():
    return render_template('test.html')
    

#Temporary
@application.route('/homepage')
def homepage1():
    return render_template('homepage.html')

@application.route('/changes')
def changesPage1():
    return render_template('changes.html')

@application.route('/documentation')
def featuresPage1():
    return render_template('documentation.html')

@application.route('/test')
def testPage1():
    return render_template('test.html')


# this will change with a gui
application.add_url_rule('/', 'index', (lambda: base()))
application.add_url_rule('/gui/', 'guiIndex', (lambda: gui()))
application.add_url_rule('/newsapi/', 'apiIndex', (lambda: apiIndex()))


if __name__ == '__main__':
    application.run(debug=True)
    
    
    
