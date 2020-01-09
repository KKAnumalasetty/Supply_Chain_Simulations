# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 20:28:59 2020

@author: karth
"""

import dash
from dash_core_components import Dropdown,Graph
from dash_html_components import H3,Div
from dash.dependencies import Input, Output
from datetime import datetime as dt
from plotly import graph_objs as go

print('dash version - ',dash.__version__)
import pandas as pd
print('pandas version - ',pd.__version__)
import numpy as np
print('numpy version - ',np.__version__)

from pandas_datareader import data as web


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# UI layout - DASH app

app.layout = Div([
        
        H3('Dash App'),
        
        Dropdown(
                id='my-dropdown',
                options =[
                        {'label':'Coke','value':'COKE'},
                        {'label':'Apple','value':'AAPL'},
                        {'label':'Tesla','value':'TSLA'},
                        {'label':'Amazon','value':'AMZN'}
                        ],
                value='COKE'
                ),
        
        Graph(id='my-graph')
        ])
        
#Server logic of DASH app

@app.callback(
    Output('my-graph',component_property='figure'),
    [Input('my-dropdown',component_property='value')])
def update_graph(dropdown_properties):
    selected_value = dropdown_properties
    df = web.DataReader(selected_value,'yahoo',dt(2016,1,1),dt.now())
    import plotly.express as px
    fig = px.scatter(df, x=df.index, y=df["Close"])
    print(df)
    return fig

if __name__ == "__main__":
    app.run_server(debug=False)
