from APIClasses import turtleTesting, penguinTesting


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
        api.output += '\n['+test["TestID"].rjust(2, '0')+"] "+test["Description"].ljust(api.longestTestName)+" : "

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
    apiList = []
    # apiList.append(turtleTesting())
    apiList.append(penguinTesting())
    for api in apiList:
        testAPI(api)


runTests()
