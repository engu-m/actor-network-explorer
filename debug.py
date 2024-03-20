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
                            "Full graph",
                            html.Pre(
                                "",
                                id="debug-info",
                                style={
                                    "overflow-y": "scroll",
                                    "height": "calc(33% - 5px)",
                                    "border": "thin lightgrey solid",
                                },
                            ),
                            "Node info",
                            html.Pre(
                                "",
                                id="debug-info-node",
                                style={
                                    "overflow-y": "scroll",
                                    "height": "calc(33% - 5px)",
                                    "border": "thin lightgrey solid",
                                },
                            ),
                            "Edge info",
                            html.Pre(
                                "",
                                id="debug-info-edge",
                                style={
                                    "overflow-y": "scroll",
                                    "height": "calc(33% - 5px)",
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
