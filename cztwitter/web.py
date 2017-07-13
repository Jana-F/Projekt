from datetime import datetime, timedelta

import binascii
from flask import Flask, render_template, request, redirect, url_for, session, abort, Markup
from os import urandom

from cztwitter import config
from cztwitter.graphs import display_user_data
from cztwitter.twitter import get_user, update_do_check

app = Flask(__name__)
app.secret_key = config.SECRET_KEY


@app.template_global('csrf_token')
def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = binascii.hexlify(urandom(16)).decode('utf-8')  # str() is ugly
    return session["csrf_token"]


@app.template_global('csrf_token_input')
def csrf_token_input():
    return Markup('<input type="hidden" name="csrf_token" value="%s">' % csrf_token())


def check_csrf_token():
    if "csrf_token" not in request.form:
        abort(400)

    if request.form["csrf_token"] != csrf_token():
        abort(400)


@app.before_request
def auto_check_csrf():
    if request.method == "POST" or request.form:
        check_csrf_token()


@app.route('/user/<screen_name>')
def profile(screen_name):
    user = get_user(screen_name)
    if not user.get('do_check'):
        return render_template('no_data.html', screen_name=user['nick'])

    til = datetime.today()
    since = til - timedelta(days=7)

    graph = display_user_data(user, since, til)
    return render_template('profile.html', graph=graph, screen_name=user['nick'])


@app.route('/track/<screen_name>', methods=['POST'])
def track(screen_name):
    user = get_user(screen_name)
    do_check = bool(request.form['do_check'])
    update_do_check(user, do_check)
    return redirect(url_for('profile', screen_name=user['nick']))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('profile', screen_name=request.form['screen_name']))
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=config.DEBUG)
