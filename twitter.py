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


def add_new_user(user_id, screen_name, do_check):
    """
    This function verifies, if the user is in the database. If not, this function inserts his id and nick to the table 'twitter_user'.
    It also inserts the information if the check is necessary.
    """
    cur.execute('''SELECT id FROM twitter_user WHERE id = %s;''', (user_id,))        # 2nd parameter for execute() must be tuple
    row = cur.fetchall()
    if row == []:
        cur.execute('''INSERT INTO twitter_user(id, nick, do_check) VALUES (%s, %s, %s);''', (user_id, screen_name, do_check))
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


def download_followers(screen_name):
    """
    This function downloads a dictionary from api.twitter.com. It contains a list of followers for the particular user
    listed in the function parameter and the 'cursor' information to allow paging. Each page has up to 200 entries.
    Using the 'add_new_user' and 'add_followers' functions, the information from all pages is inserted to the database.
    Do_check value is True for the followed users and Falls for followers.
    """
    next_cursor = -1
    while next_cursor != 0:
        r = session.get('https://api.twitter.com/1.1/followers/list.json',
                        params={'screen_name': screen_name, 'cursor': next_cursor, 'count': 200}
                        )

        followers = r.json()['users']
        followed_id = get_user_details(screen_name)
        add_new_user(followed_id, screen_name, True)
        now = datetime.now()
        for follower in followers:
            add_new_user(follower['id'], follower['screen_name'], False)
            add_followers(follower['id'], followed_id, now)

        next_cursor = r.json()['next_cursor']
        print('Number of records:', len(followers), 'next_cursor:', next_cursor)


def count_followers(screen_name, from_date, to_date):
    """
    The function counts all followers for the particular user and for each day within the specified period.
    It returns a dictionary that contains a list of dates and a list of numbers of followers for each day.
    """
    first_day = datetime.strptime(from_date, '%Y-%m-%d')
    last_day = datetime.strptime(to_date, '%Y-%m-%d')
    followed_id = get_user_details(screen_name)
    cur.execute('''SELECT followed_at, COUNT(*) FROM follows 
        WHERE followed_at BETWEEN %s AND %s and whom = %s
        GROUP BY followed_at ORDER BY followed_at;''', (first_day, last_day, followed_id))
    number_of_followers = cur.fetchall()
    date_when = []
    followers_per_day = []
    for record in number_of_followers:
        date_when.append(record[0])
        followers_per_day.append(record[1])
    followers_info = {
        'info_date_when': date_when,
        'info_followers_per_day': followers_per_day
    }
    return followers_info


def add_tweets_info(tweet_id, user_id, tweet_date, no_likes, no_retweets):
    """
    This function inserts information about tweets to the table 'tweets' - tweet_id, user_id, date,
    number of likes and number of retweets.
    """
    cur.execute('''INSERT INTO tweets(tweet_id, user_id, tweet_date, no_likes, no_retweets) 
        VALUES (%s, %s, %s, %s, %s);''', (tweet_id, user_id, tweet_date, no_likes, no_retweets))
    conn.commit()


def update_tweets_info(no_likes, no_retweets, tweet_id):
    """
    This function updates number of likes and number of retweets in tweets table.
    """
    cur.execute('''UPDATE tweets SET(no_likes, no_retweets) = (%s, %s) WHERE tweet_id = (%s);''',
                (no_likes, no_retweets, tweet_id))
    conn.commit()


def download_tweets(screen_name):
    """
    This function downloads a list of dictionaries from api.twitter.com. It contains information about
    tweets and twitter user. Using the add_tweet_info function, the information is inserted to the database.
    It inserts only original tweets (no retweets).
    """
    r = session.get('https://api.twitter.com/1.1/statuses/user_timeline.json',
                    params={'screen_name': screen_name, 'count': 200, 'include_rts': False}
                    )
    tweets = r.json()
    for tweet in tweets:
        cur.execute('''SELECT tweet_id FROM tweets WHERE tweet_id = %s;''', (tweet['id'],))
        row = cur.fetchone()
        if row is None:
            add_tweets_info(tweet['id'], tweet['user']['id'], tweet['created_at'], tweet['favorite_count'],
                            tweet['retweet_count'])
            conn.commit()
        else:
            update_tweets_info(tweet['favorite_count'], tweet['retweet_count'], tweet['id'])
            conn.commit()
