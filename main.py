import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from flask import Flask
import requests

# Server initialization
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# Loading data from Excel
EXCEL_FILE = "data/NIHMS1635539-supplement-1635539_Sup_tab_4.xlsx"
s4b_results = pd.read_excel(EXCEL_FILE, sheet_name="S4B limma results", header=2)
s4a_values = pd.read_excel(EXCEL_FILE, sheet_name="S4A values", header=2)

# Data preprocessing
s4b_results = s4b_results.dropna(subset=["EntrezGeneSymbol"])
s4b_results["negLog10AdjP"] = -np.log10(s4b_results["adj.P.Val"].replace(0, np.nan))

# Default values for threshold lines
default_logFC_limit = 1.0
default_pval_limit = 4

# Colors of points of volcano plot
RED_COLOR = "#EE553B"  # Significant genes
BLUE_COLOR = "#636efa"  # Insignificant genes

# Consts about volcano plot
POINT_SIZE = 6
VOLCANO_HEIGHT = 600
THRESHOLD_WIDTH = 1.5
THRESHOLD_COLOR = "black"
MIN_LOG_THRESHOLD = 0.5
MAX_LOG_THRESHOLD = 1.5
INIT_VAL_LOG_THRESHOLD = 1
STEP_LOG_THRESHOLD = 0.1
MIN_PVAL_THRESHOLD = 1
MAX_PVAL_THRESHOLD = 10
INIT_VAL_PVAL_THRESHOLD = 4
STEP_PVAL_THRESHOLD = 1

# Publications consts
LINKS_NUMBER = 5


def assign_colors_in_volcano(logfc_col, pval_col, fc_limit, pval_limit):
    """Assigns a color to the points:
        red if the point exceeds the thresholds fc_limit or pval_limit,
        otherwise blue. """
    colors = []
    for fc, pval in zip(logfc_col, pval_col):
        if (abs(fc) > fc_limit) or (pval > pval_limit):
            colors.append(RED_COLOR)
        else:
            colors.append(BLUE_COLOR)
    return colors


def create_volcano_plot(fc_limit, pval_limit, data):
    """
    Generates an interactive volcano plot with contour thresholds using data.
    """
    xvals = data["logFC"]
    yvals = data["negLog10AdjP"]
    symbols = data["EntrezGeneSymbol"]

    point_colors = assign_colors_in_volcano(xvals, yvals, fc_limit, pval_limit)

    fig = go.Figure([
        go.Scatter(
            x=xvals,
            y=yvals,
            mode="markers",
            text=symbols,
            customdata=symbols,
            marker=dict(size=POINT_SIZE, color=point_colors),
        )
    ])

    fig.update_layout(
        title="Interactive Volcano Plot",
        xaxis_title="log2 Fold Change",
        yaxis_title="-log10 Adjusted P-value",
        hovermode="closest",
        height=VOLCANO_HEIGHT,
        title_x=0.5,
        shapes=[
            dict(
                type="line",
                x0=fc_limit, x1=fc_limit,
                y0=0, y1=max(yvals),
                line=dict(color=THRESHOLD_COLOR, width=THRESHOLD_WIDTH, dash="dash")
            ),
            dict(
                type="line",
                x0=-fc_limit, x1=-fc_limit,
                y0=0, y1=max(yvals),
                line=dict(color=THRESHOLD_COLOR, width=THRESHOLD_WIDTH, dash="dash")
            ),
            dict(
                type="line",
                x0=min(xvals), x1=max(xvals),
                y0=pval_limit, y1=pval_limit,
                line=dict(color=THRESHOLD_COLOR, width=THRESHOLD_WIDTH, dash="dash")
            ),
        ]
    )
    return fig


# Default graph initialization
volcano_fig = create_volcano_plot(default_logFC_limit, default_pval_limit, s4b_results)

