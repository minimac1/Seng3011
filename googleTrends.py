from flask import Flask, render_template, Blueprint, session, request, Response
from flask_restful import Resource, Api, reqparse, fields, marshal
from datetime import datetime, timedelta, date, tzinfo
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from botocore.exceptions import ClientError
import v4_0
import csv
import collections
import json
import requests
import boto3
import re
import psycopg2
from pytrends.request import TrendReq
#utcOffset = tz.utcoffset(dt)
pytrends = TrendReq(hl='en-us', tz=-600) #change when functioning

# connect to database
try:
    dbConn = psycopg2.connect("dbname='ebdb' user='teamturtleseng' password='SENG3011!' host='aaiweopiy3u4yv.ccig0wydbyxl.ap-southeast-2.rds.amazonaws.com' port='5432'")
    dbCur = dbConn.cursor()
except:
    print('unable to connect to the database')

# Num weeks is integer of number of weeks for range (max 3)
# Query is string to query google with
# Returns array of trends
#   index 0                is todays trends
#   index (numWeeks*7)-1   is the end of the array
def trendFromNumWeek(numWeeks, query):
    kw_list = [query]
    pytrends.build_payload(kw_list, cat=0, timeframe='now 7-d', geo='', gprop='')
    dfCurrWeek = pytrends.interest_over_time();
    pytrends.build_payload(kw_list, cat=0, timeframe='today 3-m', geo='', gprop='')
    dfCurrMonth = pytrends.interest_over_time();
    resDict = {}

    for currdate in dfCurrMonth[query].index:
        if not str(currdate.date()) in resDict:
            resDict[str(currdate.date())] = dfCurrMonth[query].get(currdate)
        elif (dfCurrMonth[query].get(currdate) > resDict[str(currdate.date())]):
            resDict[str(currdate.date())] = dfCurrMonth[query].get(currdate)

    for currdate in dfCurrWeek[query].index:
        if not str(currdate.date()) in resDict:
            resDict[str(currdate.date())] = dfCurrWeek[query].get(currdate)
        elif (dfCurrWeek[query].get(currdate) > resDict[str(currdate.date())]):
            resDict[str(currdate.date())] = dfCurrWeek[query].get(currdate)


    dictIter = collections.OrderedDict(sorted(resDict.items()))
    numDays = numWeeks*7
    resArray = []
    for x in range(0, numDays):
        curr = dictIter.popitem()
        resArray.append(curr[1])
    return resArray

def getCIDList():
    resList = []
    try:
        dbCur.execute("""SELECT DISTINCT company FROM userFollows;""")
        rows = dbCur.fetchall()
        for row in rows:
            curCid = row[0]
            resList.append(curCid)
    except:
        return "Error geting company list"
    return resList

