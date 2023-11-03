import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash_katex import DashKatex
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import math

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LITERA],
                meta_tags=[{'name': 'viewport','content':'width=device-width, initial-scale=0.5, maximum-scale=1.0,minimum-scale=0.5'}])
server = app.server
p=1/6
def binomial_probability(n, k, p):
    binomial_coefficient = math.comb(n, k)
    success_probability = p ** k
    failure_probability = (1 - p) ** (n - k)
    return binomial_coefficient * success_probability * failure_probability


def at_least_k_successes(n, k, p):
    if n is None or k is None or k > n:
        return 'NA'
    return sum(binomial_probability(n, i, p) for i in range(k, n + 1))

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H3("Probability of obtaining at least k successes in n trials",
                    className='text-center mb-3'),
            html.H3("Liars Dice: rolling at least k same faces among n dice",
                    className='text-center text-muted font-weight-lighter mb-3')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    html.Label("Number of trials (n):"),
                    dcc.Input(id='n-input', type='number', value=15),
                    html.Label("Number of successes (k):"),
                    dcc.Input(id='k-input', type='number', value=7),
                    dcc.Checklist(id='change-p-checklist', options=[{'label': '1’s are wild', 'value': 'change'}],
                              value=['change']),
                    html.Br(),
                    html.Div(id='probability-output'),
                    html.Div(id='next-best-move')
                    ])
            ], body=True, className="shadow-sm p-3 mb-5 bg-light rounded"),
            dbc.Card([
                html.Label("Binomial Probability Formula:"),
                DashKatex(expression=r'P(X = k) = \binom{n}{k} p^k (1 - p)^{n-k}'),
                html.Label("At Least k Successes Formula:"),
                DashKatex(expression=r'P(X \geq k) = \sum_{i=k}^{n} \binom{n}{i} p^i (1 - p)^{n-i}'),
                html.Div(id='p-value')
            ], body=True, className="shadow-sm p-3 mb-5 bg-light rounded")
        ], width={'size': 5}),
        dbc.Col([
            dbc.Card([
                dcc.Graph(id='probability-barplot')
            ], body=True, className="p-3 mb-5 bg-light rounded")
        ], width={'size': 7})
    ]),
    dbc.Row([
        dbc.Col([
            html.Footer([
                html.P("Developed by Victor Zommers | ",
                       style={'display': 'inline-block','font-size': '16px'}),
                html.A("Check out other dashboards", href="https://sites.google.com/view/victor-zommers/",
                       style={'display': 'inline-block', 'margin-left': '5px','font-size': '16px'},target="_blank")
            ], style={'text-align': 'left', 'margin-top': '20px'})
        ], width=12)
    ])
], fluid=True)

@app.callback(
    [Output('p-value', 'children'),
     Output('probability-output', 'children'),
     Output('next-best-move', 'children'),
     Output('probability-barplot', 'figure')],
    [Input('n-input', 'value'), Input('k-input', 'value'),Input('change-p-checklist', 'value')]
)
def update_probability_and_plot(n, k,checklist_values):
    p = 2 / 6 if 'change' in checklist_values else 1 / 6
    if n is None or k is None:
        return f'Where p = {round(p,3)} is independent probability for each trial (dice roll)','Please enter valid values for n and k.', 'NA', go.Figure()
    if k > n:
        return f'Where p = {round(p,3)} is independent probability for each trial (dice roll)','Number of successes cannot be greater than number of trials.', 'NA', go.Figure()

    probabilities = [at_least_k_successes(n, i, p) for i in range(1, k + 1)]
    figure = go.Figure(go.Bar(x=list(range(1, k + 1)), y=probabilities))
    figure.update_layout(xaxis_title="k [dice of same face]", yaxis_title="Probability", template="simple_white")
    figure.add_shape(type="line", line_color="salmon", line_width=3, opacity=1, line_dash="dot",x0=0, x1=1, xref="paper", y0=0.5, y1=0.5, yref="y")
    figure.update_xaxes(tickvals=list(range(1, k + 1)))  # ensure x-axis labels are integers

    probability = at_least_k_successes(n, k, p)
    next_move = at_least_k_successes(n, k + 1, p)
    return f'Where p = {round(p,3)} is independent probability for each trial (dice roll)',f'Probability of current bet: {round(probability,8)}', f'Probability of next bet (k+1 quantity raise): {round(next_move,8)}', figure


if __name__ == '__main__':
    app.run_server(debug=False)