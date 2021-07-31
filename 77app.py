import dash
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import json
import os

################################################################################################
# Load the data 
################################################################################################
#2019 Endorsements
endorsements_2019 = pd.read_csv('data/endorsements_2019_updated.csv')

#player sponsorship 2020 2021
player_sponsorships_2020_2021 = pd.read_csv('data/player_sponsorships_2020_2021.csv')

#player stats 2020 2021
player_stats_2020_2021 = pd.read_csv('data/2020-2021 NBA Player Stats.csv')

#2020 2021 player data combined
player_2020_2021_count_fg_stats_social_media = pd.read_csv('data/player_2020_2021_count_fg_stats_social_media_csv.csv')

#industry data to plot
player_sponsorships_2020_2021_industry = player_sponsorships_2020_2021.merge(player_stats_2020_2021, on='Player')
industry_fg = player_sponsorships_2020_2021_industry.groupby('Industry').mean().sort_values(by='PTS', ascending=False)['PTS']
industry_fg = pd.DataFrame(industry_fg)
industry_fg["PTS"] = round(industry_fg["PTS"], 1)
industry_toplot = industry_fg.reset_index()
#industry_toplot

#subindustry data to plot
subindustry_fg = player_sponsorships_2020_2021_industry.groupby('Subindustry').mean().sort_values(by='Age', ascending=False)['Age']
subindustry_fg = pd.DataFrame(subindustry_fg)
subindustry_fg["Age"] = round(subindustry_fg["Age"], 1)
subindustry_toplot = subindustry_fg.reset_index()
#subindustry_toplot

#Industry
#industry = pd.read_csv('data/Industry.csv')
#industry.fillna("No Subindustry", inplace=True)

#Team Valuations
team_valuations = pd.read_csv('data/Team_Valuations_City (1).csv')
team_valuations = team_valuations.rename(columns={"Item": "Team", "Attribute" : "Year", "Value" : "Valuation (in millions)"})
team_valuations = team_valuations[team_valuations["Team"].notna()]
team_valuations["Year"] = team_valuations["Year"].astype("int")
add_zeroes = "000000"
team_valuations["Valuation (in millions)"] = team_valuations["Valuation (in millions)"].map(str) + add_zeroes
team_valuations["Valuation (in millions)"] = team_valuations["Valuation (in millions)"].str.replace(".", "")
convert_dict = {"City": str,
               "Team": str,
               "Valuation (in millions)": int,
               "LAT": int,
               "LONG" : int
               }
team_valuations_ = team_valuations.copy()
team_valuations_ = team_valuations_.astype(convert_dict)
team_valuations_['Team'] = team_valuations_['Team'].astype(str)
################################################################################################
# plotly vizulaizations
################################################################################################

####
# endorsement locations
endorsement_location = endorsements_2019[['Endorsment (millions)','Division']]
endorsement_location_fig = px.bar(endorsement_location, 
             x='Division', y='Endorsment (millions)', 
             color_discrete_sequence =[('blue')]*len(endorsement_location))

####
#value cost location
value_cost_location = endorsements_2019[['Value to cost','Division']]
value_cost_location_fig = fig = px.bar(value_cost_location, 
             x='Division', y='Value to cost', 
             color_discrete_sequence =[('red')]*len(endorsement_location),
             title='Value to Cost by NBA Division')


#player sponsorship compared to fg average
sponsorship_fg_fig = px.scatter(player_2020_2021_count_fg_stats_social_media, x="FG", y="Sponsorship", color="Sponsorship",
                 size='FG', hover_data=['Player'],color_continuous_scale='rdbu')


#industry compared to fg average
industry_fg_fig = px.scatter(player_2020_2021_count_fg_stats_social_media, x="FG", y="Industry", color="Industry",
                 size='FG', hover_data=['Player'],color_continuous_scale='rdbu', title = "NBA Player Industry Compared to FG Average")


