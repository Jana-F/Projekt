import psycopg2
from datetime import datetime
from twitter_wall import twitter_session
import configparser
from pprint import pprint

# práce s databází
try:
    conn = psycopg2.connect(dbname='cztwitter', user='jana', host='vanyli.net', password='!l3grac3ful', port=5433)
except:
    print("I am unable to connect to the database")
cur = conn.cursor()

def add_new_user(twitter_id, nick):
    cur.execute("""SELECT id FROM twitter_user WHERE id = %s;""", (twitter_id,))
    row = cur.fetchall()
    if row == []:
        cur.execute("""INSERT INTO twitter_user(id, nick) VALUES (%s, %s);""", (twitter_id, nick))
        conn.commit()

def add_followers(who, whom, followed_at):
    cur.execute("""INSERT INTO follows(who, whom, followed_at) VALUES (%s, %s, %s);""", (who, whom, followed_at))
    conn.commit()

# stažení seznamu followerů pro konkrétního uživatele
def download_followers(name):
    config = configparser.ConfigParser()
    config.read('./auth.cfg')
    api_key = config['twitter']['key']
    api_secret = config['twitter']['secret']

    session = twitter_session(api_key, api_secret)

    next_cursor = 'maybe'
    while next_cursor != 0:
        r = session.get('https://api.twitter.com/1.1/followers/list.json',
                        params={'screen_name': name, 'cursor': next_cursor, 'count': 200},
                        )

        followers = r.json()["users"]
        for follower in followers:
            add_new_user(follower["id"], follower["screen_name"])

        next_cursor = r.json()["next_cursor"]
        print(next_cursor)

download_followers('yedpodtrzitko')
#add_new_user(321, "Pavel")
now = datetime.now()
#add_followers(123, 678, now)
