import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly as plotly
import plotly.graph_objs as go
import os
#import theoretical_funcs_numba_sub
import json
from rq import Queue
from worker import conn
import time
from numba import jit

app = dash.Dash(__name__)
server = app.server
q = Queue('high',connection=conn)

colors = {
    'text': '#7FDBFF'
}

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

#############
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
    #k_min = [0,900]
    #k_max = [900,1001]
    k_min = [0]
    k_max = [1001]
    Ex = np.zeros((1001,1001))
    Ez = np.zeros((1001,1001))
    Ex_minus =np.zeros((1001,1001))
    Ez_minus = np.zeros((1001,1001))
    list_ks = list(zip(k_min,k_max))

    #for i in range(len(k_min)):
    #    still_compute = True
    still_compute = True
    computed_data = q.enqueue(point_electrode_dipoles_sub,Ex,Ez,value,list_ks[0][0],list_ks[0][1])
    #computed_data = point_electrode_dipoles_sub(Ex,Ez,value,list_ks[0][0],list_ks[0][1])

    while still_compute is True:
        if computed_data.result is not None:
            Ex[:,list_ks[0][0]:list_ks[0][1]] = computed_data.result[0]
            Ez[:,list_ks[0][0]:list_ks[0][1]] = computed_data.result[1]
    #Ex[:,list_ks[0][0]:list_ks[0][1]] = computed_data[0]
    #Ez[:,list_ks[0][0]:list_ks[0][1]] = computed_data[1]


            still_compute = False

                    #Ex[:,list_ks[1][0]:list_ks[1][1]] = computed_data_2[0]
                    #Ez[:,list_ks[1][0]:list_ks[1][1]] = computed_data_2[1]
    for j in np.arange(0,1001):
        Ex_minus[:,1000-j]=Ex[:,j]
        Ez_minus[:,1000-j]=-Ez[:,j]

    E_field=np.sqrt((Ex+Ex_minus)**2+(Ez+Ez_minus)**2)

    #finished = q.enqueue(finish_calc,Ex,Ex_minus,Ez,Ez_minus)
    E = np.flipud(E_field)
    #E = np.flipud(computed_data.result)
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

@jit(error_model='numpy')
def point_electrode_dipoles_sub(Ex,Ez,csf_thick,k_min,k_max):
    h=0.001
    i0=1e-3
    rho1=0.5
    rho2=2.5
    K21=(rho2-rho1)/(rho2+rho1)
    scale=(i0*rho1)/(2*np.pi)
    x_offset=0
    z_offset=0

    cx1 = np.zeros((50,1))
    cx2 = np.zeros((50,1))
    cz1 = np.zeros((50,1))
    cz2 = np.zeros((50,1))

    cxb1 = np.zeros((50,1))
    czb1 = np.zeros((50,1))
    cxb2 = np.zeros((50,1))
    czb2 = np.zeros((50,1))

    for k in range(k_min,k_max):
        x= np.float32(x_offset+(k)*0.00001)
        for j in range(0,csf_thick):

            z=z_offset+(j)*0.00001
            Eox=x*scale/(x**2+z**2)**1.5
            Eoz=z*scale/(x**2+z**2)**1.5
            #
            # n = np.arange(0,50)
            # m = n-1
            # cx1 = (x*K21**(n+1)/((2*(n+1)*h-z)**2+x**2)**1.5)
            # cx2 =(x*K21**(n+1)/((2*(n+1)*h+z)**2+x**2)**1.5)
            # cz1 = (-(2*(n+1)*h-z)*K21**(n+1)/((2*(n+1)*h-z)**2+x**2)**1.5)
            # cz2 = ((2*(n+1)*h+z)*K21**(n+1)/((2*(n+1)*h+z)**2+x**2)**1.5)


            for n in range(0,50):
                m=n-1
                cx1[n,0]=(x*K21**(n+1)/((2*(n+1)*h-z)**2+x**2)**1.5)
                cx2[n,0]=(x*K21**(n+1)/((2*(n+1)*h+z)**2+x**2)**1.5)
                cz1[n,0]=(-(2*(n+1)*h-z)*K21**(n+1)/((2*(n+1)*h-z)**2+x**2)**1.5)
                cz2[n,0]=((2*(n+1)*h+z)*K21**(n+1)/((2*(n+1)*h+z)**2+x**2)**1.5)


            Cxo1=scale*np.sum(cx1)
            Cxo2=scale*np.sum(cx2)
            Czo1=scale*np.sum(cz1)
            Czo2=scale*np.sum(cz2)

            Ex[j,k]=Eox+Cxo1+Cxo2
            Ez[j,k]=Eoz+Czo1+Czo2

    for k in range(k_min,k_max):
        x=np.float32(x_offset+(k)*0.00001)
        for j in range(csf_thick,1001):
            z=z_offset+(j)*0.00001

            Eox=x*scale/(x**2+z**2)**1.5
            Eoz=z*scale/(x**2+z**2)**1.5
            #
            # n = np.arange(0,50)
            # m = n -0
            # cxb1 = (x*K21**(n+1)/((2*m*h+z)**2+x**2)**-1.5)
            # cxb2 = (x*K21**(n+1)/((2*(n+1)*h+z)**2+x**2)**-1.5)
            # czb1 = ((2*m*h+z)*K21**(n+1)/((2*m*h+z)**2+x**2)**1.5)
            # czb2 = ((2*(n+1)*h+z)*K21**(n+1)/((2*(n+1)*h+z)**2+x**2)**1.5)

            for n in range(0,50):
                m=n-0
                cxb1[n]=(x*K21**(n+1)/((2*m*h+z)**2+x**2)**-1.5)
                cxb2[n]=(x*K21**(n+1)/((2*(n+1)*h+z)**2+x**2)**-1.5)
                czb1[n]=((2*m*h+z)*K21**(n+1)/((2*m*h+z)**2+x**2)**1.5)
                czb2[n]=((2*(n+1)*h+z)*K21**(n+1)/((2*(n+1)*h+z)**2+x**2)**1.5)

            #
            Cxob1=scale*np.sum(cxb1)
            Cxob2=scale*np.sum(cxb2)
            Czob1=scale*np.sum(czb1)
            Czob2=scale*np.sum(czb2)

            Ex[j,k]=Eox+Cxob1+Cxob2
            Ez[j,k]=Eoz+Czob1+Czob2

    Ex_return = Ex[:,k_min:k_max]
    Ez_return = Ez[:,k_min:k_max]
    return Ex_return, Ez_return

if __name__ == '__main__':
    app.run_server(debug=True)
