import requests
import csv


def readTestDataCSV():
        with open("testData2.csv", newline='') as csvfile:
            testList = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            newlist = []
            for row in testList:
                newlist.append(row)
        return newlist


def getJSON(url):
    r = requests.get(url)
    if(r.status_code == 200 or r.status_code == 400):
        return r.json()
    else:
        return {"errorCode": r.status_code}


class turtleTesting:
    name = "Turtle"
    tests = []
    output = ""
    longestTestName = 0

    def __init__(self):
        self.tests = readTestDataCSV()
        self.longestTestName = max(len(k["Description"]) for k in self.tests)

    def getURL(self, startDate, endDate, companyID, topic):
        url = "http://seng3011-turtle.ap-southeast-2.elasticbeanstalk.com/newsapi/v3.0/query?"
        url += "startDate="+startDate
        url += "&endDate="+endDate
        if(companyID != ""):
            if(companyID == "-"):
                url += "&companyId="
            else:
                url += "&companyId="+companyID
        if(topic != ""):
            if(topic == "-"):
                url += "&topic="
            else:
                url += "&topic="+topic
        return (url)

    def getResult(self, url):
        json = getJSON(url)
        if("Developer Notes" in json.keys() and "Execution Result" in json["Developer Notes"]):
            exeRes = json["Developer Notes"]["Execution Result"]
            if(exeRes[0].startswith("Successful")):
                return "successful API call"
            else:
                if ("date" in exeRes[1].lower()):
                    return "invalid Date"
                if ("company" in exeRes[1].lower()):
                    return "invalid Company"
                if ("instrument id" in exeRes[1].lower()):
                    return "invalid Company"
        if("errorCode" in json.keys()):
            return str(json["errorCode"])
        return "fail"

    def checkCorrect(self, out, correct):
        if(correct == out):
            return True
        return False

    def runTest(self, test):
        url = self.getURL(test["startDate"], test["endDate"], test["companyID"], test["topic"])
        res = self.getResult(url)
        passed = self.checkCorrect(res, test["expected return"])
        retString     = "      Test Passed"
        if(not passed):
            retString = "! ! ! Test Failed"

        retString += ". Expected \""+test["expected return"]+"\" got \""+res+"\" ["+url+"]"
        return (retString, passed, False)


class penguinTesting:
    name = "Penguin"
    tests = []
    output = ""
    longestTestName = 0

    def __init__(self):
        self.tests = readTestDataCSV()
        self.longestTestName = max(len(k["Description"]) for k in self.tests)

    def getURL(self, startDate, endDate, companyID, topic):
        newCompanyID = companyID.replace('-', "%20").replace('_', ',')
        newTopic = topic.replace('-', "%20").replace('_', ',')

        url = "http://seng3011-penguin.herokuapp.com/api2?"
        url += "start_date="+startDate
        url += "&end_date="+endDate
        if(companyID != ""):
            if(companyID == "-"):
                url += "&company_id="
            else:
                url += "&company_id="+newCompanyID
        if(topic != ""):
            if(topic == "-"):
                url += "&topics="
            else:
                url += "&topics="+newTopic
        return (url)

    def getResult(self, url):
        json = getJSON(url)
        if(json["newsDataSet"] == "" and ("No results were returned, try more general parameters." in json["log"])):
            return "successful API call"
        if(len(json["newsDataSet"]) != 0 and ("Operation completed successfully" in json["log"])):
            return "successful API call"
        if("specify at least one company of interest" in json["log"]):
            return "Error: specify at least one company of interest"
        if("Error occured. The following company does not exist in our records" in json["log"]):
            return "invalid Company"
        if("Error occured. " in json["log"] and "_date" in json["log"].split("Error occured. ", 1)[1]):
            return "invalid Date"
        if("errorCode" in json.keys()):
            return str(json["errorCode"])
        return "fail"

    def checkCorrect(self, out, correct):
        if(correct == out):
            return True
        return False

    def runTest(self, test):
        url = self.getURL(test["startDate"], test["endDate"], test["companyID"], test["topic"])
        res = self.getResult(url)
        passed = self.checkCorrect(res, test["expected return"])
        retString     = "      Test Passed"
        if(not passed):
            retString = "! ! ! Test Failed"

        retString += ". Expected \""+test["expected return"]+"\" got \""+res+"\" ["+url+"]"
        return (retString, passed, False)


