from flask import Flask, render_template
application = Flask(__name__)

@app.route('/')
##@app.route('/News/<name>')
def base():
    return render_template('base.html')

if __name__ == '__main__':
    application.run(debug=True)
