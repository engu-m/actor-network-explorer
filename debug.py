from dash import dcc, html

def myPre(id, clipboard_text):
    clipboard = html.Div(
        [
            dcc.Clipboard(id=f"{id}-clipboard", target_id=id),
            clipboard_text,
        ],
        style={"display": "inline-flex"},
    )

    return html.Div(
        [
            clipboard,
            html.Pre(
                "",
                id=id,
                className="overflow-auto my-0",
                style={
                    "height": "calc(30% - 8px)",
                    "border": "thin lightgrey solid",
                },
            ),
        ]
    )



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
                            myPre("debug-info", "Full graph"),
                            myPre("debug-info-node", "Node info"),
                            myPre("debug-info-edge", "Edge info"),
                        ],
                        style={"height": "500px"},
                    ),
                    label="Elements",
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
