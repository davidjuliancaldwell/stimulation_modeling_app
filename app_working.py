import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly as plotly
import plotly.graph_objs as go
import os
from theoretical_funcs_numba_sub import point_electrode_dipoles
import json
from rq import Queue
from worker import conn
import time

app = dash.Dash(__name__)
server = app.server

q = Queue('high',connection=conn)


colors = {
    'text': '#7FDBFF'
}

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

# bring in the data

# data_test_100 = np.flipud(np.load('test_E_100.npy'))
# data_test_10 = np.flipud(np.load('test_E_10.npy'))
# data_test_20 = np.flipud(np.load('test_E_20.npy'))
# data_test_50 = np.flipud(np.load('test_E_50.npy'))
#
# dataFrame = {'csf_1_mm':data_test_10,'csf_2_mm':data_test_20,'csf_5_mm':data_test_50,'csf_10_mm':data_test_100}

app.layout = html.Div([
    #html.Div([
    html.H2('Visualization of Theoretical Dipole Stimulation'),
    html.Hr(),
    html.Div([
        html.Div([
        # dcc.Dropdown(
        #             id='type_stim',
        #             options=[{'label': i, 'value': i} for i in dataFrame.keys()],
        #             value='csf_10_mm'
        #             ),
        # html.Div(children='Dropdown menu to select CSF thickness of interest', style={
        #     'textAlign': 'center',
        #     'color': colors['text']
        # }),
         html.Div([
            html.Div(dcc.Input(id='load-data-box', type='number',value=100)),
            html.Button('Submit', id='button',n_clicks=0),
            html.Div(id='output-container-button',
                     children='Enter a value and press submit')
        ]),
        ],style={'width': '49%', 'display': 'inline-block'}),

        html.Div([
        html.Div([
        dcc.Input(
            id='x_cord',
            placeholder='Enter an X cord value...',
            type='number',
            value=500
        ),
        ]),
            html.Div(children='Enter value to select x coord', style={
                'textAlign': 'center',
                'color': colors['text'],
            }),
        html.Div([
        dcc.Input(
            id='z_cord',
            placeholder='Enter a z cord value...',
            type='number',
            value=500
        ),
        ]),
        html.Div(children='Enter value to select z coord', style={
            'textAlign': 'center',
            'color': colors['text']
        }),
        ],style={'width': '49%', 'display': 'inline-block', 'float':'right'}),
    ]),

    html.Hr(),
    html.Div([
    dcc.Graph(id='heatmap_efield') ], style={'width': '49%', 'display': 'inline-block', 'padding': '20 20 20 20'}),

    html.Div([
        dcc.Graph(id='x-graph'),
        dcc.Graph(id='z-graph'),
    ], style={'display': 'inline-block', 'width': '49%','padding': '20 20 20 20'}),

    html.Hr(),
    html.Div(children='Slider to control range of the plot', style={
        'textAlign': 'center',
        'color': colors['text'],
        'width': '49%',
    }),
    html.Div(dcc.RangeSlider(
        id='max_val',
        min=0,
        max=1100,
        value=[0,500],
        step=10,
        marks={i: '{}'.format(i) for i in range(0,1101,50)},),
        style={'width': '49%', 'padding': '0px 20px 20px 20px'}
    ),
        # hidden signal value
    html.Div(id='computed_data', style={'display': 'none'})
    ])
    #],
    #style = {'display': 'inline-block', 'width': '48%'})
######################

@app.callback(
   dash.dependencies.Output('computed_data', 'children'),
   [dash.dependencies.Input('button','n_clicks')],
   [dash.dependencies.State('load-data-box', 'value')])
def clean_data(n_clicks,value):

    computed_data = q.enqueue(point_electrode_dipoles,value)

    time.sleep(26)
    E = np.flipud(computed_data.result)

    E_list = E.tolist()
    return json.dumps(E_list) # or, more generally, json.dumps(cleaned_df)
@app.callback(
    dash.dependencies.Output('heatmap_efield', 'figure'),
    [dash.dependencies.Input('computed_data', 'children'),
    dash.dependencies.Input('max_val', 'value')])
def update_figure_compute(data_input,selected_range):
    maximum_val = int(selected_range[1])
    minimum_val = int(selected_range[0])
    data_input_select = np.asarray(json.loads(data_input))
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
        margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
        height=450,
        )
    }

