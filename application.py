from flask import Flask, render_template
application = Flask(__name__)

@application.route('/')
##@app.route('/News/<name>')
def base():
    return render_template('base.html')

# add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: base()))

if __name__ == '__main__':
    application.run(debug=True)
