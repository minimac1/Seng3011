from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse, fields, marshal
from datetime import datetime
import csv
import json
import requests
import re
import datetime
application = Flask(__name__)
api = Api(application)
currentVersion = 'v1.0'

defaultPageSize = 200
api_url = "http://content.guardianapis.com/search"

# Log JSON fields
log_fields = {}
log_fields['Developer Team'] = fields.String(default='Team Turtle')
log_fields['Module Name'] = fields.String(default='News API')
log_fields['API Version'] = fields.String(default=currentVersion)
#log_fields['Parameters passed'] = fields.List(fields.String)
log_fields['Parameters passed'] = fields.String
#change exec result if error occurs
log_fields['Execution Result'] = fields.List(fields.String)


@application.route('/')
@application.route('/homepage')
##@app.route('/News/<name>')
def base():
    return render_template('homepage.html')
#shud probably change these to /Api/changes etc
@application.route('/changes')
def changesPage():
    return render_template('changes.html')

@application.route('/features')
def featuresPage():
    return render_template('features.html')

@application.route('/test')
def testPage():
    return render_template('test.html')

def parseGuardian(jsonData, compNameList, params, execStartTime):
    #use compNameList to make a instrIdList
    instrIdList = []
    for c in compNameList:
        instrIdList.append(asxNameToCode(c))

    #sets up the nested fields
    newsData_fields = {}
    newsData_fields['InstrumentIDs'] = fields.List(fields.String)
    newsData_fields['CompanyNames'] = fields.List(fields.String)
    newsData_fields['TimeStamp'] = fields.String
    newsData_fields['Headline'] = fields.String
    newsData_fields['NewsText'] = fields.String
    #sets up the main field, which has the nested data
    output_fields = {}
    output_fields['Log Output'] = fields.Nested(log_fields)
    output_fields['NewsDataSet'] = fields.List(fields.Nested(newsData_fields))

    #parse the given json into a nested field, append to list
    newsDataList = []
    for x in jsonData:
        newsData = {'InstrumentIDs': instrIdList,
            'CompanyNames': compNameList,
            'TimeStamp': x["webPublicationDate"],
            'Headline': x["webTitle"],
            'NewsText': x["fields"]["bodyText"]
        }
        newsDataList.append(newsData)
    # make a json of the nested fields
    execEndTime = datetime.datetime.now()
    logOutput = {'Parameters passed' : str(params),
                'Execution Result' :
                    ["Successful", str(execStartTime),
                    str(execEndTime),  str(execEndTime-execStartTime)]
                }
    data = {'Log Output' : logOutput,
            'NewsDataSet' : newsDataList}

    # marshal orders the data alphabetically. is this a problem?!
    # return the json marshalled with the fields
    return marshal(data, output_fields)


def asxRemoveTails(companyName):
    nameEndings = [" Limited", " LTD"]
    for end in nameEndings:
        if(companyName.upper().endswith(end.upper())):
            companyName = companyName[:-len(end)]
    return companyName


def openCompanyList():
    with open('static/csv/ASXListedCompanies.csv', newline='') as csvfile:
        companyList = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        newlist = []
        for row in companyList:
            newlist.append(row)
            newlist[-1]["Company name"] = asxRemoveTails(newlist[-1]["Company name"])
    return newlist


# Checks if a given company name or ASX code is in our ASX database, returns false if not
def asxCheckValid(thingToCheck):
    thingToCheck = asxRemoveTails(thingToCheck)
    companyList = openCompanyList()
    isValid = False
    if len(thingToCheck) == 3 and any(item["ASX code"].upper() == thingToCheck.upper() for item in companyList):
        isValid = True
    elif (len(thingToCheck) == 6 and thingToCheck.upper().endswith(".AX")) and any(item["ASX code"].upper() == thingToCheck[:3].upper() for item in companyList):
        isValid = True
    elif any(thingToCheck.upper() in item["Company name"].upper() for item in companyList):
        isValid = True
    return isValid


