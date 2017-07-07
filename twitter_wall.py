# chcp 65001
# twitter wall- jde nastavit, jestli má zobrazovat retweety

import requests
import base64
import click
import configparser
import time

def twitter_session(api_key, api_secret):
    session = requests.Session()
    secret = '{}:{}'.format(api_key, api_secret)
    secret64 = base64.b64encode(secret.encode('ascii')).decode('ascii')

    headers = {
        'Authorization': 'Basic {}'.format(secret64),
        'Host': 'api.twitter.com',
    }

    r = session.post('https://api.twitter.com/oauth2/token',
                        headers=headers,
                        data={'grant_type': 'client_credentials'})

    bearer_token = r.json()['access_token']

    def bearer_auth(req):
        req.headers['Authorization'] = 'Bearer ' + bearer_token
        return req

    session.auth = bearer_auth
    return session


@click.command()
@click.option('--conffile', default='./auth.cfg', help='Path for the auth config file')
@click.option('--word', default='#python', help='Word we want to find.')
@click.option('--number', default=5, help='Number of tweets.')
@click.option('--retweets', default='no', help='Displaying retweets - yes or no.')
@click.option('--time_interval', default=10, help ='Time interval between queries')

def tweets(conffile, word, number, retweets, time_interval):
    config = configparser.ConfigParser()
    config.read(conffile)
    api_key = config['twitter']['key']
    api_secret = config['twitter']['secret']

    session = twitter_session(api_key, api_secret)

    r = session.get('https://api.twitter.com/1.1/search/tweets.json',
        params={'q': word, 'count': 150},
    )

    sinceID = 0
    count_tweets = 0

    if retweets == 'no':
        for tweet in r.json()['statuses']:
            if not 'retweeted_status' in tweet:
                sinceID = printing_tweets(tweet, sinceID)
                count_tweets += 1
                if count_tweets == number:
                    break

    if retweets == 'yes':
        for tweet in r.json()['statuses']:
            sinceID = printing_tweets(tweet, sinceID)
            count_tweets += 1
            if count_tweets == number:
                break

    while True:
        r = session.get('https://api.twitter.com/1.1/search/tweets.json',
            params={'q': word, 'count': 5, 'since_id': sinceID},
            )

        time.sleep(time_interval)
        print()
        print('New searching...')
        time.sleep(1)
        print()

        if retweets == 'no':
            for tweet in r.json()['statuses']:
                if not 'retweeted_status' in tweet:
                    sinceID = printing_tweets(tweet, sinceID)

        if retweets == 'yes':
            for tweet in r.json()['statuses']:
                sinceID = printing_tweets(tweet, sinceID)


def printing_tweets(tw, since):
    print(tw['text'])
    print(50*'-')
    tweetID = tw['id']
    if since < tweetID:
        since = tweetID
    return since

if __name__ == '__main__':
    tweets()
