import psycopg2

from cztwitter.twitter_wall import twitter_session
from cztwitter.config import TWITTER, DATABASE


def init_connections():
    """
    The program connects to the database. If not successful, raises the exception.
    Then reads the API Key from the auth.cfg file and API Secret and opens the connection to twitter API.
    """
    try:
        conn = psycopg2.connect(
            dbname=DATABASE['name'],
            user=DATABASE['user'],
            host=DATABASE['host'],
            password=DATABASE['password'],
            port=DATABASE['port'],
        )
        cur = conn.cursor()
    except Exception as e:
        raise Exception('I am unable to connect to the database')

    api_key = TWITTER['key']
    api_secret = TWITTER['secret']

    session = twitter_session(api_key, api_secret)
    return session, conn, cur


session, conn, cur = init_connections()
