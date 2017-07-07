from math import floor, ceil

import plotly
from plotly.graph_objs import Scatter, Layout, Figure


def render_graph(graph_data: dict):
    # prvni graf, tecky
    trace1 = Scatter(
        x=graph_data['info_date_when'],
        y=[1, 2, 0, 2, 3, 0],
        mode='markers',
        marker={
            'size': 25,
            'color': 'rgba(255, 182, 193, .9)',
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
        y=[4, 3, 1, 2, 1, 2],
        mode='markers',
        marker={
            'symbol': 'square',
            'size': 15,
            'color': 'rgba(120, 255, 193, .9)',
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
            showline=True,
            titlefont=dict(
                color='rgb(148, 103, 189)'
            ),
            tickfont=dict(
                color='rgb(148, 103, 189)'
            )
        ),
        yaxis=dict(
            title='followers',
            range=[min_followers, max_followers],
            zeroline=True,
            showline=True,
            titlefont=dict(
                color='rgb(148, 103, 189)'
            ),
            tickfont=dict(
                color='rgb(148, 103, 189)'
            )
        ),
        yaxis2=dict(
            title='tweets, likes',
            range=[0, 5],
            zeroline=True,
            showline=True,
            titlefont=dict(
                color='rgb(148, 103, 189)'
            ),
            tickfont=dict(
                color='rgb(148, 103, 189)'
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