#sub industry compared to fg average
subindustry_fg_fig = px.scatter(player_2020_2021_count_fg_stats_social_media, x="FG", y="Subindustry", color="Subindustry",
                 size='FG', hover_data=['Player'],color_continuous_scale='rdbu')


#Average Points by Sponsorship Industry
#avg_pts_industry_fig = px.bar(industry_toplot, 
             #x='Industry', y='PTS',color_discrete_sequence =[('blue')]*len(industry_toplot),
             #title='Average Points by Sponsorship Industry')

#Average Points by Sponsorship Subindustry
#avg_pts_subindustry_fig = px.bar(subindustry_toplot, 
             #x='Age', y='Subindustry',
             #color_discrete_sequence =[('red')]*len(subindustry_toplot),
             #title='Average Age by Sponsorship Subindustry')

#Industry Tree Map
#industry_tree_fig = px.treemap(industry, path=['Industry', 'Subindustry'], 
                 #values='total', color='Industry')
#fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
#fig.data[0].hovertemplate = '%{label}<br>%{value}'

#player sponsorship and tenure
#sponsor_tenure = px.scatter(player_stats_social_media_tenure, x="Tenure (Years)", y="Sponsorship", hover_data=['Player'],color_continuous_scale='rdbu', 
                #title = "NBA Player Sponsorships by Tenure")

# Team valuations bubble map
bubble_map = px.scatter_geo(team_valuations_, 
                     lat="LAT", 
                     lon= "LONG", 
                     color="Team",
                     hover_name="Team",
                     color_discrete_sequence = ["blue", "red", "yellow"],
                     #hover_data = {'Team': True, 'City': True, 'LAT':False, 'LONG':False, 'Year': True, 'Valuation (in millions)': True},
                     size="Valuation (in millions)",
                     animation_frame="Year",
                     scope = "usa"
                     )

