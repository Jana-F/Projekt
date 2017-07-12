from flask import Flask


@app.route('/user/<username>')
def profile(username):
    pass