#update CompanyID with alias to google
def updateGoogleTrends(companyID, dateFrom, dateTo):
    companyID = companyID.upper()
    alias = v4_0.asxCodeToName(companyID)
    cidNoTrail = v4_0.removeExchangeCode(companyID)
    print("Updating " + companyID + " W/O Trails: " + cidNoTrail + ". Alias: " + alias)
    kw_list = [alias, cidNoTrail]
    dateToHour = dateTo.hour
    dateFromHour = dateFrom.hour
    dateRange = str(dateFrom.date())+"T"+str(dateFromHour) + " " + str(dateTo.date())+"T"+str(dateToHour)
    print("DateFrom: [" + str(dateFrom) + "] DateTo: [" + str(dateTo) + "] DateRange: " + dateRange)
    pytrends.build_payload(kw_list, cat=0, timeframe=dateRange, geo='', gprop='')
    df = pytrends.interest_over_time();

    for currdate in df[cidNoTrail].index:
        newRes = df[cidNoTrail].get(currdate)
        newRes = newRes.item()
        dateString = str(currdate.date())
        hourString = str(currdate.hour)
        #print("Date: " + str(currdate.date()) + "Hour: " + str(currdate.hour) + " Res: "+str(newRes))
        dbCur.execute("""SELECT trend from trendData where cid=%s and date=%s and hour=%s;""", (companyID, dateString, hourString))
        rowCount = dbCur.rowcount
        if (rowCount == 0): #Not in table so add
            #print("Not in table")
            dbCur.execute("""INSERT INTO trendData VALUES (%s,%s,%s,%s);""", (companyID, dateString, hourString, newRes))
        else: #In table so get highest
            rows = dbCur.fetchall()
            for row in rows:
                curRes = row[0]
                #print("In table: ["+str(curRes)+"]")
                if (newRes>curRes):
                    #print ("Res: " + str(newRes) + " > " + str(curRes))
                    dbCur.execute("""DELETE FROM trendData WHERE cid=%s and date=%s and hour=%s and trend=%s;""", (companyID, dateString, hourString, curRes))
                    dbCur.execute("""INSERT INTO trendData VALUES (%s,%s,%s,%s);""", (companyID, dateString, hourString, newRes))
                #else:
                    #print("lower value [" +str(newRes)+"] <= ["+ str(curRes) + "]")
    for currdate in df[alias].index:
        newRes = df[alias].get(currdate)
        newRes = newRes.item()
        dateString = str(currdate.date())
        hourString = str(currdate.hour)
        #print("Date: " + str(currdate.date()) + "Hour: " + str(currdate.hour) + " Res: "+str(newRes))
        dbCur.execute("""SELECT trend from trendData where cid=%s and date=%s and hour=%s;""", (companyID, dateString, hourString))
        rowCount = dbCur.rowcount
        if (rowCount == 0): #Not in table so add
            #print("Not in table")
            dbCur.execute("""INSERT INTO trendData VALUES (%s,%s,%s,%s);""", (companyID, dateString, hourString, newRes))
        else: #In table so get highest
            rows = dbCur.fetchall()
            for row in rows:
                curRes = row[0]
                #print("In table: ["+str(curRes)+"]")
                if (newRes>curRes):
                    #print ("Res: " + str(newRes) + " > " + str(curRes))
                    dbCur.execute("""DELETE FROM trendData WHERE cid=%s and date=%s and hour=%s and trend=%s;""", (companyID, dateString, hourString, curRes))
                    dbCur.execute("""INSERT INTO trendData VALUES (%s,%s,%s,%s);""", (companyID, dateString, hourString, newRes))
                #else:
                    #print("lower value [" +str(newRes)+"] <= ["+ str(curRes) + "]")

    dbConn.commit()

def updateAllTrends():
    print("[GTrends] Updating All Google Trends...\n");
    dbCIDList = getCIDList();
    for curCID in dbCIDList:
        curCID = curCID.upper()
        dateTo = datetime.now()
        tenHours = timedelta(hours=10) #utc time
        dateTo = dateTo - tenHours
        oneday = timedelta(days=1)
        dateFrom = dateTo - oneday
        updateGoogleTrends(curCID, dateFrom, dateTo)
        sevenDays = timedelta(days=7)
        weekoneTo = dateTo - sevenDays
        weekoneFrom = dateFrom - sevenDays
        updateGoogleTrends(curCID, weekoneFrom, weekoneTo)
        weektwoTo = weekoneTo - sevenDays
        weektwoFrom = weekoneFrom - sevenDays
        updateGoogleTrends(curCID, weektwoFrom, weektwoTo)
        weekthreeTo = weektwoTo - sevenDays
        weekthreeFrom = weektwoFrom - sevenDays
        updateGoogleTrends(curCID, weekthreeFrom, weekthreeTo)
    print("[GTrends] Completed Updating All Google Trends\n");


