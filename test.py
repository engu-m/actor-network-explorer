from dash import Dash, html
import dash_bootstrap_components as dbc

app = Dash(__name__)

eye = html.Div(html.Div("Loading", className="loader eye"), className="load_container small")
mouth = html.Div(
    html.Div("Loading", className="loader mouth"), className="load_container small mouth"
)


app.layout = html.Div(
    [
        html.Div(
            [
                html.Div([eye, eye], className="frow"),
                html.Div(mouth, className="frow"),
            ],
            className="load_container big fcol face",
        ),
    ]
)


if __name__ == "__main__":
    app.run(debug=True)