@app.callback(
    dash.dependencies.Output('x-graph', 'figure'),
    [dash.dependencies.Input('computed_data', 'children'),
    dash.dependencies.Input('x_cord','value')])
def update_x_compute(data_input,x_cord_val):
    data_input_select = np.asarray(json.loads(data_input))
    data_x = data_input_select[:,x_cord_val]
    indep_axis_x = len(data_x)
    return {
        'data': [
            #go.Contour([data])
            go.Scatter(
                x=indep_axis_x,
                y=data_x)
        ],
        'layout': go.Layout(
        xaxis={'title':'z dimension'},
        yaxis={'title': 'Magnitude of electric field'},
        title='E-field slice in x dimension',
        height= 225,
        margin= {'l': 40, 'b': 40, 'r': 40, 't': 40},
        )
    }

@app.callback(
    dash.dependencies.Output('z-graph', 'figure'),
    [dash.dependencies.Input('computed_data', 'children'),
    dash.dependencies.Input('z_cord','value')])
def update_z_compute(data_input,z_cord_val):
        data_input_select = np.asarray(json.loads(data_input))
        data_z= data_input_select[z_cord_val,:]
        indep_axis_z = len(data_z)
        return {
        'data': [
            #go.Contour([data])
            go.Scatter(
                x = indep_axis_z,
                y= data_z)
        ],
        'layout': go.Layout(
        xaxis={'title':'x dimension'},
        yaxis={'title': 'Magnitude of field'},
        title='E-field slice in z dimension',
        height = 225,
        margin = {'l': 40, 'b': 40, 'r': 40, 't': 40},
        )
    }


#######################


# @app.callback(
#     dash.dependencies.Output('heatmap_efield', 'figure'),
#     [dash.dependencies.Input('type_stim','value'),
#     dash.dependencies.Input('max_val', 'value')])
# def update_figure(data_input,selected_range):
#     maximum_val = int(selected_range[1])
#     minimum_val = int(selected_range[0])
#     data_input_select = dataFrame[data_input]
#     return {
#         'data': [
#             #go.Contour([data])
#             go.Heatmap(
#                 z=data_input_select,
#              colorscale='Reds',
#              zauto = 'false',
#              zmin=minimum_val,
#              zmax=maximum_val)
#         ],
#         'layout': go.Layout(
#         xaxis={'title':'x dimension'},
#         yaxis={'title': 'depth'},
#         title='Plots of simulated field effects',
#         margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
#         height=450,
#         )
#     }
#
# @app.callback(
#     dash.dependencies.Output('x-graph', 'figure'),
#     [dash.dependencies.Input('type_stim','value'),
#     dash.dependencies.Input('x_cord','value')])
# def update_x(data_input,x_cord_val):
#     data_input_select = dataFrame[data_input]
#     data_x = data_input_select[:,x_cord_val]
#     indep_axis_x = len(data_x)
#     return {
#         'data': [
#             #go.Contour([data])
#             go.Scatter(
#                 x=indep_axis_x,
#                 y=data_x)
#         ],
#         'layout': go.Layout(
#         xaxis={'title':'z dimension'},
#         yaxis={'title': 'Magnitude of electric field'},
#         title='E-field slice in x dimension',
#         height= 225,
#         margin= {'l': 40, 'b': 40, 'r': 40, 't': 40},
#         )
#     }
#
# @app.callback(
#     dash.dependencies.Output('z-graph', 'figure'),
#     [dash.dependencies.Input('type_stim','value'),
#     dash.dependencies.Input('z_cord','value')])
# def update_z(data_input,z_cord_val):
#         data_input_select = dataFrame[data_input]
#         data_z= data_input_select[z_cord_val,:]
#         indep_axis_z = len(data_z)
#         return {
#         'data': [
#             #go.Contour([data])
#             go.Scatter(
#                 x = indep_axis_z,
#                 y= data_z)
#         ],
#         'layout': go.Layout(
#         xaxis={'title':'x dimension'},
#         yaxis={'title': 'Magnitude of field'},
#         title='E-field slice in z dimension',
#         height = 225,
#         margin = {'l': 40, 'b': 40, 'r': 40, 't': 40},
#         )
#     }

if __name__ == '__main__':
    app.run_server(debug=True)
