from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse
application = Flask(__name__)
api = Api(application)

@application.route('/')
##@app.route('/News/<name>')
def base():
    return render_template('base.html')

class InputProcess(Resource):
    def get(self):

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
        # the tags field for guardian api. eg. technology/apple

        # startDate => from-date [YYYY-MM-DD]
        # endDate => to-date [YYYY-MM-DD]
        # companyId => tag
        # topic => q
        #
        # https://content.guardianapis.com/search?q="information%20technology"
        # &tag=technology/apple
        # &from-date=2014-01-01
        # &to-date=2018-01-01
        # &api-key=6a81a5ed-2739-409d-8ada-059c122c8b43
        #the json file here should work.
        return parser.parse_args()

# add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: base()))

#add rule for api call, calls InputProcess
api.add_resource(InputProcess, '/newsapi/v1.0/query', endpoint = 'query')

if __name__ == '__main__':
    application.run(debug=True)