# Returns the full name of a company from its ASX code, if not in our database then returns the input given
def asxCodeToName(thingToCheck):
    if(len(thingToCheck) == 6 and thingToCheck.upper().endswith(".AX")):
        thingToCheck = thingToCheck[:3]
    companyList = openCompanyList()
    if(len(thingToCheck) < 3):
        return thingToCheck
    return next((item for item in companyList if item["ASX code"].upper() == thingToCheck.upper()), {"Company name": thingToCheck.upper()})["Company name"]


# Returns the ASX code of a company from its full name, if not in our database then returns the input given
def asxNameToCode(thingToCheck):
    thingToCheck = asxRemoveTails(thingToCheck)
    companyList = openCompanyList()
    return next((item for item in companyList if item["Company name"].upper() == thingToCheck.upper()), {"ASX code": thingToCheck.upper()})["ASX code"]


# Returns the industry group of a company from its full name, if not in our database then returns the input given
def asxNameToType(thingToCheck):
    thingToCheck = asxRemoveTails(thingToCheck)
    companyList = openCompanyList()
    return next((item for item in companyList if item["Company name"].upper() == thingToCheck.upper()), {"GICS industry group": thingToCheck.upper()})["GICS industry group"]

# a "fuzzy" version of the asxNameToCode function, looks for a substring instead of an exact match
def asxNameToCodeFuzzy(thingToCheck):
    thingToCheck = asxRemoveTails(thingToCheck)
    companyList = openCompanyList()
    return next((item for item in companyList if thingToCheck.upper() in item["Company name"].upper()), {"ASX code": thingToCheck.upper()})["ASX code"]

# a "fuzzy" version of the asxNameToCode function, looks for a substring instead of an exact match
def asxNameToTypeFuzzy(thingToCheck):
    thingToCheck = asxRemoveTails(thingToCheck)
    companyList = openCompanyList()
    return next((item for item in companyList if thingToCheck.upper() in item["Company name"].upper()), {"GICS industry group": thingToCheck.upper()})["GICS industry group"]


# Each entry in the dictionary corresponds to the error code required
def errorReturn(errorCode,params):
    errorCase = {
        1 : "startDate is empty",
        2 : "endDate is empty",
        3 : "startDate is after endDate",
        4 : "A Company Name you entered is invalid",
        5 : "An Instrument ID you entered is invalid",
        6 : "The Guardian API returned no articles",
        7 : "The time period you entered is too big",
        8 : "You entered an invalid character",
        9 : "startDate is invalid format",
        10 : "endDate is invalid format"
    }

    logOutput = {'Parameters passed' : str(params),
                'Execution Result' :
                    ["Error", str(errorCase.get(errorCode, "Invalid Error Code"))]
                }

    return marshal(logOutput, log_fields)

# Given parsed params and a pageNumber, returns the json from Guardian Api
# Used for recursive calling of the api when there is more than 1 page of data
def callGuardian(my_params, curPageNum):
    parsed_url = (api_url + '?q=' + my_params['q'] + '&from-date='
    + my_params['from-date'] + '&to-date=' + my_params['to-date']
    + '&order-by=' + my_params['order-by']
    + '&show-fields=' + my_params['show-fields']
    + '&page=' + str(curPageNum)
    + '&page-size=' + str(defaultPageSize)
    + '&api-key=' + my_params['api-key'])

    response = requests.get(parsed_url)
    return response.json()