# Dash Application Interface
app.layout = html.Div(
    children=[
        html.H1(
            "Protein activity dashboard",
            style={"textAlign": "center", "width": "100%"}
        ),
        html.Div([
            html.Label("logFC threshold"),
            dcc.Slider(
                id="logfc-slider",
                min=MIN_LOG_THRESHOLD,
                max=MAX_LOG_THRESHOLD,
                step=STEP_LOG_THRESHOLD,
                value=INIT_VAL_LOG_THRESHOLD,
                tooltip={"always_visible": True}
            ),
            html.Br(),
            html.Label("P-value threshold"),
            dcc.Slider(
                id="pval-slider",
                min=MIN_PVAL_THRESHOLD,
                max=MAX_PVAL_THRESHOLD,
                step=STEP_PVAL_THRESHOLD,
                value=INIT_VAL_PVAL_THRESHOLD,
                tooltip={"always_visible": True}
            ),
        ], style={"width": "50%", "margin": "40px auto 0px auto"},
            className="slider-container"),
        html.Div(
            children=[
                dcc.Graph(
                    id="volcano-plot",
                    figure=volcano_fig,
                    style={
                        "minWidth": "500px",
                        "width": "70%",
                        "height": "600px",
                        "flexGrow": "1"
                    },
                ),
                html.Div(
                    [
                        html.H3("Boxplot: Young vs Old"),
                        dcc.Graph(
                            id="boxplot",
                            style={"height": "500px", "width": "100%"}
                        ),
                    ],
                    style={
                        "width": "30%",
                        "display": "flex",
                        "flexDirection": "column",
                        "alignItems": "center",
                        "minWidth": "300px",
                        "maxWidth": "700px"
                    },
                ),
            ],
            id="plots-container",
            style={
                "display": "flex",
                "flexDirection": "row",
                "alignItems": "start",
                "width": "100%",
                "flexWrap": "wrap"
            },
        ),
        html.Div(
            children=[
                html.Button(
                    "Show All",
                    id="paper-button",
                    n_clicks=0,
                    style={
                        "display": "none",
                    }
                ),
                html.Div(
                    id="paper-info",
                    style={
                        "width": "80%",
                    }
                ),
                dcc.Store(id="stored-pubmed-data")
            ],
            style={
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
            }
        )
    ],
    style={"fontFamily": "verdana"}
)


@app.callback(
    Output("volcano-plot", "figure"),
    [
        Input("logfc-slider", "value"),
        Input("pval-slider", "value")
    ]
)
def update_volcano_plot(fc_limit, pval_limit):
    """ Updates volcano plot when thresholds change """
    return create_volcano_plot(fc_limit, pval_limit, s4b_results)


