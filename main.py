import flask
from flask import jsonify, Flask, request
from email.utils import parseaddr
import hashlib
import json
import sys
from src.application.stock.Stock import Stock
sys.path.insert(1, '/src/website/python')
from src.website.python import User, datastoreHelper

CLIENT_ID = '978820308825-dkff9fbqjg4vvpr22ohfkidi2n28bj1c.apps.googleusercontent.com'
CLIENT_SECRET = 'l415lpbQTPiMwInvyUrNWyU2'


app = Flask(__name__, template_folder="src/website/templates" )
# flask needs this don't ask any questions, shh it's a secret
app.secret_key = b'oaijrwoizsdfmnvoiajw34foinmzsdv98j234'
import bs4 as bs
import requests

def get_s_and_p_tickers():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text.rstrip()
        tickers.append(ticker)
    return tickers

tickers = get_s_and_p_tickers()
@app.route('/')
def index():
    if get_user():
        return flask.redirect('/dashboard')
    else:
        return show_page('login.html', 'Login')

# dashboard route
@app.route('/dashboard')
def dashboard():
    if get_user():
        return show_page('portfolio.html', 'Dashboard')
    else:
        return flask.redirect('/')


# route for create account page
@app.route('/CreateAccount')
def createAcct():
    return show_page('CreateAccount.html', 'Create Account')

# route for create account page
@app.route('/add_position', methods=[ 'POST', 'GET' ])
def add_positions():
    search = flask.request.args.get('search')
    return flask.render_template('AddPosition.html', stock=search, title='Add Position')


# 'register' method that performs registration of user
@app.route('/register', methods=['POST'])
def register():
    # from the signup form - get username, pass1/2, email
    username = flask.request.form.get('username')
    email = flask.request.form.get('email')
    password1 = flask.request.form.get('password')
    password2 = flask.request.form.get('password_confirm')

    # errors compiles error strings that occur, and then show page can place them into
    # any template {errors} field to display on the page - if we want to do it this way
    errors = []
    #test push
    # if passes don't match - this is an error
    if password1 != password2:
        errors.append('Passwords do not match.')

    # if email is entered invalid - this is an error
    email_parts = parseaddr(email)
    if len(email_parts) != 2 or not email_parts[1]:
        errors.append('Invalid email address: ' + str(email))

    # use the entered info to create a user object
    user = User.User(username, email)

    # if there were any errors in the form - we will return them to the signup
    if errors:
        return show_page('/CreateAccount.html', 'Create Account', errors=errors)
    else: # else if there are no erorrs, hash password, and write the user to the db
        passwordhash = hash_password(password1)
        # store User and hashed pasword into the datastore
        datastoreHelper.save_user(user, passwordhash)
        # set the session user
        flask.session['user'] = user.username
        # now the user is logged in, we redirect them to the dashboard/portfolio page
        return flask.redirect('/dashboard')


# route for create account page
@app.route('/login')
def login():
    return show_page('login.html', 'Login')

# route for create account page
@app.route('/get_tickers')
def get_tickers():
    print(tickers) 
    return json.dumps(tickers)

# route for create account page
@app.route('/get_stock_data/<ticker>')
def get_stock_data(ticker):
    stock = Stock(ticker)
    return json.dumps(stock.getAllInfo())

@app.route('/user_login', methods=['POST'])
def user_login():
    # from the sign in form, get email and password
    email = flask.request.form.get('email')
    password = flask.request.form.get('password')

    # hash the password
    passwordhash = hash_password(password)

    # try to get a user object from the datastore with this username and hashpass
    user = datastoreHelper.load_user(email, passwordhash)

    if user:  # if we get a real user, this user is logged in, set the session user
        flask.session['user'] = user.username
        return flask.redirect('/dashboard')
    else:  # if login failed, return them to login
        errors = ['Failed to log in']
        return flask.redirect('/login')


# signs out the user, setting their session to None and redirecting to the home page
@app.route('/signout')
def signout():
    flask.session['user'] = None
    return flask.redirect('/')


# when a user signs in, the username is in the session[user], so we can get it at any time
def get_user():
    return flask.session.get('user', None)


# adapted from week6p9, show page is a wrapper for render_template, it allows us to easily specify what we pass to the template
def show_page(page, title, show=True, errors=None):
    # always need a page, page title, and user to pass into template
    # errors is an array of error strings, to be displayed in the errors field in the event of errors *note: errors*
    return flask.render_template(page, page_title=title, user=get_user(), show=show, errors=errors)


# Hashes the password using sha256 from hashlib
def hash_password(pw):
    encoded = pw.encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
