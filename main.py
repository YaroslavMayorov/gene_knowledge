import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from flask import Flask

server = Flask(__name__)
app = dash.Dash(__name__, server=server)

EXCEL_FILE = "NIHMS1635539-supplement-1635539_Sup_tab_4.xlsx"
s4b_results = pd.read_excel(EXCEL_FILE, sheet_name="S4B limma results", header=2)
s4a_values = pd.read_excel(EXCEL_FILE, sheet_name="S4A values", header=2)

s4b_results = s4b_results.dropna(subset=["EntrezGeneSymbol"])
s4b_results["negLog10AdjP"] = -np.log10(s4b_results["adj.P.Val"].replace(0, np.nan))

volcano_fig = go.Figure(
    data=go.Scatter(
        x=s4b_results["logFC"],
        y=s4b_results["negLog10AdjP"],
        mode="markers",
        text=s4b_results["EntrezGeneSymbol"],
        customdata=s4b_results["EntrezGeneSymbol"],
        marker={"size": 6},
    )
)

volcano_fig.update_layout(
    title="Volcano plot (Click on a point)",
    xaxis_title="log2 Fold change",
    yaxis_title="-log10 Adjusted P-value",
    hovermode="closest",
    height=600,
)

app.layout = html.Div(
    children=[
        html.H1("Protein activity dashboard"),
        dcc.Graph(
            id="volcano-plot",
            figure=volcano_fig,
            style={"width": "70%", "display": "inline-block", "vertical-align": "top"},
        ),
        html.Div(
            [
                html.H2("Boxplot: Young vs Old"),
                dcc.Graph(id="boxplot"),
            ],
            style={"width": "25%", "display": "inline-block", "marginLeft": "20px"},
        ),
    ]
)


@app.callback(
    Output("boxplot", "figure"),
    [Input("volcano-plot", "clickData")],
)
def update_boxplot(click_data):
    if click_data is None:
        return go.Figure()

    gene_symbol = click_data["points"][0]["customdata"]

    row_s4a = s4a_values[s4a_values["EntrezGeneSymbol"] == gene_symbol]

    if row_s4a.empty:
        return go.Figure()

    relevant_cols = [c for c in s4a_values.columns if ".OD" in c or ".YD" in c]

    old_cols = [c for c in relevant_cols if ".OD" in c]
    young_cols = [c for c in relevant_cols if ".YD" in c]

    old_values = row_s4a[old_cols].values.flatten()
    young_values = row_s4a[young_cols].values.flatten()

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

    box_fig = go.Figure(data=box_data)
    box_fig.update_layout(
        title=f"Expression for {gene_symbol}",
        yaxis_title="Protein concentration",
    )

    return box_fig


if __name__ == "__main__":
    app.run_server(debug=True)
