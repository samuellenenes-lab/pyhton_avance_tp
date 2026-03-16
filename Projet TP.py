import pandas as pd
import numpy as np

import dash
from dash import html, dcc, dash_table, Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go


# =======================
# Data
# =======================

CSV_PATH = "C:\\Users\\samue\\OneDrive\\Documents\\Cours\\M1 ECAP\\Python avancée\\TD1\\cours-m1-ecap\\datasets\\data.csv"
df = pd.read_csv(CSV_PATH)

df["Transaction_Date"] = pd.to_datetime(df["Transaction_Date"], errors="coerce")
df = df.dropna(subset=["Transaction_Date"]).copy()

df["Discount_pct"] = pd.to_numeric(df["Discount_pct"], errors="coerce").fillna(0)
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0)
df["Avg_Price"] = pd.to_numeric(df["Avg_Price"], errors="coerce").fillna(0)

# CA 
df["Revenue"] = df["Quantity"] * df["Avg_Price"] * (1 - df["Discount_pct"] / 100.0)

df["Year"] = df["Transaction_Date"].dt.year
df["Month"] = df["Transaction_Date"].dt.month

# Décembre 2019 
TARGET_YEAR = 2019
TARGET_MONTH = 12


def filter_df(location_value):
    if location_value and location_value != "ALL":
        return df[df["Location"] == location_value].copy()
    return df.copy()


def indicator_kpi_fig(title, value, reference, value_format="~s"):
    """
    KPI avec go.Indicator + delta(reference=mois précédent)
    - sans triangles/symboles
    """
    fig = go.Figure(go.Indicator(
        mode="number+delta",
        value=value,
        number={"valueformat": value_format},
        delta={
            "reference": reference,
            "valueformat": value_format,
            "relative": False,
        },
        title={"text": title},
    ))
    fig.update_layout(
        height=210,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(t=40, b=0, l=20, r=20),
    )
    return fig


# =======================
# App
# =======================

#Initialisation
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

HEADER_BG = "#b9d9e6"   
PANEL_BG = "#ffffff"
BORDER = "#ffffff"
TEXT_MUTED = "#6c757d"


def panel(children, padding="12px"):
    return html.Div(
        children=children,
        style={
            "background": PANEL_BG,
            "border": f"1px solid {BORDER}",
            "borderRadius": "10px",
            "padding": padding,
        },
    )


app.layout = dbc.Container(
    fluid=True,
    style={"padding": "0", "background": "#f4f7fb", "minHeight": "100vh"},
    children=[
        # ===== en-tête =====
        html.Div(
            style={
                "background": HEADER_BG,
                "height": "64px",
                "display": "flex",
                "alignItems": "center",
                "padding": "0 18px",
                "borderBottom": f"1px solid {BORDER}",
            },
            children=[
                html.Div("ECAP Store", style={"fontSize": "28px", "fontWeight": "600"}),
                html.Div(style={"flex": "1"}),
                html.Div(
                    style={"width": "200px"},
                    children=[
                        dcc.Dropdown(
                            id="zone_dd",
                            options=[{"label": "Toutes les zones", "value": "ALL"}]
                            + [{"label": loc, "value": loc} for loc in sorted(df["Location"].dropna().unique())],
                            clearable=False,
                            placeholder="Choisissez des zones"
                        )
                    ],
                ),
            ],
        ),

        # ===== corp =====
        dbc.Container(
            fluid=True,
            style={"padding": "18px"},
            children=[
                dbc.Row(
                    className="g-3",
                    children=[
                        # colonne gauche
                        dbc.Col(
                            width=5,
                            children=[
                                dbc.Row(
                                    className="g-3",
                                    children=[
                                        dbc.Col(
                                            panel(
                                                dcc.Graph(
                                                    id="kpi_ca",
                                                    config={"displayModeBar": False},
                                                    style={"height": "210px"},
                                                ),
                                                padding="8px",
                                            ),
                                            width=6,
                                        ),
                                        dbc.Col(
                                            panel(
                                                dcc.Graph(
                                                    id="kpi_tx",
                                                    config={"displayModeBar": False},
                                                    style={"height": "210px"},
                                                ),
                                                padding="8px",
                                            ),
                                            width=6,
                                        ),
                                    ],
                                ),
                                html.Div(style={"height": "14px"}),
                                panel(
                                    [
                                        html.Div(
                                            "Fréquence des 10 meilleures ventes",
                                            style={"fontWeight": "700", "margin": "6px 0 6px 6px"},
                                        ),
                                        dcc.Graph(
                                            id="bar_top10",
                                            config={"displayModeBar": False},
                                            style={"height": "470px"},
                                        ),
                                    ]
                                ),
                            ],
                        ),

                        # colonne droite
                        dbc.Col(
                            width=7,
                            children=[
                                panel(
                                    [
                                        html.Div(
                                            "Evolution du chiffre d'affaire par semaine",
                                            style={"fontWeight": "700", "margin": "6px 0 6px 6px"},
                                        ),
                                        dcc.Graph(
                                            id="line_week",
                                            config={"displayModeBar": False},
                                            style={"height": "340px"},
                                        ),
                                    ]
                                ),
                                html.Div(style={"height": "14px"}),
                                panel(
                                    [
                                        html.Div(
                                            "Table des 100 dernières ventes",
                                            style={"fontWeight": "700", "margin": "6px 0 10px 6px"},
                                        ),
                                        dash_table.DataTable(
                                            id="table_last100",
                                            page_size=10,
                                            page_current=0,
                                            filter_action="native",
                                            sort_action="native",
                                            style_table={"overflowX": "auto"},
                                            style_cell={
                                                "fontFamily": "Arial",
                                                "fontSize": "13px",
                                                "padding": "8px",
                                                "whiteSpace": "nowrap",
                                            },
                                            style_header={
                                                "fontWeight": "700",
                                                "backgroundColor": "#f2f5fa",
                                                "borderBottom": f"1px solid {BORDER}",
                                            },
                                            style_data={
                                                "borderBottom": f"1px solid {BORDER}",
                                            },
                                        ),
                                    ]
                                ),
                            ],
                        ),
                    ],
                )
            ],
        ),
    ],
)


