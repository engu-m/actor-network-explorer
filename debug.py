from dash import dcc, html
import numpy as np


def tabs(prod_panels, debug):
    if debug:
        return dcc.Tabs(
            [
                dcc.Tab(
                    html.Div(prod_panels),
                    label="Main",
                    value="tab-1",
                ),
                dcc.Tab(
                    html.Div(
                        [
                            myClipboard("debug-info", "Full graph"),
                            html.Pre(
                                "",
                                id="debug-info",
                                className="overflow-auto my-0",
                                style={
                                    "height": "calc(30% - 8px)",
                                    "border": "thin lightgrey solid",
                                },
                            ),
                            myClipboard("debug-info-node", "Node info"),
                            html.Pre(
                                "",
                                id="debug-info-node",
                                className="overflow-auto my-0",
                                style={
                                    "height": "calc(30% - 8px)",
                                    "border": "thin lightgrey solid",
                                },
                            ),
                            myClipboard("debug-info-edge", "Edge info"),
                            html.Pre(
                                "",
                                id="debug-info-edge",
                                className="overflow-auto my-0",
                                style={
                                    "height": "calc(30% - 8px)",
                                    "border": "thin lightgrey solid",
                                },
                            ),
                        ],
                        style={"height": "500px"},
                    ),
                    label="Info",
                    value="tab-2",
                ),
                dcc.Tab(
                    html.Div(
                        [
                            dcc.Dropdown(
                                id="dropdown-layout",
                                options=[
                                    "random",
                                    "grid",
                                    "circle",
                                    "concentric",
                                    "breadthfirst",
                                    "cose",
                                    "cose-bilkent",
                                    "fcose",
                                    "cola",
                                    "euler",
                                    "spread",
                                    "dagre",
                                    "klay",
                                ],
                                value=np.random.choice(
                                    [
                                        # "cose",
                                        "cose-bilkent",
                                        "fcose",
                                        "cola",
                                        "euler",
                                        "spread",
                                    ]
                                ),
                                clearable=False,
                            ),
                        ],
                        style={"height": "500px"},
                    ),
                    label="Layout",
                    value="tab-3",
                ),
            ],
            value="tab-3",
        )
    return html.Div(prod_panels)
