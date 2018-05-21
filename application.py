from flask import Flask, render_template, Blueprint, session, request, Response
from flask_restful import Resource, Api, reqparse, fields, marshal
from wtforms import TextField, Form
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from botocore.exceptions import ClientError
from v1_0 import application as api_v1
from v2_0 import application as api_v2
from v3_0 import application as api_v3
from v4_0 import application as api_v4

from v3_0 import removeExchangeCode, csvRemoveTails, asxCodeToName

import requests
import os
import re
import indicoio
import boto3
import googleTrends
import datetime
import atexit
import json
from datetime import timedelta, date
import psycopg2
from aylienapiclient import textapi

application = Flask(__name__)
application.secret_key = os.urandom(24)

application.register_blueprint(api_v1, url_prefix='/newsapi/v1.0')
application.register_blueprint(api_v2, url_prefix='/newsapi/v2.0')
application.register_blueprint(api_v3, url_prefix='/newsapi/v3.0')
application.register_blueprint(api_v4, url_prefix='/newsapi/v4.0')

# company_list = ["Bratislava",
#          "Bansk Bystrica",
#          "Preov",
#          "Povask Bystrica",
#          "Zilina",
#          "Koice",
#          "Ruomberok",
#          "Zvolen",
#          "Poprad"]

# connect to database
try:
    dbConn = psycopg2.connect("dbname='ebdb' user='teamturtleseng' password='SENG3011!' host='aaiweopiy3u4yv.ccig0wydbyxl.ap-southeast-2.rds.amazonaws.com' port='5432'")
    dbCur = dbConn.cursor()
except:
    print('unable to connect to the database')

@application.context_processor
def inject_user():
    if 'username' in session:
        username = session['username']
        print('session[username] = '+username)
    else:
        username = None  # <div class=\"g-signin2\" data-onsuccess=\"onSignIn\"></div>
    if 'image' in session:
        image = session['image']
    else:
        image = "https://qualiscare.com/wp-content/uploads/2017/08/default-user-300x300.png"
    # will have to change link to the profile page if logged in
    return dict(user=username,image=image)

@application.route('/')
##@app.route('/News/<name>')
def base():
    return render_template('homepage.html')

def apiIndex():
    return render_template('homepage.html')

@application.route('/signin', methods=['POST'])
def signIn():
    username = request.form.get('username')
    email = request.form.get('email')
    image = request.form.get('image')
    id = request.form.get('id')

    if (username is None) or (email is None) or (image is None) or (id is None):
        return "Error: Missing Parameter"
    else:
        session['username'] = username
        session['userEmail'] = email
        session['image'] = image
        session['id'] = id
        session['followTime'] = "Daily"
        session['emailEventPref'] = 'Yes'
        session.permanent = True

        try:
            dbCur.execute("""SELECT * FROM userData WHERE id=%s;""", (id,))
            rows = dbCur.fetchall()
            if(len(rows) == 0):
                print('adding user to database')
                print(dbCur.mogrify("""INSERT INTO userData VALUES (%s, %s, %s, %s, %s, %s);""", (str(id), username, email, image, session['followTime'], session['emailEventPref'])))
                dbCur.execute("""INSERT INTO userData VALUES (%s, %s, %s, %s, %s, %s);""", (str(id), username, email, image, session['followTime'], session['emailEventPref']))
                dbConn.commit()
            else:
                pass
                #dbCur.execute("""SELECT followTime, emailEvent FROM userData where id=%s;""", (str(id),))
                #rows = dbCur.fetchall()
                #for row in rows:
                #    session['followTime'] = row[0]
                #    session['emailEventPref'] = row[1]
                #read userFol
            return "Success: Logged in as "+username
        except:
            return "Success: Logged in as "+username+"; error talking to database"


@application.route('/signout', methods=['POST'])
def signOut():
    session.pop('username', None)
    session.pop('userEmail', None)
    session.pop('image', None)
    session.pop('id', None)
    session.pop('followTime', None)
    session.pop('emailEventPref', None)
    session.pop('userFol', None)
    return "Log out success"


@application.route('/redirect')
def redirect():
    return render_template('redirect.html')


@application.route('/google6ba7dcd540cdf4c2.html')
def googleVerification():
    return render_template('googleVerification.html')

@application.route('/newsapi')
def apiHome():
    return render_template('apiHome.html')

def rgCol(number):
    if number > 100:
        number = 100
    elif number < 0:
        number = 0
    r = int(round((220-(number * 2.2)),0))
    g = int(round((number * 2.2),0))
    r = hex(r)
    g = hex(g)
    r = r[2:]
    g = g[2:]
    if (len(r) == 1):
        r = "0"+r
    if (len(g) == 1):
        g = "0"+g
    colour = "#"+r+g+"00"
    return colour