# =======================
# Callbacks
# =======================
@app.callback(
    Output("kpi_ca", "figure"),
    Output("kpi_tx", "figure"),
    Output("bar_top10", "figure"),
    Output("line_week", "figure"),
    Output("table_last100", "data"),
    Output("table_last100", "columns"),
    Input("zone_dd", "value"),
)
def update_dashboard(zone_value):
    dff = filter_df(zone_value)

    # --- Mois cible vs mois précédent ---

    dec = dff[(dff["Year"] == TARGET_YEAR) & (dff["Month"] == TARGET_MONTH)]
    prev = dff[(dff["Year"] == TARGET_YEAR) & (dff["Month"] == TARGET_MONTH - 1)]

    # KPI 1: CA

    dec_ca = dec["Revenue"].sum()
    prev_ca = prev["Revenue"].sum()
    fig_kpi_ca = indicator_kpi_fig("December", dec_ca, prev_ca, value_format = ".3s")

    # KPI 2: nb de ventes (lignes) — référence = mois précédent

    dec_n = float(len(dec))
    prev_n = float(len(prev))
    fig_kpi_tx = indicator_kpi_fig("December", dec_n, prev_n, value_format=".0f")

    # --- Bar Top 10 categories (fréquence) par genre ---

    top_cats = (
        dff.groupby("Product_Category")
        .size()
        .sort_values(ascending=False)
        .head(10)
        .index
        .tolist()
    )
    bar_df = dff[dff["Product_Category"].isin(top_cats)].copy()
    freq = (
        bar_df.groupby(["Product_Category", "Gender"])
        .size()
        .reset_index(name="Total vente")
    )

    # ordre des catégories (du + vendu au - vendu)
    cat_order = (
        dff.groupby("Product_Category")
        .size()
        .loc[top_cats]
        .sort_values(ascending=False)
        .index
        .tolist()
    )

    fig_bar = px.bar(
        freq,
        x="Total vente",
        y="Product_Category",
        color="Gender",
        barmode="group",
        orientation="h",
        category_orders={"Product_Category": cat_order, 
                         "Gender": ["F", "M"]},
        labels={"Product_Category": "Categorie du produit"},
    )
    fig_bar.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        legend_title_text="Sexe",
        paper_bgcolor="#dbebf8",
        plot_bgcolor="#dbebf8"
    )

    # --- CA par semaine ---
    weekly = (
        dff.set_index("Transaction_Date")
        .sort_index()
        .resample("W")
        .agg({"Revenue": "sum"})
        .reset_index()
    )
    weekly["Semaine"] = weekly["Transaction_Date"]

    fig_line = px.line(
        weekly,
        x="Semaine",
        y="Revenue",
        labels={"Revenue": "Chiffre d'affaire", "Semaine": "Semaine"},
    )
    fig_line.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor="#dbebf8",
    plot_bgcolor="#dbebf8",
    xaxis=dict(
        showgrid=True,
        gridcolor="white",
        gridwidth=1,
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="white",
        gridwidth=1,
    ),
)

    # --- table des 100 dernières ventes ---
    cols = ["Transaction_Date", "Gender", "Location", "Product_Category", "Quantity", "Avg_Price", "Discount_pct"]
    last100 = (
        dff.sort_values("Transaction_Date", ascending=False)
        .loc[:, cols]
        .head(100)
        .copy()
    )
    last100["Transaction_Date"] = last100["Transaction_Date"].dt.strftime("%Y-%m-%d")

    columns = [
        {"name": "Date", "id": "Transaction_Date"},
        {"name": "Gender", "id": "Gender"},
        {"name": "Location", "id": "Location"},
        {"name": "Product_Category", "id": "Product_Category"},
        {"name": "Quantity", "id": "Quantity"},
        {"name": "Avg_Price", "id": "Avg_Price"},
        {"name": "Discount_pct", "id": "Discount_pct"},
    ]

    return fig_kpi_ca, fig_kpi_tx, fig_bar, fig_line, last100.to_dict("records"), columns


if __name__ == '__main__':
    app.run_server(debug=True)