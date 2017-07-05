import plotly
from plotly.graph_objs import Scatter, Layout, Figure


def render_graph(followers_data):
    dates = []
    for record in followers_data:
        dates.append(record[0])


    # prvni graf, tecky
    trace1 = Scatter(
        x=dates,
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

    # prvni graf, tecky
    trace2 = Scatter(
        x=dates,
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
        x=dates,
        y=[50, 100, 80, 110, 150, 90],
        mode='lines',
        name='followers',
    )

    data = [trace1, trace2, trace3]

    layout = Layout(
        title='Double Y Axis Example',
        xaxis=dict(
            zeroline=True,
            showline=True,
         ),
        yaxis=dict(
            title='followers',
            range=[0, 160],
            zeroline=True,
            showline = True
        ),
        yaxis2=dict(
            title='tweets, likes',
            range=[0, 4],
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

#followers_week =[(datetime.date(2017, 7, 1), 372), (datetime.date(2017, 7, 3), 372), (datetime.date(2017, 7, 5), 372), (datetime.date(2017, 6, 30), 372), (datetime.date(2017, 7, 4), 372), (datetime.date(2017, 7, 2), 372)]ender_graph(followers_data)