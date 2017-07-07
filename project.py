from graphs import render_graph
from twitter import download_followers, count_followers, download_tweets

if __name__ == '__main__':
    # download_followers('yedpodtrzitko')
    followers_date_and_sum = count_followers('yedpodtrzitko', '2017-06-30', '2017-07-06')
    download_tweets('yedpodtrzitko')
    render_graph(followers_date_and_sum)
