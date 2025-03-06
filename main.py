import dash
from dash import dcc, html
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
    title="Volcano Plot (Click on a point)",
    xaxis_title="log2 Fold Change",
    yaxis_title="-log10 Adjusted P-value",
    hovermode="closest",
    height=600,
)

app.layout = html.Div(
    children=[
        html.H1("Protein Activity Dashboard"),
        dcc.Graph(
            id="volcano-plot",
            figure=volcano_fig,
            style={"width": "70%", "display": "inline-block", "vertical-align": "top"},
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)