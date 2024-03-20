from dash import Dash, html
import dash_bootstrap_components as dbc

app = Dash(__name__)

eye = html.Div(html.Div("Loading", className="loader eye"), className="load_container small")
mouth = html.Div(
    html.Div("Loading", className="loader mouth"), className="load_container small mouth"
)


rolling_emoji = html.Div(
    [
        html.Div(
            "😲",
            className="emoji",
        ),
    ],
    className="load_container",
)

app.layout = rolling_emoji


if __name__ == "__main__":
    app.run(debug=True)
