from flask import Flask, render_template,Blueprint
from flask_restful import Resource, Api, reqparse, fields, marshal
from datetime import datetime
import csv
import json
import requests
import re
import datetime
application = Blueprint('api_v2', __name__)
api = Api(application)
currentVersion = 'v2.0'

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

def parseGuardian(jsonData, compNameList, params, execStartTime):
    #use compNameList to make a instrIdList
    instrIdList = []
    for c in range(0, len(compNameList)):
        if len(compNameList[c]) <= 3:
            instrIdList.append(compNameList[c])
            if (asxCheckValid(compNameList[c])):
                compNameList[c] = asxCodeToName(compNameList[c])
            else:
                compNameList[c] = "Abbreviation not supported"
        else:
            instrIdList.append(asxNameToCode(compNameList[c]))

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

    # check if guardian returned no articles
    devMessage = ""
    if not jsonData:
        devMessage = ": Guardian API returned no articles"

    execEndTime = datetime.datetime.now()
    logOutput = {'Parameters passed' : str(params),
                'Execution Result' :
                    ["Successful" + devMessage, str(execStartTime),
                    str(execEndTime),  str(execEndTime-execStartTime)]
                }


    data = {'Log Output' : logOutput,
            'NewsDataSet' : newsDataList}

    # marshal orders the data alphabetically. is this a problem?!
    # return the json marshalled with the fields
    return marshal(data, output_fields)


def csvRemoveTails(companyName):
    nameEndings = [" Group Limited", " Limited", " LTD"]
    for end in nameEndings:
        if(companyName.upper().endswith(end.upper())):
            companyName = companyName[:-len(end)]
    return companyName.upper()


def openCompanyList(csvName):
    with open("static/csv/"+csvName+".csv", newline='') as csvfile:
        companyList = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        newlist = []
        for row in companyList:
            newlist.append(row)
            newlist[-1]["Company name"] = csvRemoveTails(newlist[-1]["Company name"])

    return newlist


def getExchanges(withDot):
    exchanges = ["AX", "NASDAQ", "EUX", "LSE", "NYSE", "SSX"]
    if withDot:
        exchanges = ['.'+item for item in exchanges]
    return exchanges


def removeExchangeCode(exchange):
    ends = getExchanges(True)
    for end in ends:
        if exchange.endswith(end):
            exchange = exchange[:-len(end)]
    return exchange


def openAllCompanyLists():
    companyDict = {}
    exchanges = getExchanges(False)
    for exchange in exchanges:
        companyDict[exchange] = openCompanyList(exchange)
    return companyDict


# an exact checkIfValid function
def asxCheckValid(thingToCheck):
    thingToCheck = csvRemoveTails(thingToCheck)
    companyDict = openAllCompanyLists()
    # check if it ends in an exchange code
    for end in getExchanges(True):
        if thingToCheck.endswith(end):
            return any(removeExchangeCode(thingToCheck) == item["Symbol"].upper() for item in companyDict[end[1:]])
    # check all exchanges
    if(not (" " in thingToCheck or "." in thingToCheck)):
        return any(any(removeExchangeCode(thingToCheck) == item["Symbol"].upper() for item in companyDict[end]) for end in getExchanges(False))
    # check all exchanges for name
    else:
        return any(any(thingToCheck == item["Company name"].upper() for item in companyDict[end]) for end in getExchanges(False))


# a fuzzy checkIfValid function
def asxCheckValidFuzzy(thingToCheck):
    thingToCheck = csvRemoveTails(thingToCheck)
    companyDict = openAllCompanyLists()
    # check if it ends in an exchange code
    for end in getExchanges(True):
        if thingToCheck.endswith(end):
            return any(removeExchangeCode(thingToCheck)in item["Symbol"].upper() for item in companyDict[end[1:]])
    # check all exchanges
    if(not (" " in thingToCheck or "." in thingToCheck)):
        return any(any(removeExchangeCode(thingToCheck) in item["Symbol"].upper() for item in companyDict[end]) for end in getExchanges(False))
    # check all exchanges for name
    else:
        return any(any(thingToCheck in item["Company name"].upper() for item in companyDict[end]) for end in getExchanges(False))


