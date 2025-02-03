import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd

# Load data
competitor_data = pd.read_json("data/competitor_data.json")
reviews_data = pd.read_csv("data/sentiment_analysis.csv")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H1("Market Research Dashboard", className="text-center my-4"),

    dbc.Row([
        dbc.Col([
            html.H3("Competitor Products"),
            dcc.Dropdown(
                id="competitor-dropdown",
                options=[{"label": name, "value": name} for name in competitor_data["name"].unique()],
                placeholder="Select a Competitor",
            ),
            html.Div(id="competitor-details")
        ], width=6),

        dbc.Col([
            html.H3("Sentiment Analysis"),
            dcc.Graph(
                id="sentiment-bar-chart",
                figure={
                    "data": [
                        {
                            "x": reviews_data["sentiment"].value_counts().index,
                            "y": reviews_data["sentiment"].value_counts().values,
                            "type": "bar",
                        }
                    ],
                    "layout": {"title": "Sentiment Breakdown"},
                },
            ),
        ], width=6),
    ]),

    dbc.Row([
        dbc.Col([
            html.H3("Price Analysis"),
            dcc.Graph(
                id="price-chart",
                figure={
                    "data": [
                        {
                            "x": competitor_data["name"],
                            "y": competitor_data["price"],
                            "type": "bar",
                            "name": "Price",
                        }
                    ],
                    "layout": {"title": "Competitor Pricing"},
                },
            ),
        ])
    ])
])

@app.callback(
    Output("competitor-details", "children"),
    [Input("competitor-dropdown", "value")]
)
def display_competitor_details(selected_name):
    if selected_name:
        competitor = competitor_data[competitor_data["name"] == selected_name].iloc[0]
        return html.Div([
            html.P(f"Name: {competitor['name']}"),
            html.P(f"Price: {competitor['price']}"),
            html.P(f"Rating: {competitor['rating']}"),
        ])
    return "Select a competitor to see details."

if __name__ == "__main__":
    app.run_server(debug=True)