@application.route('/db')
def db():
    # add dummy variables
    name = request.args.get('company')
    if name is None:
        return render_template('profile.html')
    company = {}
    company['name'] = name
    #company['change'] = 50
    #company['changec'] = "#800000"
    #company['recS'] = "slightly Positive" probly dont need an overall sentiment here considering we list it for each article
    #company['recSc'] = "#7a8c00"
    #company['returns'] = 5
    #company['returnsc'] = "#7a8c00"
    #company['stock'] = 3.2
    #company['stockc'] = "#7a8c00"
    statement = "Google trends indicates there has been a minor event recently.<br>" # some way of creating a statement from reading our data
    statement += "A negative sentiment on the recent articles indicates a problem with this company."
    company['statement'] = statement

    now = (datetime.datetime.now()- timedelta(days=1)) # currently -1day because i can't use current day
    eDate= now.isoformat()
    eDate = eDate[0:23] + "Z" # will probly need to pass in dates to choose the start date, once we've stored a results
    sDate= (now - timedelta(days=14)) # otherwise currently hardcoded to the previous week
    sDate = str(eDate).replace(' ','T')
    sDate = sDate[0:23] + "Z"
    cId = name
    url = ("http://seng3011-turtle.ap-southeast-2.elasticbeanstalk.com/newsapi/v3.0/query?startDate=" + sDate
     + "&endDate=" + eDate + "&companyId=" + cId)
    res = requests.get(url).json()
    articles = []
    #if 'NewsDataSet' not in re:
        #company['statement'] += re['Developer Notes']['Execution Result']
        #return render_template('dB.html',articles=articles,company=company)
    i = 0
    for art in res['NewsDataSet']:
        if i > 9:
            break; #limiting it to 10 articles
        temp = {}
        temp['headline'] = art['Headline']
        temp['url'] = art['URL']
        date = art['TimeStamp']
        date = date[0:16]
        date = date.replace('T', ' ')
        temp['date']=date
        text = art['NewsText']
        if not text:
            continue
        temp['sent'] = text

        articles.append(temp)
        i+= 1
    sent = []
    for art in articles:
        sent.append(art['sent'])
    if sent != []:
        sent = sentiment(sent)
        for c, value in enumerate(sent,1):
            value = round(value,2)*100
            articles[c-1]['sent'] = value
            articles[c-1]['sentc'] = rgCol(value)
        articles = sorted(articles, key=lambda k: k['date'])
    changes = stockPrice(name)
    first = 1
    earliest = ""
    for date in changes:
        if first == 1:
            eariest = date;
            first = 0
        elif date < earliest:
            earliest = date

    name = re.sub(r"\..*","",name)
    now = datetime.datetime.now()
    #nDate = now.year + "-" + now.month + "-" + now.day
    trends = googleTrends.trendFromNumWeek(5, name)
    tc = []
    i = 3*7
    while i < len(trends):
        avg = average(trends,i)
        change = round((trends[i]-avg)/avg*100,0)
        tc.append(change)
        i += 1
    i = 0
    tc.reverse()
    for date in tc:
        now = (datetime.datetime.now()- timedelta(days=i))
        month = str(now.month)
        day = str(now.day)
        if len(month) == 1:
            month = "0" + month
        if len(day) == 1:
            day = "0" + day
        nDate = str(now.year) + "-" + month + "-" + day
        print(nDate)
        if nDate in changes:
            changes[nDate]['trends'] = tc[i]
            bDate = nDate[5:]
            bDate = bDate.replace('-','/')
            changes[nDate]['shortDate'] = bDate
        else:
            bDate = nDate[5:]
            bDate = bDate.replace('-','/')
            changes[nDate]={}
            changes[nDate]['trends'] = tc[i]
            changes[nDate]['stock'] = 0
            changes[nDate]['shortDate'] = bDate
        i += 1

    for date in list(changes):
        if 'trends' not in changes[date]:
            del changes[date]

    print(changes)
    sChanges = []
    for date in sorted(changes):
        temp={}
        temp['shortDate'] = changes[date]['shortDate']
        temp['stock'] = changes[date]['stock']
        temp['trends'] = changes[date]['trends']
        sChanges.append(temp)
    return render_template('dB.html',articles=articles,company=company,changes = sChanges)

def average(numbers,pos):
    count = 0
    avg = 0
    while (count < 3):
        pos-= 7
        count += 1
        avg += numbers[pos]
    avg = int(round((avg/count),0))
    return avg

