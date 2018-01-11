import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly as plotly
import plotly.graph_objs as go
import os

app = dash.Dash(__name__)
server = app.server

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

# bring in the data
data_test = np.flipud(np.load('test_E.npy'))

app.layout = html.Div([
    html.H2('Plots of Simulated Efield'),
    dcc.Graph(id='contour_efield'),
        dcc.Slider(
            id='max_val',
            min=0,
            max=1000,
            value=500,
            step=None,
            marks={i: '{}'.format(i) for i in range(0,1000,100)},
        ),
])

@app.callback(
    dash.dependencies.Output('contour_efield', 'figure'),
    [dash.dependencies.Input('max_val', 'value')])
def update_figure(selected_max):
    maximum_val = int(selected_max)
    return {
        'data': [
            #go.Contour([data])
            go.Heatmap(
                z=data_test,
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
