from flask import Flask, render_template
application = Flask(__name__)

@application.route('/')
##@app.route('/News/<name>')
def base():
    return render_template('base.html')

# add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: base()))

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