#Function that returns google news in json format
#argements are all strings eg. ("ANZ.AX", "2017-09-06", "2018-01-10")
def googleNews(instrumentId, startDate, endDate):
    #12b538a8b7c24dc2b1b496061a014e80
    g_url = 'https://newsapi.org/v2/everything?'

    s_params = {
        'q': "",
        'sources': "australian-financial-review,abc-news-au",
        'from': "",
        'to': "",
        'language': "en",
        'sortBy': "relevancy",
        'apikey': "12b538a8b7c24dc2b1b496061a014e80"

    }

    abbrev = removeExchangeCode(instrumentId)
    company = csvRemoveTails(asxCodeToName(instrumentId))

    qu = '(' + abbrev + ')' + 'OR' + '(' + company + ')'
    s_params['q'] = qu
    s_params['from'] = startDate
    s_params['to'] = endDate

    url_to_pass = (g_url + s_params['q'] + '&sources=' + s_params['sources']
    + '&from=' + s_params['from'] + '&to=' + s_params['to'] + '&language='
    + s_params['language'] + '&sortBy' + s_params['sortBy'] + '&apikey='
    + s_params['apikey'] )

    articles = requests.get(url_to_pass).json()
    #print(articles)
    return articles

#Function that extracts the articles
#Argeument articles is an array of urls strings
#returns an array of article texts.
def extractNewText(articles):
    arr = articles
    toReturn = []
    client = textapi.Client("3dd5c680", "2d20c5a25c086699eb796c7e21d2bfb8")

    for c in arr:

        extract = client.Extract({"url": c})
        toReturn.append(extract['article'])

    return toReturn




#function that returns stock prices in json formating
#argument instrumentId is a string eg. "ANZ.AX"
def stockPrice(instrumentId):
    s_params = {
        'function': "TIME_SERIES_DAILY",
        'symbol': "",
        #'apikey': "JSLIQKXENUXYT6V3"
        'apikey' : "ERXH2MS2R8UU6EDN"

    }

    a_url = "https://www.alphavantage.co/query?"
    s_params['symbol'] = instrumentId

    stock_url = (a_url + 'function=' + s_params['function']
    + '&symbol=' + s_params['symbol'] + '&apikey='
    + s_params['apikey'])
    #stocks = []

    response = requests.get(stock_url).json()
    points = response['Time Series (Daily)']
    dates = sorted(points)
    dates.reverse()
    i = 0
    #print(points)
    stocks = {}
    for point in dates:
        stocks[point] = {}
        openS = float(points[point]['1. open'])
        closeS = float(points[point]['4. close'])
        stocks[point]['stock']=round((openS - closeS),2)
        #stocks.append(temp)
        if i >10:
            break
        i += 1
    return stocks



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
    #print(s)

    ar = indicoio.sentiment(s)

    #print(ar)
    return ar

class SearchForm(Form):
    autocomp = TextField('Insert Company ID', id='profile_autocomplete')

@application.route('/_autocomplete', methods=['GET'])
def autocomplete():
    return Response(json.dumps(company_list), mimetype='application/json')



