import psycopg2
from datetime import datetime, timedelta
from twitter_wall import twitter_session
import configparser


# from pprint import pprint


def init_connections():
    """
    The program connects to the database. If not successful, raises the exception.
    Then reads the API Key from the auth.cfg file and API Secret and opens the connection to twitter API.
    """
    config = configparser.ConfigParser()
    config.read('./auth.cfg')

    try:
        conn = psycopg2.connect(
            dbname=config['db']['name'],
            user=config['db']['user'],
            host=config['db']['host'],
            password=config['db']['password'],
            port=config['db']['port'],
        )
        cur = conn.cursor()
    except Exception as e:
        print(e)
        raise Exception('I am unable to connect to the database')

    api_key = config['twitter']['key']
    api_secret = config['twitter']['secret']

    session = twitter_session(api_key, api_secret)
    return session, conn, cur


session, conn, cur = init_connections()


def add_new_user(user_id: int, screen_name: str, do_check: bool = False):
    """
    This function verifies, if the user is in the database. If not, this function inserts his id, nick and
    do_check to the table 'twitter_user'.
    """

    cur.execute('''SELECT id FROM twitter_user WHERE id = %s;''', (user_id,))
    row = cur.fetchone()
    if not row:
        cur.execute('''INSERT INTO twitter_user(id, nick, do_check) VALUES (%s, %s, %s);''',
                    (user_id, screen_name, do_check))
        conn.commit()


def add_followers(who: int, whom: int, followed_at: datetime):
    """
    The function inserts information about followers to the table 'follows' - id, id of the followed person and date.
    Each row must be unique. If the record already exists, it raises an exception and will not insert it again.
    """
    try:
        cur.execute('''INSERT INTO follows(who, whom, followed_at) VALUES (%s, %s, %s);''', (who, whom, followed_at))
        conn.commit()
    except:
        conn.rollback()


def get_user_details(screen_name: str):
    """
    The function connects to api.twitter.com and returns info about the user whose nick we typed as the parameter.
    """
    r = session.get('https://api.twitter.com/1.1/users/show.json',
                    params={'screen_name': screen_name}
                    )
    return r.json()


def get_user(screen_name: str = None, user_id: int = None) -> dict:
    """
    This function checks if the user is in the database. If not, she inserts him to the 'twitter_user' table.
    The do_check column has the value True for the followed person.
    """
    user = cur.execute('''SELECT * FROM twitter_user where nick = %s''', (screen_name,))
    if not user:
        user = get_user_details(screen_name)
        add_new_user(user['id'], screen_name, True)
    else:
        user = {
            'id': user['id'],
            'screen_name': user['nick'],
        }
    return user


def download_followers(user: dict):
    """
    This function downloads a dictionary from api.twitter.com. It contains a list of followers for the particular user
    listed in the function parameter and the 'cursor' information to allow paging. Each page has up to 200 entries.
    Using the 'add_new_user' and 'add_followers' functions, the information from all pages is inserted to the database.
    Do_check value is False for followers.
    """
    now = datetime.now()
    next_cursor = -1
    print(user)
    while next_cursor != 0:
        r = session.get('https://api.twitter.com/1.1/followers/list.json',
                        params={'screen_name': user['screen_name'], 'cursor': next_cursor, 'count': 200}
                        )

        followers = r.json()['users']
        for follower in followers:
            add_new_user(follower['id'], follower['screen_name'])
            add_followers(follower['id'], user['id'], now)

        next_cursor = r.json()['next_cursor']
        # print('Number of records:', len(followers), 'next_cursor:', next_cursor)


