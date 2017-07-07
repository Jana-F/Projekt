from datetime import datetime

from graphs import render_graph
from twitter import download_followers, count_followers, download_tweets, get_user

if __name__ == '__main__':
    user = get_user('yedpodtrzitko')
    since = datetime(2017, 6, 30)
    til = datetime(2017, 7, 6)
    #download_followers(user)
    graph_data = count_followers(user, since, til)
    graph_data['user'] = user
    download_tweets(user)
    render_graph(graph_data)
