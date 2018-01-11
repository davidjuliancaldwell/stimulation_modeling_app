import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly as plotly
import plotly.graph_objs as go
import os

app = dash.Dash(__name__)
server = app.server

colors = {
    'text': '#7FDBFF'
}

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

# bring in the data
data_test_100 = np.flipud(np.load('test_E_100.npy'))
data_test_10 = np.flipud(np.load('test_E_10.npy'))
data_test_50 = np.flipud(np.load('test_E_50.npy'))

dataFrame = {'csf_1_mm':data_test_10,'csf_5_mm':data_test_50,'csf_10_mm':data_test_100}

app.layout = html.Div([
    html.Div([
    html.H2('Visualization of Theoretical Dipole Stimulation'),
    html.Hr(),

    dcc.Dropdown(
                id='type_stim',
                options=[{'label': i, 'value': i} for i in dataFrame.keys()],
                value='csf_10_mm'
                ),
    html.Div(children='Dropdown menu to select CSF thickness of interest', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    html.Hr(),

    dcc.Graph(id='heatmap_efield'),

    html.Hr(),
    html.Div(children='Slider to control range of the plot', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    dcc.RangeSlider(
        id='max_val',
        min=0,
        max=1100,
        value=[0,500],
        step=10,
        marks={i: '{}'.format(i) for i in range(0,1101,50)},
    ),


    ])
    ],

    style = {'display': 'inline-block', 'width': '48%'})


@app.callback(
    dash.dependencies.Output('heatmap_efield', 'figure'),
    [dash.dependencies.Input('type_stim','value'),
    dash.dependencies.Input('max_val', 'value')])
def update_figure(data_input,selected_range):
    maximum_val = int(selected_range[1])
    minimum_val = int(selected_range[0])
    data_input_select = dataFrame[data_input]
    return {
        'data': [
            #go.Contour([data])
            go.Heatmap(
                z=data_input_select,
             colorscale='Reds',
             zauto = 'false',
             zmin=minimum_val,
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
