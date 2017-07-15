from datetime import datetime, timedelta, date

import logging

from cztwitter import config
from cztwitter.connections import session, conn, cur

log = logging.getLogger(__name__)


def add_new_user(user: dict, do_check: bool = False) -> dict:
    """
    Verify, if the user is in the database. If not, then it will do so.
    """

    cur.execute('''SELECT * FROM twitter_user WHERE id = %s;''', (user['id'],))
    row = cur.fetchone()
    if not row:
        cur.execute('''INSERT INTO twitter_user(id, screen_name, do_check) VALUES (%s, %s, %s);''',
                    (user['id'], user['screen_name'], do_check))
        conn.commit()
        row = {
            'id': user['id'],
            'screen_name': user['screen_name'],
            'do_check': do_check,
        }
    return row


def add_followers(who: int, whom: int, followed_at: datetime):
    """
    Insert information about followers to the table 'follows' - id, id of the followed person and date.
    Each row must be unique. If the record already exists, it raises an exception and will not insert it again.
    """
    try:
        cur.execute('''INSERT INTO follows(who, whom, followed_at) VALUES (%s, %s, %s);''', (who, whom, followed_at))
        conn.commit()
    except:
        conn.rollback()


def download_user_details(screen_name: str) -> dict:
    """
    Connect to api.twitter.com and returns info about the user whose screen_name we typed as the parameter.
    """
    res = session.get('https://api.twitter.com/1.1/users/show.json',
                      params={'screen_name': screen_name})
    return res.json()


def get_user(screen_name: str = None, user_id: int = None) -> dict:
    """
    Check if the user is in the database. If not, she inserts him to the 'twitter_user' table.
    The do_check column has the value True for the followed person.
    """
    if screen_name:
        cur.execute('''SELECT * FROM twitter_user where screen_name = %s''', (screen_name,))
    elif user_id:
        cur.execute('''SELECT * FROM twitter_user where id = %s''', (user_id,))
    else:
        raise ValueError("missing user lookup identifier")

    user = cur.fetchone()
    if not user:
        user = download_user_details(screen_name)
        user = add_new_user(user)

    return user


def insert_followers_sum(user: dict):
    """
    Insert a brief info about number of followers at given day.
    """
    try:
        cur.execute("""INSERT INTO followers_sum 
        (who, checked_at, followers) VALUES (%s, %s, %s) 
        """, (user['id'], date.today(), user['followers_count']))
        conn.commit()
    except:
        conn.rollback()


def get_followers_sum(user: dict, when: date = None):
    """
    Get a record about followers at given day
    """
    if not when:
        when = date.today()
    cur.execute("""SELECT * FROM followers_sum WHERE who = %s and checked_at = %s""", (user['id'], when))
    return cur.fetchone()


def download_followers(user: dict):
    """
    Download info about followers. If there's not too much of them (`config.DETAILS_LIMIT`),
    download each of them separately, so detailed diffs can be shown.
    Otherwise, store just an info about the number of followers and call it a day.
    """
    checked_today = get_followers_sum(user)
    if checked_today:
        return  # already checked today, no need to do anything else

    user_details = download_user_details(user['screen_name'])
    if user_details['followers_count'] < config.DETAILS_LIMIT:
        log.info('downloading details')
        now = datetime.now()
        next_cursor = -1
        while next_cursor != 0:
            r = session.get(
                'https://api.twitter.com/1.1/followers/list.json',
                params={
                    'screen_name': user['screen_name'],
                    'cursor': next_cursor,
                    'count': 200,
                }
            )
            if not r.ok:
                return

            followers = r.json()['users']
            for follower in followers:
                add_followers(follower['id'], user['id'], now)

            next_cursor = r.json()['next_cursor']

    # if we downloaded everything successfuly, store a brief info about it
    insert_followers_sum(user_details)


def get_followers_count(user: dict, from_date: date, to_date: date) -> dict:
    """
    Count all followers for the particular user and for each day within the specified period.
    It returns a dictionary that contains a list of dates and a list of number of followers for each day.
    """
    followers_per_day = []
    date_when = []
    while from_date <= to_date:
        followers = get_followers_sum(user, from_date)
        if not followers:
            followers_per_day.append(0)
        else:
            followers_per_day.append(followers['followers'])

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
    Insert information about tweets to the table 'tweets' - tweet_id, user_id, date,
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
    Updates number of likes and number of retweets in tweets table.
    """
    cur.execute('''UPDATE tweets SET(no_likes, no_retweets) = (%s, %s) WHERE tweet_id = (%s);''',
                (tweet['favorite_count'], tweet['retweet_count'], tweet['id']))
    conn.commit()


def download_tweets(user: dict, hours=72):
    """
    Download a list of dictionaries from api.twitter.com. It contains information about
    tweets and twitter user. Using the add_tweet_info function, the information is inserted to the database.
    It inserts only original tweets (no retweets).
    """
    date_until = datetime.today()
    date_since = date_until - timedelta(hours=hours)
    cur.execute('''SELECT tweet_id 
    FROM tweets 
    WHERE tweet_date <= %s AND tweet_date >= %s 
    AND user_id = %s''', (date_until, date_since, user['id']))
    existing_tweets = cur.fetchall() or []
    existing_tweets = {x['tweet_id'] for x in existing_tweets}
    max_id = None
    keep_loading = True
    while keep_loading:
        r = session.get(
            'https://api.twitter.com/1.1/statuses/user_timeline.json',
            params={
                'screen_name': user['screen_name'],
                'count': 20,
                'include_rts': False,
                'max_id': max_id,
            })
        if not r.ok:
            break

        tweets = r.json()
        for tweet in tweets:
            created_at = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            if created_at < date_since:
                keep_loading = False
                break  # if we get too old tweet, quit

            if tweet['id'] not in existing_tweets:
                add_tweet_info(tweet)
            else:
                update_tweet_info(tweet)

            max_id = max_id and min(max_id, tweet['id']) or tweet['id']


def count_tweets(user: dict, from_date: date, to_date: date):
    """
    Count all tweets for the particular user and for each day within the specified period.
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


def count_likes(user: dict, from_date: date, to_date: date):
    """
    Count the number of likes relating to the tweets written on a particular day within the
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
        'info_likes_number': likes_number,
    }
    return likes_info


def update_do_check(user: dict, status: bool):
    """
    Change the value in the do_check column.
    """
    cur.execute('''UPDATE twitter_user SET do_check = %s WHERE id = %s''', (status, user['id']))
    conn.commit()
