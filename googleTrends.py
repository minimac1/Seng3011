from flask import Flask, render_template,Blueprint
from flask_restful import Resource, Api, reqparse, fields, marshal
from datetime import datetime
import csv
import json
import requests
import re
import datetime
from pytrends.request import TrendReq
pytrends = TrendReq(hl='en-us', tz=-600) #change when functioning
pytrendsUserList = []
pytrendsCompanyList = []


pytrendsInstance = {}
pytrendsInstance['CompanyID'] = fields.String
pytrendsInstance['Current Hour Results'] = fields.Integer
pytrendsInstance['Hourly Change (%)'] = fields.String
#Store each user, with their set of company ids (no duplicates)
userPytrends = {}
userPytrends['UserID'] = fields.String
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

#update CompanyID with alias to google
def updateGoogleTrends(companyID, alias):
    kw_list = [alias]
    pytrends.build_payload(kw_list, cat=0, timeframe='now 1-H', geo='', gprop='')
    df = pytrends.interest_over_time();

    found = False
    newRes = df[alias].sum()
    for currCID in pytrendsCompanyList:
        if (currCID['CompanyID'] == companyID):
            found = True
            prevRes = currCID['Current Hour Results']
            change = newRes - prevRes
            percentChange = (change/prevRes)*100
            currCID['Current Hour Results'] = newRes
            currCID['Hourly Change (%)'] = round(percentChange,2)

    #If not found, create
    if not found:
        newCID = {'CompanyID' : companyID,
                'Current Hour Results' : newRes,
                'Hourly Change (%)' : "0"}
        pytrendsCompanyList.append(newCID)

def removeCIDfromCompanyList(CID):
    for companyInstance in pytrendsCompanyList:
        if (companyInstance['CompanyID'] == CID):
            pytrendsCompanyList.remove(companyInstance)

#add user with provided set of CIDs
def addGoogleTrendsUser(userID, listOfCIDs):
    currUser = {'UserID' : userID, 'CompanyIDList' : listOfCIDs}
    pytrendsUserList.append(currUser)
    for CID in listOfCIDs:
        updateGoogleTrends(CID, CID)

#assumes user exists, doesnt add duplicate
def addIDsToGoogleTrendsUser(userID, newCID):
    for currUser in pytrendsUserList:
        if (currUser['UserID'] == userID):
            if (not newCID in currUser['CompanyIDList']):
                currUser['CompanyIDList'].append(newCID)
                updateGoogleTrends(newCID, newCID)

def removeIDfromGoogleTrendsUser(userID, idToRemove):
    count = 0
    for currUser in pytrendsUserList:
        if (idToRemove in currUser['CompanyIDList']):
            count++
            if (currUser['UserID'] == userID):
                currUser['CompanyIDList'].remove(idToRemove)
    #If this was the only occurance of this CID, remove from pytrendsCompanyList
    if (count==1):
        removeCIDfromCompanyList(idToRemove)

addGoogleTrendsUser('thisismycookieID', ['ANZ.ax', 'WOW.ax'])
updateGoogleTrends('ANZ.ax', 'ANZ')
updateGoogleTrends('WOW.ax', 'Woolworths')
print("\n.....Printing Company List ['ANZ.ax', 'WOW.ax'].....\n")
print(companyListAsJson())
print("\n.....Call update again to show change.....\n")
updateGoogleTrends('ANZ.ax', 'ANZ')
updateGoogleTrends('WOW.ax', 'Woolworths')
print(companyListAsJson())
print("\n.....Now printinging user database.....\n")
print(userListAsJson())