class hawkTesting:
    name = "Rooster Hawk"
    tests = []
    output = ""
    longestTestName = 0

    def __init__(self):
        self.tests = readTestDataCSV()
        self.longestTestName = max(len(k["Description"]) for k in self.tests)

    def getURL(self, startDate, endDate, companyID, topic):
        newCompanyID = companyID.replace('-', "%20").replace('_', ',')
        newTopic = topic.replace('-', "%20").replace('_', ',')
        url = "http://seng.fmap.today/v2/news?"
        url += "start_date="+startDate
        url += "&end_date="+endDate
        if(companyID != ""):
            if(companyID == "-"):
                url += "&company="
            else:
                url += "&company="+newCompanyID
        if(topic != ""):
            if(topic == "-"):
                url += "&topic="
            else:
                url += "&topic="+newTopic
        return (url)

    def getResult(self, url):
        json = getJSON(url)
        if("eventDetails" in json.keys() and "details" in json["eventDetails"]):
            details = json["eventDetails"]["details"]
            if("errorName" in details.keys()):
                return details["errorName"]
        if("status" in json.keys()):
            if(json["status"] == "ok"):
                return "successful API call"
        if("errorCode" in json.keys()):
            return str(json["errorCode"])
        return "fail"

    def checkCorrect(self, out, correct):
        if(correct == out):
            return True
        if(out == "ParametersMissing"):
            if(correct == "invalid Company" or correct == "invalid Date"):
                return True
        return False

    def runTest(self, test):
        url = self.getURL(test["startDate"], test["endDate"], test["companyID"], test["topic"])
        if(test["expected return"] == "invalid Company"):
            retString = "   ! Test Skipped. Rooster does not reject incorrect companies ["+url+"]"
            return (retString, False, True)
        else:
            res = self.getResult(url)
            passed = self.checkCorrect(res, test["expected return"])
            retString = "      Test Passed"
            if(not passed):
                retString = "! ! ! Test Failed"

            retString += ". Expected \""+test["expected return"]+"\" got \""+res+"\" ["+url+"]"
            return (retString, passed, False)


class lionTesting:
    name = "Lion"
    tests = []
    output = ""
    longestTestName = 0

    def __init__(self):
        self.tests = readTestDataCSV()
        self.longestTestName = max(len(k["Description"]) for k in self.tests)

    def getURL(self, startDate, endDate, companyID, topic):
        url = "http://api.lionnews.net/news?"
        url += "start_date="+startDate
        url += "&end_date="+endDate
        if(companyID != ""):
            if(companyID == "-"):
                url += "&companynames="
            else:
                url += "&companynames="+companyID
        if(topic != ""):
            if(topic == "-"):
                url += "&topic="
            else:
                url += "&topic="+topic
        return (url)

    def getResult(self, url):
        json = getJSON(url)
        if("response" in json.keys() and "status" in json["response"]):
            status = json["response"]["status"]
            if(status == "ok"):
                return "successful API call"
            elif(status == "error"):
                if ("date" in json["response"]["message"].lower()):
                    return "invalid Date"
        if("errorCode" in json.keys()):
            return str(json["errorCode"])
        return "fail"

    def checkCorrect(self, out, correct):
        if(correct == out):
            return True
        return False

    def runTest(self, test):
        url = self.getURL(test["startDate"], test["endDate"], test["companyID"], test["topic"])
        if(test["expected return"] == "invalid Company"):
            retString = "   ! Test Skipped. Lion does not reject incorrect companies ["+url+"]"
            return (retString, False, True)
        else:
            res = self.getResult(url)
            passed = self.checkCorrect(res, test["expected return"])
            retString = "      Test Passed"
            if(not passed):
                retString = "! ! ! Test Failed"

            retString += ". Expected \""+test["expected return"]+"\" got \""+res+"\" ["+url+"]"
            return (retString, passed, False)