def count_followers(user: dict, from_date: datetime, to_date: datetime) -> dict:
    """
    The function counts all followers for the particular user and for each day within the specified period.
    It returns a dictionary that contains a list of dates and a list of number of followers for each day.
    """
    followers_per_day = []
    date_when = []
    while from_date <= to_date:
        cur.execute('''SELECT followed_at, COUNT(*) FROM follows
            WHERE followed_at = %s and whom = %s
            GROUP BY followed_at ORDER BY followed_at;''', (from_date, user['id']))
        followers = cur.fetchone()
        if not followers:
            followers_per_day.append(0)
        else:
            followers_per_day.append(followers[1])
        date_when.append(from_date)
        from_date = from_date + timedelta(days=1)

    followers_info = {
        'info_date_when': date_when,
        'info_followers_per_day': followers_per_day,
        'info_user': user,
    }
    return followers_info


def add_tweet_info(tweet: dict):
    """
    This function inserts information about tweets to the table 'tweets' - tweet_id, user_id, date,
    number of likes and number of retweets.
    """
    try:
        cur.execute('''INSERT INTO tweets(tweet_id, user_id, tweet_date, no_likes, no_retweets) 
            VALUES (%s, %s, %s, %s, %s);''', (
            tweet['id'], tweet['user']['id'], tweet['created_at'], tweet['favorite_count'], tweet['retweet_count']
        ))
        conn.commit()
    except:
        conn.rollback()


def update_tweet_info(tweet: dict):
    """
    This function updates number of likes and number of retweets in tweets table.
    """
    cur.execute('''UPDATE tweets SET(no_likes, no_retweets) = (%s, %s) WHERE tweet_id = (%s);''',
                (tweet['favorite_count'], tweet['retweet_count'], tweet['id']))
    conn.commit()


def download_tweets(user: dict):
    """
    This function downloads a list of dictionaries from api.twitter.com. It contains information about
    tweets and twitter user. Using the add_tweet_info function, the information is inserted to the database.
    It inserts only original tweets (no retweets).
    """
    r = session.get('https://api.twitter.com/1.1/statuses/user_timeline.json',
                    params={'screen_name': user['screen_name'], 'count': 200, 'include_rts': False})
    tweets = r.json()
    for tweet in tweets:
        cur.execute('''SELECT tweet_id FROM tweets WHERE tweet_id = %s;''', (tweet['id'],))
        row = cur.fetchone()
        if not row:
            add_tweet_info(tweet)
        else:
            update_tweet_info(tweet)


def count_tweets(user: dict, from_date: datetime, to_date: datetime):
    """
    This function counts all tweets for the particular user and for each day within the specified period.
    If the date is not in the database (it means there are no tweets this date) it adds 0 to the list 'tweets_per_day'.
    """
    date_tweet = []
    tweets_per_day = []
    while from_date <= to_date:
        cur.execute('''SELECT tweet_date, COUNT(*) FROM tweets
            WHERE tweet_date = %s and user_id = %s GROUP BY tweet_date''', (from_date, user['id']))
        number_of_tweets = cur.fetchone()
        if not number_of_tweets:
            date_tweet.append(from_date)
            tweets_per_day.append(0)
        else:
            date_tweet.append(number_of_tweets[0])
            tweets_per_day.append(number_of_tweets[1])
        from_date = from_date + timedelta(days=1)

    tweets_info = {
        'info_date_when': date_tweet,
        'info_tweets_per_day': tweets_per_day,
    }
    return tweets_info


def count_likes(user: dict, from_date: datetime, to_date: datetime):
    """
    This function counts the number of likes relating to the tweets written on a particular day within the
    specified period. If the date is not in the database it adds 0 to the list 'likes_number'.
    number_of_likes - tweet day & number of likes
    """
    date_likes = []
    likes_number = []
    while from_date <= to_date:
        cur.execute('''SELECT tweet_date, SUM(no_likes) FROM tweets
        WHERE tweet_date = %s and user_id = %s GROUP BY tweet_date''', (from_date, user['id']))
        number_of_likes = cur.fetchone()
        if not number_of_likes:
            date_likes.append(from_date)
            likes_number.append(0)
        else:
            date_likes.append(number_of_likes[0])
            likes_number.append(number_of_likes[1])
        from_date = from_date + timedelta(days=1)

    likes_info = {
        'info_date_when': date_likes,
        'info_likes_number': likes_number
    }
    return likes_info
