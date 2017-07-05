from graphs import render_graph
from twitter import download_followers, count_followers

if __name__ == '__main__':
    #download_followers('yedpodtrzitko')
    followers_week = count_followers('yedpodtrzitko', '2017-06-30', '2017-07-05')
    render_graph(followers_week)