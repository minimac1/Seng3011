from flask import Flask, render_template,Blueprint
from flask_restful import Resource, Api, reqparse, fields, marshal
from datetime import datetime, timedelta, date
import v4_0
import csv
import json
import requests
import re
from pytrends.request import TrendReq
pytrends = TrendReq(hl='en-us', tz=-600) #change when functioning
pytrendsUserList = []
pytrendsCompanyList = []

#
# IMPORTNANT FUNCTIONS [READ ME!]
# getCurrentChange("companyid")
# addIDsToGoogleTrendsUser('userid', 'companyid', 'companyFullname')
#

pytrendsInstance = {}
pytrendsInstance['CompanyID'] = fields.String
pytrendsInstance['Current Hour Results'] = fields.Integer
pytrendsInstance['Hourly Change (%)'] = fields.Integer
#Store each user, with their set of company ids (no duplicates)
userPytrends = {}
userPytrends['UserEmail'] = fields.String
userPytrends['CompanyIDList'] = fields.List(fields.String)


def userListAsJson():
    output_fields = {}
    output_fields['Google Trends Users'] = fields.List(fields.Nested(userPytrends))
    data = {'Google Trends Users' : pytrendsUserList}
    return marshal(data, output_fields)

def companyListAsJson():
    output_fields = {}
    output_fields['Google Trends Companies'] = fields.List(fields.Nested(pytrendsInstance))
    data = {'Google Trends Companies' : pytrendsCompanyList}
    return marshal(data, output_fields)

def getCurrentChange(cid):
    for curInstance in pytrendsCompanyList:
        if (curInstance['CompanyID']==cid):
            return curInstance['Hourly Change (%)']

def updateAllTrends():
    for currInstance in pytrendsCompanyList:
        curCID = currInstance['CompanyID']
        curAlias = v4_0.fullName(curCID)
        print("Current CID: " + curCID)
        print("Current Alias: " + curAlias)
        updateGoogleTrends(curCID, curAlias)


#update CompanyID with alias to google
def updateGoogleTrends(companyID, alias):
    print("updating " + companyID)
    kw_list = [alias]
    #pytrends.build_payload(kw_list, cat=0, timeframe='now 1-H', geo='', gprop='')
    today = date.today()
    #print(str(today))
    pytrends.build_payload(kw_list, cat=0, timeframe='now 1-d', geo='', gprop='')
    df = pytrends.interest_over_time();
    newRes = df[alias].sum()
    #print("newres: " + str(newRes))
    numMonths = 4
    currDate = today
    sevenDays = timedelta(days=7)
    changeSum = 0
    for x in range(0, numMonths):
        oneweekago = currDate - sevenDays
        #print("oneweekago: " + str(oneweekago))
        dateRange = str(oneweekago)+'T00 '+str(oneweekago)+'T23'
        #print("dateRange: " + str(dateRange))
        pytrends.build_payload(kw_list, cat=0, timeframe=str(dateRange), geo='', gprop='')
        df = pytrends.interest_over_time();
        #print("changeSum: "+str(changeSum)+" inc: " + str(df[alias].sum()))
        changeSum = changeSum + df[alias].sum()
        currDate = oneweekago

    #print("done loop")
    #print("total change: " + str(changeSum))
    average = (changeSum/numMonths)
    #print("average: " + str(average))
    change = newRes - average
    percentChange = (change/average)*100
    #print("percentagechange: " + str(round(percentChange,4)))
    cidExits = False
    for currInstance in pytrendsCompanyList:
        if (currInstance['CompanyID'] == companyID):
            cidExits = True
            print("found"+ str(companyID) + "[updateGoogleTrends]")
            currInstance['Current Hour Results'] = newRes
            currInstance['Hourly Change (%)'] = round(percentChange,4)

    if (not cidExits):
        print(str(companyID)+" doesnt exist, adding new cid [updateGoogleTrends]")
        newInstance = {'CompanyID' : companyID,
                       'Current Hour Results' : newRes,
                       'Hourly Change (%)' : round(percentChange,4)
                      }
        pytrendsCompanyList.append(newInstance)

def removeCIDfromCompanyList(CID):
    for companyInstance in pytrendsCompanyList:
        if (companyInstance['CompanyID'] == CID):
            pytrendsCompanyList.remove(companyInstance)

# #add user with provided set of CIDs
# def addGoogleTrendsUser(userEmail, listOfCIDs):
#     currUser = {'UserEmail' : userEmail, 'CompanyIDList' : listOfCIDs}
#     pytrendsUserList.append(currUser)
#     for CID in listOfCIDs:
#         updateGoogleTrends(CID, CID)

#doesnt add duplicate
def addIDsToGoogleTrendsUser(userEmail, newCID, newCIDalias):
    userExists = False
    for currUser in pytrendsUserList:
        if (currUser['UserEmail'] == userEmail):
            print("GTrends: user does exit [addIDstoUser]")
            userExists = True
            if (not newCID in currUser['CompanyIDList']):
                currUser['CompanyIDList'].append(newCID)
    if (not userExists):
        print("GTrends: user doesnt exit, adding new user [addIDstoUser]")
        currUser = {'UserEmail' : userEmail, 'CompanyIDList' : [newCID]}
        pytrendsUserList.append(currUser)
    updateGoogleTrends(newCID, newCIDalias)

def removeIDfromGoogleTrendsUser(userEmail, idToRemove):
    count = 0
    for currUser in pytrendsUserList:
        if (idToRemove in currUser['CompanyIDList']):
            count += 1
            if (currUser['UserEmail'] == userEmail):
                currUser['CompanyIDList'].remove(idToRemove)
    #If this was the only occurance of this CID, remove from pytrendsCompanyList
    if (count==1):
        removeCIDfromCompanyList(idToRemove)

#Test 1
# addIDsToGoogleTrendsUser('thisismycookieID', 'CBA.ax', 'Commonwealth Bank of Australia')
# print("\n.....Printing Company List ['ANZ.ax', 'CBA.ax'].....\n")
# print(companyListAsJson())
# print("\n.....Call update again to show change.....\n")
# updateAllTrends()
# print(companyListAsJson())
# print("\n.....Now printinging user database.....\n")
# print(userListAsJson())

#Test 2
# addIDsToGoogleTrendsUser('user', 'WOW.ax', 'Woolworths')
# print(str(getCurrentChange("WOW.ax")) + "%")
