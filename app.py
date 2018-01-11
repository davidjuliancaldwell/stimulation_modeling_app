import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly as plotly
import plotly.graph_objs as go
import os
import pandas as pd

app = dash.Dash(__name__)
server = app.server

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

# bring in the data
data_test_100 = np.flipud(np.load('test_E_100.npy'))
data_test_10 = np.flipud(np.load('test_E_10.npy'))

dataFrame = {'data_10':data_test_10,'data_100':data_test_100}

app.layout = html.Div([
    html.Div([
    html.H2('Visualization of Theoretical Dipole Stimulation'),
    html.Hr(),

    dcc.Dropdown(
                id='type_stim',
                options=[{'label': i, 'value': i} for i in dataFrame.keys()],
                value='data_100'
                ),
    html.Hr(),

    dcc.Graph(id='heatmap_efield'),

    html.Hr(),

    dcc.Slider(
        id='max_val',
        min=0,
        max=1000,
        value=500,
        step=None,
        marks={i: '{}'.format(i) for i in range(0,1000,100)},
    ),
    ])
    ],

    style = {'display': 'inline-block', 'width': '48%'})


@app.callback(
    dash.dependencies.Output('heatmap_efield', 'figure'),
    [dash.dependencies.Input('type_stim','value'),
    dash.dependencies.Input('max_val', 'value')])
def update_figure(data_input,selected_max):
    maximum_val = int(selected_max)
    data_input_select = dataFrame[data_input]
    return {
        'data': [
            #go.Contour([data])
            go.Heatmap(
                z=data_input_select,
             colorscale='jet',
             zauto = 'false',
             zmin=0,
             zmax=maximum_val)
        ],
        'layout': go.Layout(
        xaxis={'title':'x dimension'},
        yaxis={'title': 'depth'},
        title='Plots of simulated field effects',
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)
