import requests
import csv


def readTestDataCSV():
        with open("testData.csv", newline='') as csvfile:
            testList = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            newlist = []
            for row in testList:
                newlist.append(row)
        return newlist


def getTurtleURL(startDate, endDate, companyID, topic):
    url = "http://seng3011-turtle.ap-southeast-2.elasticbeanstalk.com/newsapi/v2.0/query?"
    return (url+"startDate="+startDate+"&endDate="+endDate+"&companyId="+companyID+"&topic="+topic)


def getJSON(url):
    r = requests.get(url)
    return r.json()["NewsDataSet"]


def runTests():
    testData = readTestDataCSV()

    for dat in testData:
        url = getTurtleURL(dat["startDate"], dat["endDate"], dat["companyID"], dat["topic"])
        getJSON(url)


runTests()
