import requests
import csv


def readTestDataCSV():
        with open("testData.csv", newline='') as csvfile:
            testList = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            newlist = []
            for row in testList:
                newlist.append(row)
        return newlist


def getJSON(url):
    r = requests.get(url)
    if(r.status_code == 200):
        return r.json()
    else:
        return {"errorCode": r.status_code}


class TurtleTesting:
    name = "Turtle"
    tests = []
    output = ""
    longestTestName = 0

    def __init__(self):
        self.tests = readTestDataCSV()
        self.longestTestName = max(len(k["Description"]) for k in self.tests)

    def getURL(self, startDate, endDate, companyID, topic):
        url = "http://seng3011-turtle.ap-southeast-2.elasticbeanstalk.com/newsapi/v2.0/query?"
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
                if ("companyid" in exeRes[1].lower()):
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
        bool = self.checkCorrect(res, test["expected return"])
        retString = "Test Passed"
        if(not bool):
            retString = "! ! ! Test Failed"

        retString += ". Expected \""+test["expected return"]+"\" got \""+res+"\""
        return (retString, bool)


class GUILine:
    totalTests = 0
    finished = 0

    def __init__(self, total):
        self.totalTests = total

    def increment(self):
        self.finished += 1

    def getBar(self):
        totChars = 20
        filledChars = int(totChars*(self.finished/self.totalTests))
        barString = "["+('#'*filledChars).ljust(totChars, "-")+"]"
        return barString

    def update(self, note):
        newLine = "\r\t"
        newLine += str(self.finished) + "/" + str(self.totalTests)
        newLine += " " + self.getBar()
        newLine += " " + note
        print(newLine, end='')


def writeOutput(name, text):
    with open(name+"Out.txt", 'w+') as outfile:
        outfile.write(text)


def testAPI(api):
    print("\n\nRunning Tests on "+api.name+"'s News API:")
    gui = GUILine(len(api.tests))
    passed = 0

    for test in api.tests:
        gui.update(("Running Test: " + test["Description"]).ljust(api.longestTestName+15))
        # add description to start of line
        api.output += '\n['+test["TestID"].rjust(2,'0')+"] "+test["Description"].ljust(api.longestTestName)+" : "

        # run the test and get a pass or error
        (testOutput, res) = api.runTest(test)

        if(res):
            passed += 1
        api.output += testOutput

        gui.increment()

    gui.update("Finished Tests".ljust(api.longestTestName+15))
    print("\n\t passed "+str(passed)+" of "+str(len(api.tests)))

    writeOutput(api.name, api.output)


def runTests():
    turt = TurtleTesting()
    testAPI(turt)


runTests()
