from math import floor, ceil

import plotly
from plotly.graph_objs import Scatter, Layout, Figure


def render_graph(graph_data: dict):
    # prvni graf, tecky
    trace1 = Scatter(
        x=graph_data['info_date_when'],
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
        x=graph_data['info_date_when'],
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
        x=graph_data['info_date_when'],
        y=graph_data['info_followers_per_day'],
        mode='lines',
        name='followers',
    )

    data = [trace1, trace2, trace3]

    min_followers = min(graph_data['info_followers_per_day'])
    max_followers = max(graph_data['info_followers_per_day'])
    min_followers = floor(min_followers / 100) * 100  # round to bottom 100
    max_followers = ceil(max_followers / 100) * 100  # round to upper 100
    layout = Layout(
        title='Twitter Statistics for {}'.format(graph_data['user']['screen_name']),
        xaxis=dict(
            title='dates',
            zeroline=True,
            showline=True
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
        yaxis2=dict(
            title='tweets & likes',
            range=[0, 10],
            zeroline=True,
            showline=True,
            titlefont=dict(
                color='rgb(191, 63, 63)'
            ),
            tickfont=dict(
                color='rgb(191, 63, 63)'
            ),
            overlaying='y',
            side='right'
        )
    )
    '''    
    # tohle by vykreslilo grafy pod sebou    
    data = tools.make_subplots(rows=1, cols=2)    
    data.append_trace(trace1, 1, 1)    
    data.append_trace(trace2, 1, 2)    
    '''
    fig = Figure(data=data, layout=layout)
    plotly.offline.plot(
        fig
    )
