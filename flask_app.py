from datetime import datetime
from flask import Flask
from flask import render_template, request, flash, redirect
from pony.flask import Pony
from pony.orm import flush
from flask_login import LoginManager
from flask_login import current_user, logout_user, login_user, login_required
from models import db

app = Flask(__name__)
app.config.update(dict(
    DEBUG = False,
    SECRET_KEY = 'secret_key_for_session_or_cookies_or_security_reasons',
    PONY = {
        'provider': 'sqlite',
        'filename': 'db.db3',
        'create_db': True
    }
))

Pony(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.User.get(id=user_id)

db.bind(**app.config['PONY'])
db.generate_mapping(create_tables=True)

@app.route('/')
def index():
    users = db.User.select()
    return render_template('home.html', user=current_user, users=users)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        possible_user = db.User.get(login=username)
        if not possible_user:
            flash('Wrong username')
            return redirect('/login')
        if possible_user.password == password:
            possible_user.last_login = datetime.now()
            login_user(possible_user)
            return redirect('/')

        flash('Wrong password')
        return redirect('/login')
    else:
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        exist = db.User.get(login=username)
        if exist:
            flash('Username %s is already taken, choose another one' % username)
            return redirect('/register')

        user = db.User(login=username, password=password)
        user.last_login = datetime.now()
        flush()
        login_user(user)
        flash('Successfully registered')
        return redirect('/')
    else:
        return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out')
    return redirect('/')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