def updateMonthlyTrends(cid):
    print("[GTrends] Updating Monthly Google Trends...\n");
    curCID = cid.upper()
    dbCIDList = getCIDList();
    if (curCID in dbCIDList):
        print("[GTrends] Already in list, should be updated every 6 hours\n")
        print("[GTrends] Exiting...\n")
    else:
        dateTo = datetime.now()
        tenHours = timedelta(hours=10) #utc time
        dateTo = dateTo - tenHours
        oneday = timedelta(days=1)
        dateFrom = dateTo - oneday
        updateGoogleTrends(curCID, dateFrom, dateTo)
        sevenDays = timedelta(days=7)
        weekoneTo = dateTo - sevenDays
        weekoneFrom = dateFrom - sevenDays
        updateGoogleTrends(curCID, weekoneFrom, weekoneTo)
        weektwoTo = weekoneTo - sevenDays
        weektwoFrom = weekoneFrom - sevenDays
        updateGoogleTrends(curCID, weektwoFrom, weektwoTo)
        weekthreeTo = weektwoTo - sevenDays
        weekthreeFrom = weektwoFrom - sevenDays
        updateGoogleTrends(curCID, weekthreeFrom, weekthreeTo)
        print("[GTrends] Completed Updating All Google Trends\n");

#dbCur.execute("""SELECT trend from trendData where cid=%s and date=%s and hour=%s;""", (companyID, dateString, hourString))
# rows = dbCur.fetchall()
# for row in rows:
#     curRes = row[0]
def getCurrentChange(cid):
    cid = cid.upper()
    curDate = datetime.now()
    tenHours = timedelta(hours=10) #utc time
    curDate = curDate - tenHours
    oneHour = timedelta(hours=1)
    oneday = timedelta(days=1)
    # dateFrom = dateTo - oneday
    changeRes = []
    todayChange = 0
    checkDate = curDate
    for x in range(0,24):
        #print("Hour: " + str(x))
        curDateString = str(checkDate.date())
        hourString = str(checkDate.hour)
        dbCur.execute("""SELECT trend from trendData where cid=%s and date=%s and hour=%s;""", (cid, curDateString, hourString))
        rowCount = dbCur.rowcount
        if (rowCount == 0): #Not in table so add
            #print("Not in table")
            #curDateFrom = checkDate - oneday
            #updateGoogleTrends(cid, curDateFrom, checkDate)
            #getCurrentChange(cid) #remove this and return 0 if slow
            #break;
            todayChange = todayChange + 0
        else:
            rows = dbCur.fetchall()
            for row in rows:
                todayChange = todayChange + row[0]
                #print("Today Change: " + str(todayChange))
        checkDate = checkDate - oneHour
    todayChange = todayChange/24
    #print("Today Change: " + str(todayChange))
    prevChangeTotal = 0
    sevenDays = timedelta(days=7)
    sixDays = timedelta(days=6)
    checkDate = curDate - sevenDays
    for y in range(0,3):
        prevChange = 0
        for x in range(0,24):
            #print("Hour: " + str(x))
            curDateString = str(checkDate.date())
            hourString = str(checkDate.hour)
            #print("Date: " + curDateString + "Hour: " + hourString)
            dbCur.execute("""SELECT trend from trendData where cid=%s and date=%s and hour=%s;""", (cid, curDateString, hourString))
            rowCount = dbCur.rowcount
            if (rowCount == 0): #Not in table so add
                #print("Not in table")
                #curDateFrom = checkDate - oneday
                #updateGoogleTrends(cid, curDateFrom, checkDate)
                #getCurrentChange(cid) #remove this and return 0 if slow
                #break;
                prevChange = prevChange + 0
            else:
                rows = dbCur.fetchall()
                for row in rows:
                    prevChange = prevChange + row[0]
                    #print("["+str(x)+"] Today Change: " + str(row[0]))
            checkDate = checkDate - oneHour
        prevChange = prevChange/24
        #print("Prev Change: " + str(prevChange))
        prevChangeTotal = prevChangeTotal + prevChange
        #print("Final Change: " + str(prevChangeTotal))
        checkDate = checkDate - sixDays
    prevChangeTotal = prevChangeTotal/3
    #print("Final Check: " + str(prevChangeTotal))
    change = todayChange - prevChangeTotal
    if (prevChangeTotal == 0):
        pChangeRounded = 0
    else:
        percentChange = (change/prevChangeTotal)*100
        pChangeRounded = str(round(percentChange,3))
        #print("Percentage Change: " + str(pChangeRounded))
    return pChangeRounded

#updateAllTrends()
getCurrentChange("CBA.AX")

#EMAIL STUFF
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


#
