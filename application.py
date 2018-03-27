from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse, fields, marshal
from datetime import datetime
application = Flask(__name__)
api = Api(application)
currentVersion = 'v1.0'

@application.route('/')
@application.route('/homepage.html')
##@app.route('/News/<name>')
def base():
    return render_template('homepage.html')

@application.route('/changes.html')
##@app.route('/News/<name>')
def changesPage():
    return render_template('changes.html')
    
@application.route('/features.html')
##@app.route('/News/<name>')
def featuresPage():
    return render_template('features.html')

@application.route('/test.html')
##@app.route('/News/<name>')
def testPage():
    return render_template('test.html')

#def parseGuardian(jsonData,logFile):
def parseGuardian():
    # parse guardian json


    newsData_fields = {}
    newsData_fields['InstrumentIDs'] = fields.List(fields.String)
    newsData_fields['CompanyNames'] = fields.List(fields.String)
    newsData_fields['TimeStamp'] = fields.String
    newsData_fields['Headline'] = fields.String
    newsData_fields['NewsText'] = fields.String

    output_fields = {}
    output_fields['NewsDataSet'] = fields.List(fields.Nested(newsData_fields))

    #will need to loop through guardian json data

    #

    newsData1 = {'InstrumentIDs': ['CBA', 'DMP'],
        'CompanyNames': ['COUGAR METALS NL', 'DOMINO\'S PIZZA ENTERPRISES LIMITED'],
        'TimeStamp': datetime.now(),
        'Headline': 'pizza is good for you',
        'NewsText': 'lol get clickbaited'
    }

    newsData2 = {'InstrumentIDs': ['CBA', 'TLS'],
        'CompanyNames': ['COMMONWEALTH BANK OF AUSTRALIA', 'TELSTRA CORPORATION LIMITED'],
        'TimeStamp': datetime.now(),
        'Headline': 'OMG NEWZ',
        'NewsText': 'give us ur money thx'
    }
    data = {'NewsDataSet' : [newsData1, newsData2]}

    #!marshal orders the data alphabetically. will need a way to change this!
    return marshal(data, output_fields)

class InputProcess(Resource):
    def get(self):

        # TODO: create a log file

        parser = reqparse.RequestParser()
        parser.add_argument('startDate', type=str)
        parser.add_argument('endDate', type=str)
        parser.add_argument('companyId', type=str)
        parser.add_argument('topic', type=str)
        args = parser.parse_args()

        #parsing to guardian Api
        # we will need a function that turns company names's to company ids and
        # vice versa. we should also have a separate function called in this
        # function that gets the "type" of company they are to parse into
        # the tags field for guardian api. eg. technology/apple.
        # see ASX..csv file

        # startDate => from-date [YYYY-MM-DD]
        # endDate => to-date [YYYY-MM-DD]
        # companyId => q (multiple ids, separated by %20AND%20)
        # topic => q (multiple ids, separated by %20AND%20)
        #
        #
        # https://content.guardianapis.com/search?q="information%20technology"%20AND%20apple
        # &from-date=2014-01-01
        # &to-date=2018-01-01
        # &api-key=6a81a5ed-2739-409d-8ada-059c122c8b43


        # once the data is correct, call guardian api
        #
        # then we can return the data from parseGuardian
        # return parseGuardian(jsonData,logFile)

        return parseGuardian()

# add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: base()))

#add rule for api call, calls InputProcess
api.add_resource(InputProcess, '/newsapi/v1.0/query', endpoint = 'query')

if __name__ == '__main__':
    application.run(debug=True)