@application.route('/profile', methods=['GET', 'POST'])
def profile(): # maybe for the demo add the few chosen companies to session['userFol'] before the if
    greenColour = "#7a8c00"
    redColour = "#800000"
    #sendEmail("teamturtleseng@gmail.com", "CBA.ax")
    companies = []
    names = [] # TEMPORARY enter 1/
    #session['userFol'] = ['AMP.ax','CBA.ax','QAN.ax']
    new = request.args.get('added')

    if 'userFol' in session:
        names = session['userFol'] # for user following, to be filled with names of following companies when user logs in
    if new is not None:
        names.append(new)
        session['userFol'] = names
        googleTrends.updateMonthlyTrends(new,False)
        try:
            dbCur.execute("""INSERT INTO userFollows VALUES (%s,%s);""", (str(session['id']), str(new)))
            dbConn.commit()
        except:
            pass

    new = request.args.get('removed')
    if new is not None:
        names.remove(new)
        session['userFol'] = names
        try:
            dbCur.execute("""DELETE FROM userFollows WHERE id = %s and company = %s;""", (str(session['id']), str(new)))
            dbConn.commit()
        except:
            pass
        # change long term stored
    for name in names: # having most fields with colours, will need to add a function the chooses the colour based on the result
        temp = {}
        temp['name'] = name
        temp['change'] = str(googleTrends.getCurrentChange(name)) + "%" #name must be form -> "XXX.SX"
        temp['changec'] = greenColour
        temp['recS'] = "Slightly Positive" # doing a sentiment analysis on the articles within past week
        temp['recSc'] = greenColour
        curStocks = stockPrice(name)
        today = str(date.today())
        temp['stock'] = curStocks[today]['stock']
        temp['stockc'] = greenColour
        companies.append(temp)
    settings = {}

    # update user settings
    new = request.args.get('eventPref')
    if (new is not None):
        try:
            dbCur.execute("""UPDATE userData SET emailEvent = %s WHERE id = %s;""", (str(new), str(session['id'])))
            #cur.execute("""UPDATE userData SET followTime =%s WHERE id = %s;""", ('Monthly', str(103735791600147053277)))
            dbConn.commit()
            session['emailEventPref'] = new
            print("changing user setting: emailEventPref = "+new)
        except:
            print("update setting 'EventPref' failed")

    new = request.args.get('time')
    if (new is not None):
        try:
            dbCur.execute("""UPDATE userData SET followTime = %s WHERE id = %s;""", (str(new), str(session['id'])))
            dbConn.commit()
            session['followTime'] = new
            print("changing user setting: followTime = "+new)
        except:
            print("update setting 'followTime' failed")

    # get user settings
    if('followTime' in session):
        settings['followTime'] = session['followTime']
    else:
        settings['followTime'] = "Daily"

    if('emailEventPref' in session):
        settings['emailEventPref'] = session['emailEventPref']
    else:
        settings['emailEventPref'] = 'Yes'

    # Autocomplete form
    form = SearchForm(request.form)
    return render_template('profile.html', companies=companies, form=form, settings=settings)

#def hourlyTrendCheck():
    #loop through googleTrends.pytrendsCompanyList
        #googleTrends.updateGoogleTrends
        #getCurrentChange("companyid")
        #if change > 15
            #loop through googleTrends.pytrendsUserList
            #if contains currCID
                #sendEmail(getEmail)

def sendEmail(sendToEmail, cIDList):
    SENDER = "Turtle Trends <teamturtleseng@gmail.com>"
    RECIPIENT = sendToEmail
    AWS_REGION = "us-east-1"
    if (len(cIDList)==1):
        SUBJECT = "Significant change in "+cIDList[0]+" trends"
    else:
        SUBJECT = "Significant change in multiple trends"
    CHARSET = "UTF-8"

    #for non-html email clients
    BODY_TEXT = ("Amazon SES Test (Python)\r\n"
                 "This email was sent with Amazon SES using the "
                 "AWS SDK for Python (Boto)."
                )

    #for normal email clients
    BODY_HTML = """<html>
    <head></head>
    <body>
      <h1>Amazon SES Test (SDK for Python)</h1>
      <p>This email was sent with
        <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
        <a href='https://aws.amazon.com/sdk-for-python/'>
          AWS SDK for Python (Boto)</a>.</p>
    </body>
    </html>
                """

    client = boto3.client('ses',region_name=AWS_REGION)

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['ResponseMetadata']['RequestId'])


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

#Email Scheduler
# application.run(use_reloader=False)
# scheduler = BackgroundScheduler()
# scheduler.start()
# # #Update Google Trends every 1 hours
# scheduler.add_job(
#     func=updateAllTrends,
#     trigger=IntervalTrigger(hours=1),
#     id='update_all_gtrends',
#     name='Updates all Google Trends companies [6hours]',
#     replace_existing=True)
# #Send daily emails
# scheduler.add_job(
#     func=updateAllTrends,
#     trigger=IntervalTrigger(hours=24),
#     id='email_daily',
#     name='Send daily email',
#     replace_existing=True)
# #Send weekly emails
# scheduler.add_job(
#     func=updateAllTrends,
#     trigger=IntervalTrigger(days=7),
#     id='email_weekly',
#     name='Send weekly email',
#     replace_existing=True)
# #Send monthly
# scheduler.add_job(
#     func=updateAllTrends,
#     trigger=IntervalTrigger(weeks=4),
#     id='email_monthly',
#     name='Send monthly email',
#     replace_existing=True)
# # #Update IndicoIO Sentiment every 24 hours
# # scheduler.add_job(
# #     func=updateSentiment,
# #     trigger=IntervalTrigger(hours=24),
# #     id='update_all_sentiments',
# #     name='Updates all Article Sentiments [24hours]',
# #     replace_existing=True)
# # Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())





# this will change with a gui
application.add_url_rule('/', 'index', (lambda: base()))
application.add_url_rule('/newsapi/', 'apiIndex', (lambda: apiIndex()))


if __name__ == '__main__':
    application.run(debug=True)
    #run timer
        #every hour
        #hourlyTrendCheck()
