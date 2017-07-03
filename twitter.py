import psycopg2
from datetime import datetime
from twitter_wall import twitter_session
import configparser
from pprint import pprint


# The program connects to the database. If not successful, raises the exception.
# Then reads the API Key from the auth.cfg file and API Secret and opens the connection to twitter API.
try:
    conn = psycopg2.connect(dbname='cztwitter', user='jana', host='vanyli.net', password='!l3grac3ful', port=5433)
    cur = conn.cursor()
except:
    print('I am unable to connect to the database')

config = configparser.ConfigParser()
config.read('./auth.cfg')
api_key = config['twitter']['key']
api_secret = config['twitter']['secret']

session = twitter_session(api_key, api_secret)


def add_new_user(twitter_id, screen_name, do_check):
    """
    This function verifies, if the user is in the database. If not, this function inserts his id and nick to the table 'twitter_user'.
    It also inserts the information if the check is necessary.
    """
    cur.execute('''SELECT id FROM twitter_user WHERE id = %s;''', (twitter_id,))        # 2nd parameter for execute() must be tuple
    row = cur.fetchall()
    if row == []:
        cur.execute('''INSERT INTO twitter_user(id, nick, do_check) VALUES (%s, %s, %s);''', (twitter_id, screen_name, do_check))
        conn.commit()


def add_followers(who, whom, followed_at):
    """
    The function inserts information about followers to the table 'follows' - id, id of the followed person and date.
    Each row must be unique. If the record already exists, it raises an exception and will not insert it again.
    """
    try:
        cur.execute('''INSERT INTO follows(who, whom, followed_at) VALUES (%s, %s, %s);''', (who, whom, followed_at))
        conn.commit()
    except:
        conn.rollback()


def get_user_details(screen_name):
    """
    The function connects to api.twitter.com and returns the id of the user whose nick we typed as the parameter.
    """
    r = session.get('https://api.twitter.com/1.1/users/show.json',
                    params={'screen_name': screen_name}
                    )
    id = r.json()['id']
    return id


def download_followers(name):
    """
    This function downloads a dictionary from api.twitter.com. It contains a list of followers for the particular user
    listed in the function parameter and the 'cursor' information to allow paging. Each page has up to 200 entries.
    Using the 'add_new_user' and 'add_followers' functions, the information from all pages is inserted to the database.
    Do_check value is True for the followed users and Falls for followers.
    """
    next_cursor = -1
    while next_cursor != 0:
        r = session.get('https://api.twitter.com/1.1/followers/list.json',
                        params={'screen_name': name, 'cursor': next_cursor, 'count': 200},
                        )

        followers = r.json()['users']
        followed_id = get_user_details(name)
        add_new_user(followed_id, name, True)
        now = datetime.now()
        for follower in followers:
            add_new_user(follower['id'], follower['screen_name'], False)
            add_followers(follower['id'], followed_id, now)

        next_cursor = r.json()['next_cursor']
        print('Number of records:', len(followers), 'next_cursor:', next_cursor)


def count_followers(screen_name, from_date, to_date):
    """
    The function counts all followers for the particular user and for each day within the specified period.
    """
    first_day = datetime.strptime(from_date, '%Y-%m-%d')
    last_day = datetime.strptime(to_date, '%Y-%m-%d')
    followed_id = get_user_details(screen_name)
    cur.execute('''SELECT followed_at, COUNT(*) FROM follows 
        WHERE followed_at BETWEEN %s AND %s and whom = %s
        GROUP BY followed_at;''', (first_day, last_day, followed_id))
    number_of_followers = cur.fetchall()
    return number_of_followers


if __name__ == '__main__':
    download_followers('yedpodtrzitko')
    count_followers('yedpodtrzitko', '2017-06-30', '2017-07-02')
