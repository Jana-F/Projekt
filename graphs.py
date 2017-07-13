from math import floor, ceil

import plotly
from plotly.graph_objs import Scatter, Layout, Figure

from twitter import get_user, count_followers, count_tweets, count_likes


def render_graph(graph_data: dict):
    # convert dates to timestamp, to the x axis can be considered a real date
    when = [(int(x.strftime('%s')) * 1000) for x in graph_data['info_date_when']]
    trace1 = Scatter(
        x=when,
        y=graph_data['info_tweets_per_day'],
        mode='markers',
        marker={
            'size': 25,
            'color': 'rgba(191, 63, 63, .9)',
            'line': {
                'width': 3,
            }
        },
        name='tweets',
        yaxis='y2'
    )

    # druhý graf, čtverečky
    trace2 = Scatter(
        x=when,
        y=graph_data['info_likes_number'],
        mode='markers',
        marker={
            'symbol': 'square',
            'size': 15,
            'color': 'rgba(213, 143, 143, .9)',
            'line': {
                'width': 2,
            }
        },
        name='likes',
        yaxis='y2'
    )

    # treti graf, souvisla cara
    trace3 = Scatter(
        x=when,
        y=graph_data['info_followers_per_day'],
        mode='lines',
        name='followers',
    )

    data = [trace1, trace2, trace3]

    min_followers = min(graph_data['info_followers_per_day'])
    max_followers = max(graph_data['info_followers_per_day'])

    min_followers = floor(min_followers / 100) * 100  # round to bottom 100
    max_followers = ceil(max_followers / 100) * 100  # round to upper 100
    max_tweets_likes = max(graph_data['info_tweets_per_day'] + graph_data['info_likes_number'])

    yaxis2 = dict(
        title='tweets & likes',
        showline=True,
        zeroline=True,
        titlefont=dict(
            color='rgb(191, 63, 63)'
        ),
        tickfont=dict(
            color='rgb(191, 63, 63)'
        ),
        overlaying='y',
        side='right',

    )

    if max_tweets_likes < 20:  # use linear axis
        yaxis2.update(dict(
            range=[0, max(5, max_tweets_likes)],
            type='linear',
        ))
    else:  # use logarithmic axis
        yaxis2.update(dict(
            type='log',
            autorange=True,
        ))

    layout = Layout(
        xaxis=dict(
            title='dates',
            type='date',
            showline=True,
        ),
        yaxis=dict(
            title='followers',
            range=[min_followers, max_followers],
            zeroline=True,
            showline=True,
            titlefont=dict(
                color='rgb(63, 191, 63)'
            ),
            tickfont=dict(
                color='rgb(63, 191, 63)'
            )
        ),
        yaxis2=yaxis2
    )
    '''    
    # tohle by vykreslilo grafy pod sebou    
    data = tools.make_subplots(rows=1, cols=2)    
    data.append_trace(trace1, 1, 1)    
    data.append_trace(trace2, 1, 2)    
    '''
    fig = Figure(data=data, layout=layout)
    return plotly.offline.plot(
        fig,
        output_type='div',
        include_plotlyjs=False,
    )


def display_user_data(screen_name, since, til):
    user = get_user(screen_name)

    graph_data = {}
    graph_followers = count_followers(user, since, til)
    graph_data.update(graph_followers)

    graph_tweets = count_tweets(user, since, til)
    graph_data.update(graph_tweets)

    graph_likes = count_likes(user, since, til)
    graph_data.update(graph_likes)

    return render_graph(graph_data)
