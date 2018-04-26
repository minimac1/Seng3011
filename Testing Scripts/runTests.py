from APIClasses import turtleTesting, penguinTesting, hawkTesting, lionTesting


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


def getSummary(passed, total, skipped):
    retString = "\n\nSummary: "
    retString += str(passed)+"/"+str(total)+" passed, "+str(skipped)+" skipped"
    return retString


def writeOutput(name, text):
    with open(name+"Out.txt", 'w+') as outfile:
        outfile.write(text)


def testAPI(api):
    print("\n\nRunning Tests on "+api.name+"'s News API:")
    gui = GUILine(len(api.tests))
    passed = 0
    skipped = 0

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

    gui.update("Finished Tests".ljust(api.longestTestName+15))
    print("\n\tPassed "+str(passed)+" of "+str(len(api.tests)-skipped), end='')

    if(skipped > 0):
        print(", Skipped "+str(skipped), end='')

    print("")

    api.output += getSummary(passed, len(api.tests)-skipped, skipped)
    writeOutput(api.name, api.output)


def runTests():
    apiList = []
    apiList.append(turtleTesting())
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
