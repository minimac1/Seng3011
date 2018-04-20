from flask import Flask, render_template, Blueprint, session, request
from flask_restful import Resource, Api, reqparse, fields, marshal
from v1_0 import application as api_v1
from v2_0 import application as api_v2

import requests
import os
import re

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
    names = []
    tags = []
    response = ""
    url = ""
    note = ""
    fav = []
    if 'guisDate' in session:
        sDate = session['guisDate']
    if 'guieDate' in session:
        eDate = session['guieDate']
    if 'guicId' in session:
        names = session['guicId']
    if 'guitags' in session:
        tags = session['guitags']
    if 'guifav' in session:
        fav = session['guifav']
    if 'guinames' in session:
        names = session['guinames']
    return render_template('interface.html', fav = fav, url = url, note=note, re = response, sdate = sDate, edate = eDate, names = names, tags = tags)

@application.route('/newsapi/gui/addD', methods=['GET','POST'])
def addDate():
    sDate = ""
    eDate = ""
    names = []
    tags = []
    response = ""
    note = "Dates Added"
    fav = []
    if 'guinames' in session:
        names = session['guinames']
    if 'guitags' in session:
        tags = session['guitags']
    if 'guifav' in session:
        fav = session['guifav']
    new = request.args.get('startDate')
    if new !=  "":
        sDate = new
        session['guisDate'] = sDate
    
    new = request.args.get('endDate')
    if new != "":
        eDate = new
        session['guieDate'] = eDate
    
    url = getUrl()
    
    if "http:" in url:
        response = requests.get(url).json()
    else:
        note = url
        url = ""
    return render_template('interface.html', fav = fav, url = url,note = note, re = response, sdate = sDate, edate = eDate, names = names, tags = tags)
    
@application.route('/newsapi/gui/addC', methods=['GET','POST'])
def addName():
    sDate = ""
    eDate = ""
    names = []
    tags = []
    response = ""
    note = ""
    fav = []
    if 'guisDate' in session:
        sDate = session['guisDate']
    if 'guieDate' in session:
        eDate = session['guieDate']
    if 'guinames' in session:
        names = session['guinames']
    if 'guitags' in session:
        tags = session['guitags']
    if 'guifav' in session:
        fav = session['guifav']
    new = request.args.get('companyId')
    
    note = "No name/Id entered"
    if new != "":
        new = new.rstrip().lstrip()
        if re.match("[^\.\s\w]",new) or new.count('.')>1:
            note = "Make sure you only enter characters or one '.' if you are using company Id's"
        else:
            names.append(new)
            session['guinames'] = names
            note = "Company added"
        
    url = getUrl()
    if "http:" in url:
        response = requests.get(url).json()
    else:
        note = url
        url = ""
    return render_template('interface.html', url = url, fav = fav, note = note, re = response, sdate = sDate, edate = eDate, names = names, tags = tags)
    
@application.route('/newsapi/gui/addF', methods=['GET','POST'])
def addFav():
    sDate = ""
    eDate = ""
    names = []
    tags = []
    response = ""
    note = "Favourite added"
    fav = []
    if 'guisDate' in session:
        sDate = session['guisDate']
    if 'guieDate' in session:
        eDate = session['guieDate']
    if 'guinames' in session:
        names = session['guinames']
    if 'guitags' in session:
        tags = session['guitags']
    if 'guifav' in session:
        fav = session['guifav']
    new = request.args.get('article')
    article={}
        
    url = getUrl()
    if "http:" in url:
        response = requests.get(url).json()
    else:
        note = url
        url = ""
    if new != "":
        for art in response['NewsDataSet']:
            if new in art['URL']:
                article['URL'] = art['URL']
                article['Headline'] = art['Headline']
        fav.append(article)
        session['guifav'] = fav

    return render_template('interface.html', fav = fav, url = url, note = note, re = response, sdate = sDate, edate = eDate, names = names, tags = tags)

@application.route('/newsapi/gui/remF', methods=['GET','POST'])
def remFav():
    sDate = ""
    eDate = ""
    names = []
    tags = []
    response = ""
    note = "Favourite added"
    fav = []
    if 'guisDate' in session:
        sDate = session['guisDate']
    if 'guieDate' in session:
        eDate = session['guieDate']
    if 'guinames' in session:
        names = session['guinames']
    if 'guitags' in session:
        tags = session['guitags']
    if 'guifav' in session:
        fav = session['guifav']
    new = request.args.get('article')
        
    url = getUrl()
    if "http:" in url:
        response = requests.get(url).json()
    else:
        note = url
        url = ""
    if new != "":
        for art in fav:
            if new in art['URL']:
                fav.remove(art)
        session['guifav'] = fav

    return render_template('interface.html', fav = fav, url = url, note = note, re = response, sdate = sDate, edate = eDate, names = names, tags = tags)
    
