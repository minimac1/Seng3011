from APIClasses import turtleTestingOnline, turtleTestingLocal, penguinTesting, hawkTesting, lionTesting
import datetime


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


def getSummary(passed, total, skipped, startTime, endTime):
    difTime = endTime-startTime
    (minDif, secDif) = divmod(difTime.days * 86400 + difTime.seconds, 60)

    retString = "Summary:\n"
    retString += "\t"+str(passed)+"/"+str(total)+" passed, "+str(skipped)+" skipped\n"
    retString += "\tTests started "+("("+startTime.strftime("%d %b %Y %H:%M:%S")+")").ljust(25)+"\n"
    retString += "\tTests ended   "+("("+endTime.strftime("%d %b %Y %H:%M:%S")+")").ljust(25)+"\n"
    retString += "\tDuration      "+("("+str(minDif)+" minutes, "+str(secDif)+" seconds)").ljust(25)+"\n"
    retString += "\n\n"
    return retString


def writeOutput(name, text):
    with open("Output - "+name+".txt", 'w+') as outfile:
        outfile.write(text)


def testAPI(api):
    print("\n\nRunning Tests on "+api.name+"'s News API:")
    gui = GUILine(len(api.tests))
    passed = 0
    skipped = 0
    startTime = datetime.datetime.now()

    for test in api.tests:
        gui.update(("Running Test: " + test["Description"]).ljust(api.longestTestName+15))
        # add description to start of line
        api.output += '['+test["TestID"].rjust(2, '0')+"] "+test["Description"].ljust(api.longestTestName)+" : \t"

        # run the test and get a pass or error
        (testOutput, pas, ski) = api.runTest(test)

        if(pas):
            passed += 1
        if(ski):
            skipped += 1
        api.output += testOutput+"\n"

        gui.increment()

    endTime = datetime.datetime.now()
    gui.update("Finished Tests".ljust(api.longestTestName+15))
    print("\n\tPassed "+str(passed)+" of "+str(len(api.tests)-skipped), end='')

    if(skipped > 0):
        print(", Skipped "+str(skipped), end='')

    print("")

    api.output = getSummary(passed, len(api.tests)-skipped, skipped, startTime, endTime) + api.output
    writeOutput(api.name, api.output)


def runTests():
    apiList = []
    apiList.append(turtleTestingOnline())
    apiList.append(turtleTestingLocal())
    apiList.append(penguinTesting())
    apiList.append(hawkTesting())
    apiList.append(lionTesting())
    chosenAPIs = []

    for api in apiList:
        choice = input("Do you want to run the tests on team "+api.name+"'s API? (y/n)").lower()
        while(choice != "y" and choice != "n"):
            print(choice)
            choice = input("Please enter y or n! ").lower()
        if(choice == 'y'):
            chosenAPIs.append(api)

    for api in chosenAPIs:
        testAPI(api)


runTests()
