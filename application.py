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
        #arguements are unprocessed and are as is
        #in the url I wasn't sure
        #how exactly we wanted to pass it into the guardian api

        #print statements for debugging
        #print("hello")
        #print(args['startDate'])

        #for now its returning the inputs
        #@Jez after passing into guardian api just return
        #the json file here should work.
        return parser.parse_args()

# add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: base()))

#add rule for api call, calls InputProcess
api.add_resource(InputProcess, '/newsapi/v1.0/query', endpoint = 'query')

if __name__ == '__main__':
    application.run(debug=True)
