from datetime import datetime, timedelta

from flask import Flask, render_template

from cztwitter import config
from cztwitter.graphs import display_user_data

app = Flask(__name__)
app.debug = config.DEBUG


@app.route('/user/<username>')
def profile(username):
    til = datetime.today()
    since = til - timedelta(days=7)

    graph = display_user_data(username, since, til)
    return render_template('profile.html', graph=graph, screen_name=username)


if __name__ == '__main__':
    app.run()
