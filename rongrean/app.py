# Import packages
from dash import Dash, html, dash_table, dcc,callback,Input, ctx, Output,dependencies, callback_context
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from province import province_coords

# Incorporate data
df = pd.read_json('https://gpa.obec.go.th/reportdata/pp3-4_2566_province.json')
 
# add lat lon to loded data frame
df['lat'] = df['schools_province'].map(lambda x: province_coords[x]['lat'] if x in province_coords else None)
df['lon'] = df['schools_province'].map(lambda x: province_coords[x]['lon'] if x in province_coords else None)
province_options = [{'label': province, 'value': province} for province in df['schools_province'].unique()]
# Initialize the app
app = Dash()

# Define the layout of the app
app.layout = html.Div(children=[
    html.H1(children='Student Distribution by Province'),
    html.Div(style={'display': 'flex', 'flex-direction': 'row'},children=[
        html.Div(style={'width': '50%'}, children=[
        dcc.Graph(id='map-graph')
        ]),
        html.Div(style={'width': '50%'}, children=[
        dcc.Graph(id='province-pi')
        ]), 
    ]),
    html.Div(style={'display': 'flex', 'flex-direction': 'row', "padding": "10px",'align-items': 'center', 'gap': '10px'},children=[
        html.Div(style={'width': '50%'}, children=[
            dcc.Dropdown(
            id='province-input',
            options=province_options,
            placeholder='Select a province'
            ),
        ]),
        html.Div(style={'width': '50%', 'display': 'flex', 'gap': '10px'}, children=[
            html.Button(id='submit-button', n_clicks=0, children='Search'),
            html.Button(id='reset-button', n_clicks=0, children='Reset'),
        ]), 
    ]),
        

    dcc.Graph(id='province-graph',),
    dcc.Store(id='clicked-provinces', data=[])
])

#call back update data click
@app.callback(
    Output('clicked-provinces', 'data'),
    [Input('submit-button', 'n_clicks'),
     Input('reset-button', 'n_clicks'),
     Input('map-graph', 'clickData')],
    [dependencies.State('province-input', 'value'),
     dependencies.State('clicked-provinces', 'data')]
)
def update_clicked_provinces(n_clicks, resetbtn, clickData, province, clicked_provinces):
    ctx = callback_context
    if "reset-button" == ctx.triggered_id:
        return []
    
    if "submit-button" == ctx.triggered_id and province:
        if province not in clicked_provinces:
            clicked_provinces.append(province)
    elif "map-graph" == ctx.triggered_id and clickData:
        province = clickData['points'][0]['hovertext']
        if province not in clicked_provinces:
            clicked_provinces.append(province)
    
    return clicked_provinces

# Define the callback to update the graph
@app.callback(
    Output('province-graph', 'figure'),
    [Input('clicked-provinces', 'data')],
)
def update_graph(clicked_provinces):
    if not clicked_provinces:
        filtered_df = df
    else:
        filtered_df = df[df['schools_province'].isin(clicked_provinces)]
    fig = px.bar(filtered_df, x='schools_province', y=['totalmale', 'totalfemale', 'totalstd'],
                 labels={'value': 'Number of Students', 'variable': 'Gender'},
                 barmode='group')
    return fig

# call back update map
@app.callback(
    Output('map-graph', 'figure'),
    [Input('map-graph', 'clickData')]
)
def update_map(clickData):
    fig = px.scatter_mapbox(df, lat='lat', lon='lon', size='totalstd',
                            hover_name='schools_province', hover_data=['totalmale', 'totalfemale'],
                            zoom=5, height=500)
    
    fig.update_traces(marker=dict(size=10, color='rgba(0, 0, 255, 0.5)', opacity=0.7), selector=dict(mode='markers'))
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    return fig

@app.callback(
    Output('province-pi', 'figure'),
    [Input('clicked-provinces', 'data')]
)
def update_pie_chart(clicked_provinces):
    if not clicked_provinces:
        filtered_df = df[df['schools_province'] == "นราธิวาส"]
        title = "นราธิวาส"
    else:
        province = clicked_provinces[len(clicked_provinces)-1]
        filtered_df = df[df['schools_province'] == province]
        title = f"{province}"

    values = filtered_df[['totalmale', 'totalfemale']].values.flatten()
    labels = ['Total Male', 'Total Female']
    colors = ['blue', 'red']
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])
    fig.update_layout(title_text=title)


    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
