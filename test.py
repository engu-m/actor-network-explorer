from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

app = Dash(__name__)

eye = html.Div(html.Div("Loading", className="loader eye"), className="load_container small")
mouth = html.Div(
    html.Div("Loading", className="loader mouth"), className="load_container small mouth"
)


rolling_emoji = html.Div(
    "😲",
    className="emoji",
)

app.layout = rolling_emoji


if __name__ == "__main__":
    app.run(debug=True)