@app.callback(
    [Output("boxplot", "figure"), Output("stored-pubmed-data", "data")],
    [Input("volcano-plot", "clickData")],
)
def update_boxplot(click_data):
    """Building a boxplot by clicking on a gene on a volcano plot,
    using s4a values database"""

    # Checking if a dot has been pressed
    if click_data is None:
        return go.Figure(), []

    # Extract the name of the gene from the click data
    gene_symbol = click_data["points"][0]["customdata"]

    # Filtering the s4a_values database to get the rows for the selected gene
    row_s4a = s4a_values[s4a_values["EntrezGeneSymbol"] == gene_symbol]

    # If there is no data on the gene, we return an empty graph with the message
    if row_s4a.empty:
        return go.Figure(layout={"title": f"No data for {gene_symbol}"}), []

    # Extracting data from columns of old (.OD) and young (.YD) samples
    relevant_cols = [c for c in s4a_values.columns if ".OD" in c or ".YD" in c]

    old_cols = [c for c in relevant_cols if ".OD" in c]
    young_cols = [c for c in relevant_cols if ".YD" in c]

    old_values = row_s4a[old_cols].values.flatten()
    young_values = row_s4a[young_cols].values.flatten()

    # Creating a list of data to build two boxplots on the same canvas
    box_data = []
    if len(young_values) > 0:
        box_data.append(
            go.Box(
                y=young_values,
                name="Young",
                boxpoints="all",
                boxmean=True
            )
        )
    if len(old_values) > 0:
        box_data.append(
            go.Box(
                y=old_values,
                name="Old",
                boxpoints="all",
                boxmean=True
            )
        )

    # Creating a boxplot with data
    box_fig = go.Figure(data=box_data)
    box_fig.update_layout(
        title=f"Expression for {gene_symbol}",
        yaxis_title="Protein concentration",
        title_x=0.5
    )

    gene_id = row_s4a.iloc[0]["EntrezGeneID"]

    # Requesting information about the gene from the service mygene.info
    try:
        query = f"http://mygene.info/v3/gene/{gene_id}"
        res_query = requests.get(query)
        if res_query.status_code == 404:
            return box_fig, [{"text": f"No papers about {gene_symbol} found", "pubmed": "error"}]
        if res_query.status_code != 200:
            raise Exception(f"{res_query.status_code}: {res_query.text}")

        # Extracting data about publications (list of dicts)
        pubmed_data = res_query.json()["generif"]

    except requests.exceptions.RequestException as e:
        pubmed_data = [{"text": f"Request error: {e}", "pubmed": "error"}]
    except Exception as e:
        pubmed_data = [{"text": f"Error: {e}", "pubmed": "error"}]
    return box_fig, pubmed_data


@app.callback(
    output=[
        dash.Output("paper-info", "children"),
        dash.Output("paper-button", "style"),
        dash.Output("paper-button", "children")
    ],
    inputs=[
        dash.Input("paper-button", "n_clicks"),
        dash.Input("stored-pubmed-data", "data")
    ],
)
def click_action(n_clicks, pubmed_data):
    """By default, we show LINKS_NUMBER links to publications,
    after clicking on the button - all"""

    # If there is no publication data, we display a message and hide the button
    if not pubmed_data:
        return html.Div([html.Strong("Choose gene for references", style={"fontSize": "20px"})],
                        style={"margin-bottom": "20px"}), {"display": "none"}, ""

    # If the button has not been pressed yet, set the click counter to 0
    if n_clicks is None:
        n_clicks = 0

    # If an error occurred when requesting publications, show the message and hide the button
    if pubmed_data[0]["pubmed"] == "error":
        return html.Div([html.Strong(pubmed_data[0]["text"], style={"fontSize": "20px", "color": RED_COLOR})],
                        style={"margin-bottom": "20px"}), {"display": "none"}, ""

    # If the number of clicks is even, we show only the first LINKS_NUMBER publications
    if n_clicks % 2 == 0:
        output_data = pubmed_data[:LINKS_NUMBER]
        button_text = "Show All" if len(pubmed_data) > LINKS_NUMBER else ""
    # If the number of clicks is odd, we show all the publications
    else:
        output_data = pubmed_data
        button_text = "Hide"

    button_style = {"display": "block"} if len(pubmed_data) > LINKS_NUMBER else {"display": "none"}

    # Creating a list of links to publications
    links = [
        html.Div(
            [
                html.A(
                    f"{paper['text']}",
                    href=f"https://pubmed.ncbi.nlm.nih.gov/{paper['pubmed']}/",
                    target="_blank",
                    className="paper-link"
                ),
                html.Br(),
                html.Span(f"PubMed ID: {paper['pubmed']}"),
                html.Hr(style={"border": "0.5px solid #ddd"})
            ]
        )
        for paper in output_data
    ]

    # Creating a css block with a title and a list of publications
    paper_info = html.Div(
        [
            html.Strong("Gene References:",
                        style={"fontSize": "20px"}
                        ),
            html.Br(),
            html.Br(),
        ]
        + links
    )
    return paper_info, button_style, button_text


if __name__ == "__main__":
    app.run_server(debug=True)