class InputProcess(Resource):
    def get(self):
        execStartTime = datetime.datetime.now()

        #arguments/parameters passed to the guardian
        #IMPORTANT some fields are hidden and to unhide them
        #add arguments t0 show-fields in my_params
        my_params = {
            'q': "",
            'from-date': "",
            'to-date': "",
            'order-by': "newest",
            'show-fields': 'body-text',
            'api-key':"6a81a5ed-2739-409d-8ada-059c122c8b43"
        }

        #extracting arguments from url
        parser = reqparse.RequestParser()
        parser.add_argument('startDate', type=str)
        parser.add_argument('endDate', type=str)
        parser.add_argument('companyId', type=str)
        parser.add_argument('topic', type=str)
        args = parser.parse_args()

        # startDate = are accepted in url call format
        # endDate = are accepted in url call format
        # companyId => q (multiple ids, separated by %20OR%20)
        # topic => q (multiple ids, separated by %20OR%20)

        #checks if dates exists before formating
        if args['startDate'] != None:
            my_params['from-date'] = re.sub(r'\.[0-9]+', '', args['startDate'] )
        else:
            return errorReturn(1,args)

        if args['endDate'] != None:
            my_params['to-date'] = re.sub(r'\.[0-9]+', '', args['endDate'] )
        else:
            return errorReturn(2,args)

        #checking if the dates are in correct format
        strptime_format = '%Y-%m-%dT%H:%M:%SZ'

        dt_str = my_params['from-date']
        try:
            dt = datetime.datetime.strptime(dt_str, strptime_format)
            print(dt)
        except ValueError:
            print('date fail')
            return errorReturn(9,args)

        dt_str = my_params['to-date']
        try:
            dt = datetime.datetime.strptime(dt_str, strptime_format)
            print(dt)
        except ValueError:
            print('date fail')
            return errorReturn(10,args)

        #checking if endDate is before startDate
        if datetime.datetime.strptime(my_params['from-date'],
        strptime_format) > datetime.datetime.strptime(my_params['to-date'], strptime_format):
            return errorReturn(3,args)

        comp = []
        if args['companyId'] != None:
            comp = re.split('_', args['companyId'])

        topics =[]
        if args['topic'] != None:
            topics = re.split('_', args['topic'])



        #compId use this to get the InstrumentIDs or companyIds
        compId = []
        compIdTemp = []
        topicTemp = []

        for c in comp:
            a = c.replace("-", " ")
            compId.append(a)

        #converting InstrumentIDs to companyId
        #also checking for valid InstrumentIDs
        i = 0;
        while i < len(compId):
            if (re.match(r'.*\.AX',compId[i])):
                print(compId[i])
                if not asxCheckValid(compId[i]):
                    return errorReturn(5, args)
                compId[i] = asxCodeToName(compId[i])

            i=i+1

        #check if company exists

        for c in compId:
            if not asxCheckValid(c):
                return errorReturn(4, args)

        for c in compId:
            a = c.replace(" ", "%20")
            compIdTemp.append(a)

        for c in topics:
            a = c.replace("-", "%20")
            topicTemp.append(a)

        #checks for the number of companys and topics and
        #forms q based on that
        if len(compIdTemp) > 0 and len(topicTemp) > 0:
            delimeter = "%20OR%20"
            my_params['q'] = delimeter.join(compIdTemp)
            my_params['q'] = '(' + my_params['q'] + ')'
            my_params['q'] = '(' + delimeter.join(topicTemp) + ')' + '%20AND%20' + my_params['q']
        elif len(compIdTemp) == 0 and len(topicTemp) > 0:
            delimeter = "%20OR%20"
            my_params['q'] = delimeter.join(topicTemp)
        elif len(topicTemp) == 0 and len(compIdTemp) > 0:
            delimeter = "%20OR%20"
            my_params['q'] = delimeter.join(compIdTemp)

        data = callGuardian(my_params, 1)

        resultsList = []
        # if there is one page
        print("Total Articles: " + str(data["response"]["total"]))
        print("Pages: " + str(data["response"]["pages"]))
        if (data["response"]["pages"] == 1):
            print("Calling page: 1")
            resultsList = data["response"]["results"]
        # if there is more than one page
        elif (data["response"]["pages"] != 1):
            for x in range(0, data["response"]["pages"]):
                print("Calling page: " + str(x+1))
                data = callGuardian(my_params, x+1)
                resultsList = resultsList + data["response"]["results"]
        else:
            print("\nYou shouldn't be here!!!!\n")

        # check if guardian returned no articles
        if not data["response"]["results"]:
            return errorReturn(6,args)

        #print statments for debugging please keep for future use
        #print(response.url) #to see the url call to the api to make sure its correct
        #print(response.text)

        # if you get to this point, there should be no errors
        return parseGuardian(resultsList, compId, args, execStartTime)

# add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: base()))

#add rule for api call, calls InputProcess
api.add_resource(InputProcess, '/newsapi/v1.0/query', endpoint = 'query')

if __name__ == '__main__':
    application.run(debug=True)