@application.route('/newsapi/gui/remC', methods=['GET','POST'])
def remName():
    sDate = ""
    eDate = ""
    names = []
    tags = []
    response = []
    fav= []
    note = "Company removed"
    if 'guisDate' in session:
        sDate = session['guisDate']
    if 'guieDate' in session:
        eDate = session['guieDate']
    if 'guinames' in session:
        names = session['guinames']
    if 'guitags' in session:
        tags = session['guitags']
    if 'guifav' in session:
        fav = session['guifav']
    new = request.args.get('companyId')
    
    if new != "":
        names.remove(new)
        session['guinames'] = names
        
    url = getUrl()
    if "http:" in url:
        response = requests.get(url).json()
    else:
        note = url
        url = ""
    
    return render_template('interface.html', url = url, fav = fav, note = note, re = response, sdate = sDate, edate = eDate, names = names, tags = tags)
    
@application.route('/newsapi/gui/addT', methods=['GET','POST'])
def addTopic():
    sDate = ""
    eDate = ""
    names = []
    tags = []
    response = ""
    fav = []
    
    if 'guisDate' in session:
        sDate = session['guisDate']
    if 'guieDate' in session:
        eDate = session['guieDate']
    if 'guinames' in session:
        names = session['guinames']
    if 'guitags' in session:
        tags = session['guitags']
    if 'guifav' in session:
        fav = session['guifav']
        
    new = request.args.get('topic')
    
    note = "No topic name entered"
    if new != "":
        new = new.rstrip().lstrip() 
        if re.match("[^\.\s\w]",new) or new.count('.')>1:
            note= "Make sure you only enter characters for a topic"
        else:
            tags.append(new)
            session['guitags'] = tags
            note = "Topic added"
        
    url = getUrl()
    if "http:" in url:
        response = requests.get(url).json()
    else:
        note = url
        url = ""
    
    return render_template('interface.html', fav = fav, url = url, note = note, re = response, sdate = sDate, edate = eDate, names = names, tags = tags)

@application.route('/newsapi/gui/remT', methods=['GET','POST'])
def remTopic():
    sDate = ""
    eDate = ""
    names = []
    tags = []
    response = ""
    fav = []
    note = "Topic removed"
    if 'guisDate' in session:
        sDate = session['guisDate']
    if 'guieDate' in session:
        eDate = session['guieDate']
    if 'guinames' in session:
        names = session['guinames']
    if 'guitags' in session:
        tags = session['guitags']
    if 'guifav' in session:
        fav = session['guifav']
    new = request.args.get('topic')
    
    if new != "":
        tags.remove(new)
        session['guitags'] = tags
        
    url = getUrl()
    if "http:" in url:
        response = requests.get(url).json()
    else:
        note = url
        url = ""
    
    return render_template('interface.html',fav = fav, url = url, note = note, re = response, sdate = sDate, edate = eDate, names = names, tags = tags)
    
def getUrl():
    sDate = ""
    eDate = ""
    names = []
    tags = []
    urlNames = ""
    urlTags = ""
    url = ""
    ourApiUrl= "http://seng3011-turtle.ap-southeast-2.elasticbeanstalk.com/newsapi/v2.0/query"
    
    if 'guisDate' in session:
        sDate = session['guisDate']
    if not sDate:
        return "Please enter a start date"
    if 'guieDate' in session:
        eDate = session['guieDate']
    if not eDate:
        return "Please enter an end date"
    if 'guinames' in session:
        names = session['guinames']
    if 'guitags' in session:
        tags = session['guitags']
    for name in names:
        name = name.replace(" ","-")
        urlNames += name + "_"
    if urlNames is not "":
        urlNames = urlNames[:-1]
    for tag in tags:
        tag = tag.replace(" ","-")
        urlTags += tag + "_"
    if urlTags is not "":
        urlTags = urlTags[:-1]
    sDate +="T00:00:00.000Z"
    eDate +="T00:00:00.000Z"
    
    url = (ourApiUrl
    + '?startDate=' + sDate
    + '&endDate=' + eDate )
    
    if urlNames is not "":
        url += ('&companyId=' + urlNames)

    if urlTags is not "":
        url += ('&topic=' + urlTags)
    
    return url
     
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
application.add_url_rule('/newsapi/', 'apiIndex', (lambda: apiIndex()))


if __name__ == '__main__':
    application.run(debug=True)
