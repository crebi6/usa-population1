import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc

# Load and preprocess data
url = "https://raw.githubusercontent.com/JoshData/historical-state-population-csv/primary/historical_state_population_by_year.csv"
df = pd.read_csv(url, names=['state', 'year', 'population'])
df['state'] = df['state'].str.upper()
df = df[df['year'] <= 2022]  # Remove future projections if any
df['population'] = df['population'].astype(int)

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server  # Required for Render deployment

# App layout with improved styling
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("US State Population Analysis", className="text-center mb-4"),
            html.P("Explore historical population trends across US states from 1900 to 2022. "
                   "Select a year to view state populations on the map, then click any state to see its historical trend.",
                   className="text-muted text-center mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label("Select Year", className="mb-2"),
                    dcc.Dropdown(
                        id='year-dropdown',
                        options=[{'label': str(y), 'value': y} for y in sorted(df['year'].unique())],
                        value=2022,
                        clearable=False,
                        className="mb-4"
                    ),
                    html.Label("Or Select State", className="mb-2"),
                    dcc.Dropdown(
                        id='state-dropdown',
                        options=[{'label': s, 'value': s} for s in sorted(df['state'].unique())],
                        value='CA',
                        clearable=False
                    )
                ])
            ], className="mb-4")
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='state-population-map', style={'height': '600px'})
                ])
            ])
        ], md=9)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='state-population-trend', style={'height': '400px'})
                ])
            ])
        ], width=12)
    ], className="mt-4")
], fluid=True)

# Callbacks
@callback(
    Output('state-population-map', 'figure'),
    Input('year-dropdown', 'value')
)
def update_map(selected_year):
    filtered = df[df['year'] == selected_year]
    fig = px.choropleth(
        filtered, locations='state', locationmode="USA-states",
        color='population', scope="usa", 
        color_continuous_scale="Viridis",
        hover_data={'population': ':,'},
        title=f'Population Distribution ({selected_year})'
    )
    fig.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        coloraxis_colorbar_title="Population",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    return fig

@callback(
    Output('state-population-trend', 'figure'),
    [Input('state-population-map', 'clickData'),
     Input('state-dropdown', 'value')]
)
def update_trend(click_data, selected_state):
    ctx = callback_context
    if ctx.triggered[0]['prop_id'] == 'state-population-map.clickData':
        selected_state = click_data['points'][0]['location']
    
    state_data = df[df['state'] == selected_state]
    fig = px.line(
        state_data, x='year', y='population',
        title=f'Population Trend for {selected_state}',
        markers=True, line_shape='spline'
    )
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Population",
        hovermode="x unified",
        yaxis_tickformat=',',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True) 