################################################################################################
# create dash app 
################################################################################################
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])
server = app.server

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dbc.Navbar(
            children=[
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(
                                html.H2('Team 77'),
                                style={'color': "#18408b"}
                            ),
                            dbc.Col(
                                dbc.NavbarBrand(
                                    "Athlete Sponsorships", className="ml-2",
                                    style={'color': "#18408b"}
                                )
                            ),
                        ],
                        no_gutters=True,
                        className="ml-auto flex-nowrap mt-3 mt-md-0",
                        align="center",
                    ),
                    href=app.get_relative_path("/"),
                ),
                dbc.Row(
                    children=[
                        dbc.NavLink("Home", href=app.get_relative_path("/")),
                        dbc.NavLink("Player Metrics", href=app.get_relative_path("/player")),
                        dbc.NavLink("Marketing Metrics", href=app.get_relative_path("/marketing"),),
                        dbc.NavLink(
                            "Discovering Sponsorships", href=app.get_relative_path("/discovering")
                        ),
                    ],
                    style={"paddingLeft": "500px", 'color': '#c00001', 'font-weight': 'bold'},
                ),
            ], color='#ffffff'
        ),
        html.Div(id="page-content"),
    ]
)

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page_content(pathname):
    path = app.strip_relative_path(pathname)
    if not path:
        return dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4("How Can Sponsors Objectively Discover Their Next Marquee Athlete?", className="card-title"),
                        html.P(
                            "The purpose of this application is to allow sponsors to utilize existing statistical player and influential "
                            "marketing data in order to determine which NBA athletes should be targeted for their sponsorship.",
                            className="card-text",
                        ),
                    ]
                ),
            ],
            style={"width": "80%",
                   "text-align": "center",
                   "background-color": "#7dafff",
                   "border-radius": "30px",
                   "margin": "auto"},
        )
    elif path == "player":
        return dbc.Container(
            [
                dbc.Row([
                    dbc.Col(html.H1("PLAYER METRICS"), className='text-center', style={'color': '#ffffff'})
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            html.H5("NBA Player Subindustry Compared to FG Average", className="card-title text-center"),
                            dbc.CardBody([
                              dcc.Graph(id='graph1', figure=sponsorship_fg_fig),
                              html.P('Looking at the scatter plot, there seems to be a bell shaped distribution between field goal percentage and the number of sponsorships received.')  
                            ])
                        ], color='#c00001', inverse=True)
                    ], width={'size': 6}),
                    dbc.Col([
                        dbc.Card([
                            html.H5("PLACEHOLDER", className="card-title text-center"),
                            dbc.CardBody([
                              #dcc.Graph(id='graph1', figure=sponsor_tenure)  
                            ])
                        ], color='#7f7f7f', inverse=True)
                    ], width={'size': 6}),
                ]),
                dbc.Row([
                    dbc.Col(html.H1("    "))
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            html.H5("PLACEHOLDER", className=('card-title text-center')),
                            dbc.CardBody([
                              dcc.Graph(id='graph1', figure={}),
                              dcc.Graph(id='graph1', figure={})
                            ])
                        ], color='#4472c4', inverse=True)
                    ], width={'size': 6}),
                    dbc.Col([
                        dbc.Card([
                            html.H5("PLACEHOLDER", className="card-title text-center"),
                            dbc.CardBody([
                              dcc.Graph(id='graph1', figure={}),
                              dcc.Graph(id='graph1', figure={})
                            ])
                        ], color='#4472c4', inverse=True)

                    ], width={'size': 6}),
                ]),
                dbc.Row([
                    dbc.Col(html.H1("    "))
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            html.H5("PLACEHOLDER", className="card-title text-center"),
                            dbc.CardBody([
                                dcc.Dropdown(id='player-dropdown',
                                     options=[
                                         {'label': 'Age', 'value': 'Age'},
                                         {'label': 'Team Rank', 'value': 'Team Rank'},
                                         {'label': 'Player Rank', 'value': 'Player Rank'},
                                         {'label': 'Win Shares', 'value': 'Win Shares'}
                                     ],value='Age'),
                        dcc.Graph(id='graph5', figure={})]),
                        ], color='#c00001', inverse=True)
                    ]),
                ]),  
            ], style={'background-color': "#18408b"}, fluid=True)
    elif path == "marketing":
        return dbc.Container(
            [
                dbc.Row([
                    dbc.Col(html.H1("MARKETING METRICS"), className='text-center text-primary')
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            html.H5("PLACEHOLDER", className=('card-title text-center')),
                            dbc.CardBody([
                                dcc.Graph(id='graph1', figure={}),
                                dcc.Graph(id='graph1', figure={})
                        ])
                    ], color='#c00001', inverse=True)
                    ]),
                    dbc.Col([
                        dbc.Card([
                            html.H5("PLACEHOLDER", className=('card-title text-center')),
                            dbc.CardBody([
                                dcc.Graph(id='graph1', figure={})
                        ])
                    ], color='#7f7f7f', inverse=True)
                ])
                ]),
                dbc.Row([
                    dbc.Col(html.H1("    "))
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            html.H5("PLACEHOLDER", className=('card-title text-center')),
                            dbc.CardBody([
                                dcc.Graph(id='graph1', figure={})
                            ])
                        ], color='#4472c4', inverse=True)
                    ])
                ]),
                dbc.Row([
                    dbc.Col(html.H1("    "))
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            html.H5("Team Valuation (in millions)", className=('card-title text-center')),
                            dbc.CardBody([
                                dcc.Graph(id='graph1', figure=bubble_map)
                            ])
                        ], color='#c00001', inverse=True)
                    ])
                ])
            ], style={'background-color': "#18408b"}, fluid=True)  
    elif path == "discovering":
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([])
                ]),
                dbc.Col([
                    dbc.Card([])
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([])
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([])
                ])
            ]),
            dbc.Row([
              dbc.Col([
                  dbc.Card([])
              ])
            ]),
        ])
    else:
        return "404"
    

if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port='8050', debug=True)