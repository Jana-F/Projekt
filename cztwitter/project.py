from datetime import datetime

from cztwitter.graphs import render_graph
from cztwitter.twitter import download_followers, get_followers_count, download_tweets, get_user, count_tweets, count_likes

if __name__ == '__main__':
    user = get_user('yedpodtrzitko')
    since = datetime(2017, 6, 30)
    til = datetime(2017, 7, 6)
    # download_followers(user)
    # download_tweets(user)

    graph_data = {}
    graph_followers = get_followers_count(user, since, til)
    graph_data.update(graph_followers)
    
    graph_tweets = count_tweets(user, since, til)
    graph_data.update(graph_tweets)

    graph_likes = count_likes(user, since, til)
    graph_data.update(graph_likes)

    render_graph(graph_data, False)
