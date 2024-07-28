# Import packages
from dash import Dash, html, dcc,callback,Input, ctx, Output,dependencies, callback_context
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
    html.H1(children='Mathayom 6 students graduate in 2023.'),
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
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x= filtered_df['schools_province'],
        y= filtered_df['totalmale'],
        name='Total Male',
        marker_color='blue'
    ))
    fig.add_trace(go.Bar(
        x= filtered_df['schools_province'],
        y= filtered_df['totalfemale'],
        name='Total Female',
        marker_color='red'
    ))
    fig.add_trace(go.Bar(
        x= filtered_df['schools_province'],
        y= filtered_df['totalstd'],
        name='Total Student',
        marker_color='yellowgreen'
    ))
    fig.update_layout(
    title="Comparison Chart",
    xaxis_title="Schools Province",
    yaxis_title="Number of Students",
    legend_title="Gender",
    xaxis_tickangle= 70,
    font=dict(
        size=16,
        )
    )
    return fig

# call back update map
@app.callback(
    Output('map-graph', 'figure'),
    [Input('clicked-provinces', 'data')]
)
def update_map(clicked_provinces):
    if not clicked_provinces:
        lat, lon, zoom = df['lat'].mean(), df['lon'].mean(), 5
    else:
        last_clicked_province  = clicked_provinces[-1]
        lat = df[df['schools_province'] == last_clicked_province]['lat'].values[0]
        lon = df[df['schools_province'] == last_clicked_province]['lon'].values[0]
        zoom = 15

    fig = px.scatter_mapbox(df, lat='lat', lon='lon',
                            hover_name='schools_province', hover_data=['totalmale', 'totalfemale'],
                            zoom=zoom, height=500)
    fig.update_layout(mapbox=dict(center=dict(lat=lat, lon=lon)))
    
    fig.update_traces(marker=dict(size=10, color='rgba(0, 0, 255, 0.5)', opacity=0.7), selector=dict(mode='markers'))
    for province in clicked_provinces:
        fig.add_trace(go.Scattermapbox(
            lat=[df[df['schools_province'] == province]['lat'].values[0]],
            lon=[df[df['schools_province'] == province]['lon'].values[0]],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=20,
                color='red',
                opacity=0.9
            ),
            name=province
        ))
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
    fig.update_layout(
        font=dict(
            size=16,
            )
        )
    fig.update_layout(title_text=title)


    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
