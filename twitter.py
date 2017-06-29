import psycopg2
from datetime import datetime

try:
    conn = psycopg2.connect(dbname='cztwitter', user='jana', host='vanyli.net', password='!l3grac3ful', port=5433)
except:
    print("I am unable to connect to the database")
cur = conn.cursor()

def add_new_user(twitter_id, nick):
    cur.execute("""SELECT id FROM twitter_user WHERE id = %s;""", (twitter_id,))
    row = cur.fetchall()
#    print(row)
    if row == []:
        cur.execute("""INSERT INTO twitter_user(id, nick) VALUES (%s, %s);""", (twitter_id, nick))
        conn.commit()

def add_followers(who, whom, followed_at):

    cur.execute("""INSERT INTO follows(who, whom, followed_at) VALUES (%s, %s, %s);""", (who, whom, followed_at))
    conn.commit()

#add_new_user(321, "Pavel")
now = datetime.now()
add_followers(123, 678, now)
