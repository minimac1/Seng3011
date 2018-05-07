from flask import Flask, render_template, Blueprint, session, request
from flask_restful import Resource, Api, reqparse, fields, marshal
from v1_0 import application as api_v1
from v2_0 import application as api_v2
from v3_0 import application as api_v3
from v4_0 import application as api_v4

import requests
import os
import re
import indicoio

application = Flask(__name__)
application.secret_key = os.urandom(24)

application.register_blueprint(api_v1, url_prefix='/newsapi/v1.0')
application.register_blueprint(api_v2, url_prefix='/newsapi/v2.0')
application.register_blueprint(api_v3, url_prefix='/newsapi/v3.0')
application.register_blueprint(api_v4, url_prefix='/newsapi/v4.0')

@application.context_processor
def inject_user():
    login = "Steve" #TEMPORARY change to login and this to log in after demo
    link = "/profile"  # change this back to signin after demo
    if 'username' in session:
        login = session['username'] # gotta set this when someone logs in

    # will have to change link to the profile page if logged in
    return dict(user=login,logged=link)

@application.route('/')
##@app.route('/News/<name>')
def base():
    return render_template('homepage.html')

def apiIndex():
    return render_template('homepage.html')

@application.route('/signin')
def signIn():
    return render_template('signin.html')

@application.route('/google6ba7dcd540cdf4c2.html')
def googleVerification():
    return render_template('googleVerification.html')

@application.route('/newsapi')
def apiHome():
    return render_template('apiHome.html')

@application.route('/db')
def db():
    # add dummy variables
    name = request.args.get('company')
    if name is None:
        return render_template('profile.html')
    company = {}
    company['name'] = name
    company['change'] = 50
    #company['changec'] = "#800000"
    #company['recS'] = "slightly Positive" probly dont need an overall sentiment here considering we list it for each article
    #company['recSc'] = "#7a8c00"
    company['returns'] = 5
    #company['returnsc'] = "#7a8c00"
    company['stock'] = 3.2
    #company['stockc'] = "#7a8c00"
    statement = "Google trends indicates a lot has happened recently." # some way of creating a statement from reading our data
    statement += "A positive sentiment analysis indicates the company is doing well."
    company['statement'] = statement


    sDate="2018-05-01T00:00:00.000Z" # will probly need to pass in dates to choose the start date, once we've stored a results
    eDate="2018-05-06T00:00:00.000Z" # otherwise currently hardcoded to the previous week
    cId = name
    url = ("http://seng3011-turtle.ap-southeast-2.elasticbeanstalk.com/newsapi/v3.0/query?startDate=" + sDate
     + "&endDate=" + eDate + "&companyId=" + cId)
    re = requests.get(url).json()
    articles = []
    #if 'NewsDataSet' not in re:
        #company['statement'] += re['Developer Notes']['Execution Result']
        #return render_template('dB.html',articles=articles,company=company)
    for art in re['NewsDataSet']:
        temp = {}
        temp['headline'] = art['Headline']
        temp['url'] = art['URL']
        text = [art['NewsText']]
        text = sentiment(text)
        temp['sent'] = round(text[0],2)
        articles.append(temp)

    return render_template('dB.html',articles=articles,company=company)

#takes in an array of news articles
#and returns an array of scores eg. [o.96, 0.3]
#The score is from 0-1 and where 0.5 is netural
# 1 is super duper positive and 0 is fully negative
def sentiment(newsText):
    indicoio.config.api_key = 'd1d92c5989dc9a21f0ed2f4e6c21f46e'
    #indicoio.config.api_key = '5c28eab27da67528360f23ca9db6e3ea'

    # single example
    #indicoio.sentiment("I love writing code!")

    s = newsText
    print(s)

    ar = indicoio.sentiment(s)

    print(ar)
    return ar

@application.route('/profile')
def profile(): # maybe for the demo add the few chosen companies to session['userFol'] before the if
    companies = []
    names = [] # TEMPORARY enter 1/
    session['userFol'] = ['AMP.ax','CBA.ax','QAN.ax']
    new = request.args.get('added')

    if 'userFol' in session:
        names = session['userFol'] # for user following, to be filled with names of following companies when user logs in
    if new is not None:
        names.append(new)
        session['userFol'] = names
        # also add it to whereever we store it long term
    new = request.args.get('removed')
    if new is not None:
        names.remove(new)
        session['userFol'] = names
        # change long term stored
    for name in names: # having most fields with colours, will need to add a function the chooses the colour based on the result
        if (name=='AMP.ax'):
            tempAMP = {}
            tempAMP['name'] = name
            tempAMP['change'] = 50 # Have to change this to what the actual change should be for the company
            tempAMP['changec'] = "#800000"
            tempAMP['recS'] = "Slightly Positive" # doing a sentiment analysis on the articles within past week
            tempAMP['recSc'] = "#7a8c00"
            tempAMP['stock'] = 3.2 # mby change in stock price or a recent period of time
            tempAMP['stockc'] = "#7a8c00"
            companies.append(tempAMP)
        elif (name=='CBA.ax'):
            tempCBA = {}
            tempCBA['name'] = name
            tempCBA['change'] = 50 # Have to change this to what the actual change should be for the company
            tempCBA['changec'] = "#800000"
            tempCBA['recS'] = "Slightly Positive" # doing a sentiment analysis on the articles within past week
            tempCBA['recSc'] = "#7a8c00"
            tempCBA['stock'] = 3.2 # mby change in stock price or a recent period of time
            tempCBA['stockc'] = "#7a8c00"
            companies.append(tempCBA)
        elif (name=='QAN.ax'):
            tempQAN = {}
            tempQAN['name'] = name
            tempQAN['change'] = 50 # Have to change this to what the actual change should be for the company
            tempQAN['changec'] = "#800000"
            tempQAN['recS'] = "Slightly Positive" # doing a sentiment analysis on the articles within past week
            tempQAN['recSc'] = "#7a8c00"
            tempQAN['stock'] = 3.2 # mby change in stock price or a recent period of time
            tempQAN['stockc'] = "#7a8c00"
            companies.append(tempQAN)
        else:
            temp = {}
            temp['name'] = name
            temp['change'] = 50 # Have to change this to what the actual change should be for the company
            temp['changec'] = "#800000"
            temp['recS'] = "Slightly Positive" # doing a sentiment analysis on the articles within past week
            temp['recSc'] = "#7a8c00"
            temp['stock'] = 3.2 # mby change in stock price or a recent period of time
            temp['stockc'] = "#7a8c00"
            companies.append(temp)
    return render_template('profile.html',companies = companies)

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
        if re.search("[^\.\s\w]",new) is not None:
            note = "Make sure you only enter characters or one '.' if you are using company Id's"
        elif new.count('.')>1:
            note = "Make sure you only enter one '.'"
        else:
            names.append(new)
            session['guinames'] = names
            note = "Company added"

    url = getUrl()
    if "http:" in url:
        response = requests.get(url).json()
    else:
        #note = url
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
        if re.search("[^\s\w\"]",new) is not None:
            note= "Make sure you only enter characters for a topic or quotation marks for phrases"
        elif new.count('\"') == 1:
            note= "You may missed a quotation mark"
        elif new.count('\"') > 2:
            note= "You may more quotation marks than intended"
        else:
            tags.append(new)
            session['guitags'] = tags
            note = "Topic added"

    url = getUrl()
    if "http:" in url:
        response = requests.get(url).json()
    else:
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
    ourApiUrl= "http://seng3011-turtle.ap-southeast-2.elasticbeanstalk.com/newsapi/v3.0/query"

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
