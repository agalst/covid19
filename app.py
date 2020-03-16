import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, ClientsideFunction

import numpy as np
import pandas as pd
import datetime
from datetime import datetime as dt
import pathlib
import glob
import plotly.graph_objs as go

path = r'./COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/' # use your path
#all_files = glob.glob(path + "/*.csv")

li = []

#for filename in all_files:
#    df = pd.read_csv(filename)
#    li.append(df)

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server
app.config.suppress_callback_exceptions = True

# Path
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

# Read data
#df = pd.concat(li, axis=0, ignore_index=True).reset_index()
#print(df.head())
df = pd.read_pickle("df_16032020.pkl")

#df = df.drop(["Longitude", "Latitude"], axis = 1)
#df["Last Update"] = pd.to_datetime(df["Last Update"])
#df["Last Update Date"] = df["Last Update"].apply(lambda x: x.date())
#df = df.groupby(by=["Last Update Date", "Country/Region"]).agg({"Last Update" : "last", "Confirmed" : "sum", "Deaths" :"sum", "Recovered" :"sum"}).reset_index()
#df["Country/Region"] = df["Country/Region"].astype('category')
#df["Province/State"] = df["Province/State"].astype('category')
#df = df.drop(["Province/State"], axis = 1)

print(df.info())
df.to_pickle("df_16032020.pkl")
country_list = df.sort_values(by="Confirmed").drop_duplicates()["Country/Region"].values
#df["Admit Source"] = []#df["Admit Source"].fillna("Not Identified")
prov_list = ["DUMMY"]#df["Admit Source"].unique().tolist()

# Date
# Format checkin Time
#df["Check-In Time"] = df["Check-In Time"].apply(
#    lambda x: dt.strptime(x, "%Y-%m-%d %I:%M:%S %p")
#)  # String -> Datetime

# Insert weekday and hour of checkin time
#df["Days of Wk"] = df["Check-In Hour"] = df["Check-In Time"]
#df["Days of Wk"] = df["Days of Wk"].apply(
#    lambda x: dt.strftime(x, "%A")
#)  # Datetime -> weekday string

#df["Check-In Hour"] = df["Check-In Hour"].apply(
#    lambda x: dt.strftime(x, "%I %p")
#)  # Datetime -> int(hour) + AM/PM

day_list = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

#check_in_duration = df["Check-In Time"].describe()

# Register all departments for callbacks
all_departments = ["DUMMY"]#df["Department"].unique().tolist()
wait_time_inputs = [
    Input((i + "_wait_time_graph"), "selectedData") for i in all_departments
]
score_inputs = [Input((i + "_score_graph"), "selectedData") for i in all_departments]


def description_card():
    """

    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H3("COVID-19 Analytics"),
            html.Div(
                id="intro",
                children="Explore the virus spread dynamics.",
            ),
        ],
    )


def generate_control_card():
    """

    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.P("Select country"),
            dcc.Dropdown(
                id="country-select",
                options=[{"label": i, "value": i} for i in country_list],
                value=country_list[0],
            ),
            html.Br(),
            html.P("Select analysis Time"),
            dcc.DatePickerRange(
                id="date-picker-select",
                start_date=dt(2014, 1, 1),
                end_date=dt(2014, 1, 15),
                min_date_allowed=dt(2014, 1, 1),
                max_date_allowed=dt(2014, 12, 31),
                initial_visible_month=dt(2014, 1, 1),
            ),
            html.Br(),
            html.Br(),
            html.P("Included provinces"),
            dcc.Dropdown(
                id="admit-select",
                options=[{"label": i, "value": i}   for i in prov_list],
                value=prov_list[:],
                multi=True,
            ),
            html.Br(),
            html.Div(
                id="reset-btn-outer",
                children=html.Button(id="reset-btn", children="Reset", n_clicks=0),
            ),
        ],
    )





app.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[html.Img(src=app.get_asset_url("plotly_logo.png"))],
        ),
        # Left column
        html.Div(
            id="left-column",
            className="four columns",
            children=[description_card(), generate_control_card()]
            + [
                html.Div(
                    ["initial child"], id="output-clientside", style={"display": "none"}
                )
            ],
        ),
        # Right column
        html.Div(
            id="right-column",
            className="eight columns",
            children=[
                # Patient Volume Heatmap
                html.Div(
                    id="patient_volume_card",
                    children=[
                        html.B("Number of confirmed cases"),
                        html.Hr(),
                        dcc.Graph(id='covid-dynamic-plot', figure={'data': [{
                                            'x': [1, 2, 3, 4],
                                            'y': [4, 1, 3, 5],
                                            'text': ['a', 'b', 'c', 'd'],
                                            'customdata': ['c.a', 'c.b', 'c.c', 'c.d'],
                                            'name': 'Trace 1',
                                            'mode': 'markers',
                                            'marker': {'size': 12}},
                                        {
                                            'x': [1, 2, 3, 4],
                                            'y': [9, 4, 1, 4],
                                            'text': ['w', 'x', 'y', 'z'],
                                            'customdata': ['c.w', 'c.x', 'c.y', 'c.z'],
                                            'name': 'Trace 2',
                                            'mode': 'markers',
                                            'marker': {'size': 12}
                                        }],
                                'layout': {'clickmode': 'event+select'}
                            }
                        ),
                    ],
                ),
            ],
        ),
    ],
)



@app.callback(
    Output("covid-dynamic-plot", "figure"),
    [
        Input("country-select", "value"),
    ],
)
def update_plot(country):
    print(country)
    if country in df["Country/Region"].unique():
        subset = df[df["Country/Region"] == country].dropna()
        subset = subset.sort_values(by="Last Update")
        data_conf = go.Scatter(x=subset["Last Update"],
                         y=subset["Confirmed"].values, name="Confirmed")
        data_death = go.Scatter(x=subset["Last Update"],
                         y=subset["Deaths"].values, name="Died")
        data_rec = go.Scatter(x=subset["Last Update"],
                         y=subset["Recovered"].values, name="Recovered")
        #layout = go.Layout(title='Energy Plot', xaxis=dict(title='Date'),
        #           yaxis=dict(title='(kWh)'))
        print(data_conf)
        return {"data" : [data_conf, data_death, data_rec], "layout" :  {'clickmode': 'event+select', 
                                              'xaxis' : {"title" : 'Update date'},
                                              'yaxis' : {"title" : 'Aggregated number of cases'},
                                              'font' : dict(family="Courier New, monospace", size=14, color="#7f7f7f")}}
    else:
        return None



# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)
