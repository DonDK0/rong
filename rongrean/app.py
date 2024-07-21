# Import packages
from dash import Dash, html, dash_table, dcc,callback,Input, Output,dependencies
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Incorporate data
df = pd.read_json('https://gpa.obec.go.th/reportdata/pp3-4_2566_province.json')

# Initialize the app
app = Dash()

# Define the layout of the app
app.layout = html.Div(children=[
    html.H1(children='Student Distribution by Province'),
    dcc.Input(id='province-input', type='text', placeholder='Enter province name'),
    html.Button(id='submit-button', n_clicks=0, children='Search'),
    dcc.Graph(id='province-graph')
])

# Define the callback to update the graph
@app.callback(
    Output('province-graph', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [dependencies.State('province-input', 'value')]
)
def update_graph(n_clicks, province):
    filtered_df = df[df['schools_province'] == province] if province else df
    fig = px.bar(filtered_df, x='schools_province', y=['totalmale', 'totalfemale', 'totalstd'],
                 labels={'value': 'Number of Students', 'variable': 'Gender'},
                 barmode='group')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
