from flask import Flask, render_template,Blueprint
from flask_restful import Resource, Api, reqparse, fields, marshal
from datetime import datetime
import v4_0
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
pytrendsInstance['Hourly Change (%)'] = fields.Integer
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
    kw_list = [alias]
    pytrends.build_payload(kw_list, cat=0, timeframe='now 1-H', geo='', gprop='')
    df = pytrends.interest_over_time();

    found = False
    newRes = df[alias].sum()
    for currInstance in pytrendsCompanyList:
        if (currInstance['CompanyID'] == companyID):
            found = True
            prevRes = currInstance['Current Hour Results']
            change = newRes - prevRes
            percentChange = (change/prevRes)*100
            currInstance['Current Hour Results'] = newRes
            currInstance['Hourly Change (%)'] = round(percentChange,4)

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

# #add user with provided set of CIDs
# def addGoogleTrendsUser(userID, listOfCIDs):
#     currUser = {'UserID' : userID, 'CompanyIDList' : listOfCIDs}
#     pytrendsUserList.append(currUser)
#     for CID in listOfCIDs:
#         updateGoogleTrends(CID, CID)

#doesnt add duplicate
def addIDsToGoogleTrendsUser(userID, newCID, newCIDalias):
    userExists = False
    for currUser in pytrendsUserList:
        if (currUser['UserID'] == userID):
            userExists = True
            if (not newCID in currUser['CompanyIDList']):
                currUser['CompanyIDList'].append(newCID)
                updateGoogleTrends(newCID, newCIDalias)
    if (not userExists):
        currUser = {'UserID' : userID, 'CompanyIDList' : [newCID]}
        pytrendsUserList.append(currUser)
        updateGoogleTrends(newCID, newCIDalias)

def removeIDfromGoogleTrendsUser(userID, idToRemove):
    count = 0
    for currUser in pytrendsUserList:
        if (idToRemove in currUser['CompanyIDList']):
            count += 1
            if (currUser['UserID'] == userID):
                currUser['CompanyIDList'].remove(idToRemove)
    #If this was the only occurance of this CID, remove from pytrendsCompanyList
    if (count==1):
        removeCIDfromCompanyList(idToRemove)

addIDsToGoogleTrendsUser('thisismycookieID', 'ANZ.ax', 'ANZ')
addIDsToGoogleTrendsUser('thisismycookieID', 'CBA.ax', 'Commonwealth Bank of Australia')
print("\n.....Printing Company List ['ANZ.ax', 'CBA.ax'].....\n")
print(companyListAsJson())
print("\n.....Call update again to show change.....\n")
updateAllTrends()
print(companyListAsJson())
print("\n.....Now printinging user database.....\n")
print(userListAsJson())
