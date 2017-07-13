from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for

from cztwitter import config
from cztwitter.graphs import display_user_data
from cztwitter.twitter import get_user, update_do_check

app = Flask(__name__)


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