def fullName(thingToCheck):
    thingToCheck = csvRemoveTails(thingToCheck)
    companyDict = openAllCompanyLists()
    for end in getExchanges(False):
        for company in companyDict[end]:
            if(thingToCheck.upper() in company["Company name"].upper()):
                return company["Company name"]
    return thingToCheck


# Returns the full name of a company from its ASX code, if not in our database then returns the input given
def asxCodeToName(thingToCheck):
    companyDict = openAllCompanyLists()
    # check if it ends in an exchange code
    for end in getExchanges(True):
        if thingToCheck.endswith(end):
            for company in companyDict[end[1:]]:
                if removeExchangeCode(thingToCheck) == company["Symbol"].upper():
                    return company["Company name"]

    # check all exchanges
    if(not (" " in thingToCheck or "." in thingToCheck)):
        for end in getExchanges(False):
            for company in companyDict[end]:
                if removeExchangeCode(thingToCheck) == company["Symbol"].upper():
                    return company["Company name"]
    return thingToCheck


# Returns the ASX code of a company from its full name, if not in our database then returns the input given
def asxNameToCode(thingToCheck):
    thingToCheck = csvRemoveTails(thingToCheck)
    companyDict = openAllCompanyLists()
    for end in getExchanges(False):
        for company in companyDict[end]:
            if(company["Company name"].upper() == thingToCheck.upper()):
                return company["Symbol"]+"."+end
    return thingToCheck


# a "fuzzy" version of the asxNameToCode function, looks for a substring instead of an exact match
def asxNameToCodeFuzzy(thingToCheck):
    thingToCheck = csvRemoveTails(thingToCheck)
    companyDict = openAllCompanyLists()

    if("." in thingToCheck):
        return thingToCheck

    exactReturn = asxNameToCode(thingToCheck)
    if("." in exactReturn):
        return exactReturn

    for end in getExchanges(False):
        for company in companyDict[end]:
            if(thingToCheck.upper() in company["Company name"].upper()):
                return company["Symbol"]+"."+end
    return thingToCheck


# Each entry in the dictionary corresponds to the error code required
def errorReturn(errorCode,params):
    errorCase = {
        1 : "startDate is empty",
        2 : "endDate is empty",
        3 : "startDate must be before endDate",
        4 : "A Company Name you entered is invalid",
        5 : "An Instrument ID you entered is invalid",
        6 : "The Guardian API returned no articles", #not used atm
        7 : "The time period you entered is too big", #not used atm
        8 : "You entered an invalid character", #not used atm
        9 : "startDate is invalid format",
        10 : "endDate is invalid format",
        11 : "Please eneter date before or equal to current date"
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
            'order-by': "relevance",
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

        if datetime.datetime.strptime(my_params['from-date'],
        strptime_format) > datetime.datetime.now():
            return errorReturn(11,args)

        if datetime.datetime.strptime(my_params['to-date'],
        strptime_format) > datetime.datetime.now():
            return errorReturn(11,args)

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
            if (re.match(r'.*\.AX$',compId[i])): # JUST WANT TO ASK, SHUD THIS BE .AX$ SO THAT IT MAKES SURE THERE IS NOTHING AFTER
                print(compId[i])
                if not asxCheckValid(compId[i]):
                    return errorReturn(5, args)
                compId[i] = asxCodeToName(compId[i])

            i=i+1

        #check if company exists

        for c in compId:
            if not asxCheckValid(c):
                return errorReturn(4, args)

        for idx, val in enumerate(compId):
            compId[idx] = fullName(val)


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

        #print statments for debugging please keep for future use
        #print(response.url) #to see the url call to the api to make sure its correct
        #print(response.text)

        # if you get to this point, there should be no errors
        return parseGuardian(resultsList, compId, args, execStartTime)

# add a rule for the index page.
#application.add_url_rule('/', 'index', (lambda: base()))
#THIS SHOULD 404

class notQuery(Resource):
    def get(self,endpointString):
        # Set the response code to 404
        return {'404 Error': endpointString+' isn\'t a valid endpoint'}, 404

#add rule for api call, calls InputProcess
api.add_resource(InputProcess, '/query', endpoint = 'query')
api.add_resource(notQuery, '/<string:endpointString>')
if __name__ == '__main__':
    application.run(debug=True)
