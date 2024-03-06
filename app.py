import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import Dash, Input, Output, State, dcc, html, Patch
from dash.exceptions import PreventUpdate

import numpy as np
import json

from db import database
from formatting import edge_string, node_string
from queries import get_actor_relations
from style import default_stylesheet

cyto.load_extra_layouts()


app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
)

cyto_graph = cyto.Cytoscape(
    id="cyto_graph",
    layout={"name": "cose", "animate": False},
    stylesheet=default_stylesheet,
    minZoom=1 / 30,
    maxZoom=30,
    style={"width": "100%", "height": "600px"},
    wheelSensitivity=0.1,
    boxSelectionEnabled=True,
)

add_remove_actor_panel = dbc.Card(
    [
        html.Div(
            [
                dbc.Label("Add actors to the graph", html_for="actor_add"),
                dbc.InputGroup(
                    [
                        dbc.Input(id="actor_add", type="text", value="Hélène Robert"),
                        dbc.Button(id="actor_add_button", children="Add", color="success"),
                    ]
                ),
            ]
        ),
        html.Div(
            [
                dbc.Label("Remove actors from the graph", html_for="actor_rm"),
                dbc.InputGroup(
                    [
                        dbc.Input(id="actor_rm", type="text", placeholder="Hélène Robert"),
                        dbc.Button(id="actor_rm_button", children="Remove", color="danger"),
                    ]
                ),
            ]
        ),
    ],
    body=True,
    className="my-2",
)

filter_panel = dbc.Card(
    [
        html.Div(
            [
                dbc.Label("Filter actors on the graph", html_for="actor_filter"),
                dbc.InputGroup(
                    [
                        dbc.Input(id="actor_filter", type="text", placeholder="Alain Delon"),
                        dbc.InputGroupText(html.I(className="fa-solid fa-filter")),
                    ]
                ),
            ],
        ),
    ],
    body=True,
    className="my-2",
)

info_panel = dbc.Card(
    [
        html.Div(
            [
                dbc.Label("Click on a node/edge to get information"),
                html.Div(id="node_info", children=""),
                html.Div(id="edge_info", children=""),
            ]
        ),
    ],
    body=True,
    className="my-2",
    style={"overflow-y": "scroll", "max-height": "33vh"},
)

info_modal = html.Div(
    [
        dbc.ButtonGroup(
            [
                dbc.Button(
                    children=html.I(
                        className="fa-solid fa-info-circle px-1", style={"color": "black"}
                    ),
                    id="btn-helper-open",
                    color="link",
                    size="lg",
                    className="p-0",
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Actor network explorer")),
                        dbc.ModalBody(
                            [
                                """Visually explore relationships between actors with just a few clicks.
                            
                            Start by searching for an actor and clicking on the "Add" button.
                            Two actors are connected in the graph if they both played in at least one movie.
                            The graph is interactive! You can select and move nodes and edges anywhere.
                            Selecting a node reveals the number of connections the actor currently \
                            has in the graph, as well as basic personal information.
                            Selecting a edge reveals the common movies these two actors have.
                            You can select simultaneously multiple nodes and edges with Ctrl+click or with a rectangle box selection Ctrl+move.
                            Remove actors at any time with one of the three buttons in the top \
                            right-corner, or by specifying his/her name in the right panel then clicking "Remove".
                            When you add an actor, only his/her relationships are shown, \
                            but not the ones of those who played with him/her. \
                            Hence, two people may have played together but share no connection\
                            on the graph if they were not individually added.
                            
                            Disclaimer: the dataset is not exhaustive, some movies/actors may be missing.
                            
                            The code lives """,
                                html.A("here", href="https://github.com/engu-m"),
                                """ (with other cool projects).
                            Datasets downloaded and edited from """,
                                html.A(
                                    "IMDB",
                                    href="https://developer.imdb.com/non-commercial-datasets/",
                                ),
                                """.
                            Database stored in MongoDB.
                            Interface using Dash, Dash Bootstrap Components and Dash Cytoscape
                            Deployed with [...]

                            © Enguerrand Monard, 2024""",
                            ],
                            style={"white-space": "pre-line"},
                            # Style pre-line: Sequences of white space are collapsed
                            # Lines are broken at newline characters, at <br>, and as necessary to fill line boxes.
                        ),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Close", id="btn-helper-close", className="ms-auto", n_clicks=0
                            )
                        ),
                    ],
                    id="modal",
                    is_open=False,
                    size="lg",
                ),
            ],
        )
    ],
    className="helper-container position-absolute m-1",
    style={
        "top": "0px",
        "left": "0px",
    },
)


def modebar_button(btn_id, fa_icon, btn_color, popover):
    button = dbc.Button(
        children=html.I(className=f"fa-solid fa-{fa_icon} px-1", style={"color": "white"}),
        id=btn_id,
        color=btn_color,
    )
    popover = dbc.Popover(
        popover,
        target=btn_id,
        body=True,
        trigger="hover",
        placement="top",
    )
    return button, popover


modebar = html.Div(
    [
        dbc.ButtonGroup(
            [
                *modebar_button("btn-rm-lonely-nodes", "broom", "info", "Remove lonely nodes"),
                *modebar_button(
                    "btn-rm-selected-nodes", "trash-can", "warning", "Remove selected nodes"
                ),
                *modebar_button("btn-rm-all-nodes", "times", "danger", "Remove ALL nodes"),
            ],
            size="sm",
        )
    ],
    className="modebar-container position-absolute m-1 border rounded",
    style={
        "top": "0px",
        "right": "0px",
    },
)

alerts = [
    dbc.Alert(id="alert-add-success", is_open=False, duration=4000, color="success"),
    dbc.Alert(id="alert-rm-success", is_open=False, duration=4000, color="success"),
    dbc.Alert(id="alert-add-none", is_open=False, duration=4000, color="warning"),
    dbc.Alert(id="alert-rm-none", is_open=False, duration=4000, color="warning"),
    dbc.Alert(id="alert-add-fail", is_open=False, duration=4000, color="danger"),
    dbc.Alert(id="alert-rm-fail", is_open=False, duration=4000, color="danger"),
]

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                html.Div(
                    alerts,
                    style={"top": "0px", "right": "0px", "width": "25%", "z-index": 100},
                    className="position-absolute m-1",
                ),
                dbc.Col(
                    html.Div(
                        [
                            dcc.Loading(cyto_graph),
                            modebar,
                            info_modal,
                        ],
                        className="border border-dark rounded m-4 position-relative",
                    ),
                    md=9,
                ),
                dbc.Col(
                    dcc.Tabs(
                        [
                            dcc.Tab(
                                html.Div([add_remove_actor_panel, filter_panel, info_panel]),
                                label="Update",
                                value="tab-1",
                            ),
                            dcc.Tab(
                                html.Div(
                                    [
                                        dcc.Dropdown(
                                            id="dropdown-layout",
                                            options=[
                                                "fcose",
                                                "cose-bilkent",
                                                "cola",
                                                "euler",
                                                "spread",
                                                "grid",
                                                "random",
                                            ],
                                            value=np.random.choice(
                                                [
                                                    # "cose",
                                                    "cose-bilkent",
                                                    "fcose",
                                                    # "cola",
                                                    # "euler",
                                                    # "spread",
                                                ]
                                            ),
                                            clearable=False,
                                        ),
                                        html.Pre(
                                            "",
                                            id="debug-info",
                                            style={
                                                "overflow-y": "scroll",
                                                "height": "calc(33% - 5px)",
                                                "border": "thin lightgrey solid",
                                            },
                                        ),
                                        html.Pre(
                                            "",
                                            id="debug-info-node",
                                            style={
                                                "overflow-y": "scroll",
                                                "height": "calc(33% - 5px)",
                                                "border": "thin lightgrey solid",
                                            },
                                        ),
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
                                label="Debug",
                                value="tab-2",
                            ),
                        ],
                        value="tab-2",
                    ),
                    md=3,
                ),
            ],
            align="center",
        ),
    ],
    fluid=True,
)


@app.callback(
    Output("modal", "is_open"),
    Input("btn-helper-open", "n_clicks"),
    Input("btn-helper-close", "n_clicks"),
    State("modal", "is_open"),
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("cyto_graph", "elements", allow_duplicate=True),
    Input("actor_add_button", "n_clicks"),
    Input("actor_add", "n_submit"),
    State("actor_add", "value"),
    State("cyto_graph", "elements"),
    prevent_initial_call="initial_duplicate",
)
def add_actor(nclicks, nsubmit, actor, elements):
    query_result = get_actor_relations(actor, database)

    # make elements iterable if None, e.g. during init
    if elements is None:
        elements = []
    for duo_data in query_result:
        # sort actors by alphabetical order
        actor1, actor2 = sorted(
            [duo_data["main_actor"], duo_data["companion_actor"]], key=lambda x: x["primaryName"]
        )

        # add actors if not already there
        for actor in (actor1, actor2):
            actor_id = actor["primaryName"]
            if actor_id not in [ele["data"]["id"] for ele in elements]:
                node_info = {
                    "id": actor["primaryName"],
                    "label": actor["primaryName"],
                }
                node_info.update(actor)
                actor_to_add = {"data": node_info}
                elements.append(actor_to_add)

        # add edge if not already there
        common_movies = duo_data["common_movies"]
        element_to_add = {
            "data": {
                "id": f"{actor1['primaryName']} , {actor2['primaryName']}",
                "source": f"{actor1['primaryName']}",
                "target": f"{actor2['primaryName']}",
                "common_movies": dict(enumerate(common_movies)),
            }
        }
        if element_to_add not in elements:
            elements.append(element_to_add)

    return elements


@app.callback(
    Output("cyto_graph", "elements", allow_duplicate=True),
    Input("btn-rm-all-nodes", "n_clicks"),
    prevent_initial_call=True,
)
def remove_all_nodes(_):
    return []


def rm_node_ids(ids_to_remove, elements):
    """Also removes obsolete edges"""
    for ele in elements[:]:  # make a copy of elements
        if ele["data"]["id"] in ids_to_remove:
            # remove node
            elements.remove(ele)
        if ele["data"].get("source") in ids_to_remove or ele["data"].get("target") in ids_to_remove:
            elements.remove(ele)
    return elements


@app.callback(
    Output("cyto_graph", "elements", allow_duplicate=True),
    Input("actor_rm_button", "n_clicks"),
    Input("actor_rm", "n_submit"),
    State("actor_rm", "value"),
    State("cyto_graph", "elements"),
    prevent_initial_call=True,
)
def rm_actor(nclicks, nsubmit, actor, elements):
    """Pressing the red Remove btn or pressing the key enter when
    the input is in focus removes the actor from the graph"""
    if actor is None:
        raise PreventUpdate
    return rm_node_ids([actor.title()], elements)


@app.callback(
    Output("cyto_graph", "elements", allow_duplicate=True),
    Input("btn-rm-selected-nodes", "n_clicks"),
    State("cyto_graph", "selectedNodeData"),
    State("cyto_graph", "elements"),
    prevent_initial_call=True,
)
def rm_selected_nodes(_, selected_nodes, elements):
    if not selected_nodes:
        raise PreventUpdate
    ids_to_remove = [node["id"] for node in selected_nodes]
    return rm_node_ids(ids_to_remove, elements)


@app.callback(
    Output("cyto_graph", "stylesheet", allow_duplicate=True),
    Input("actor_filter", "value"),
    State("cyto_graph", "elements"),
    prevent_initial_call=True,
)
def generate_filtered_stylesheet(filter_input, elements):
    if not filter_input:
        return default_stylesheet
    nodes = get_nodes(elements)
    edges = get_edges(elements)
    filtered_nodes = [
        node["data"]["id"] for node in nodes if filter_input.lower() in node["data"]["id"].lower()
    ]
    filtered_edges = [
        edge["data"]["id"]
        for edge in edges
        if any(
            filtered_node in (edge["data"]["source"], edge["data"]["target"])
            for filtered_node in filtered_nodes
        )
    ]
    stylesheet = default_stylesheet.copy()
    off_stylesheet = [
        {"selector": "node", "style": {"opacity": 0.3}},
        {
            "selector": "edge",
            "style": {
                "opacity": 0.2,
            },
        },
    ]
    on_stylesheet_nodes = [
        {"selector": f"node[id = '{node_id}']", "style": {"opacity": 1, "z-index": 10}}
        for node_id in filtered_nodes
    ]
    on_stylesheet_edges = [
        {"selector": f"edge[id = '{edge_id}']", "style": {"opacity": 1, "z-index": 9}}
        for edge_id in filtered_edges
    ]
    stylesheet = stylesheet + off_stylesheet + on_stylesheet_nodes + on_stylesheet_edges

    return stylesheet


def get_nodes(elements):
    return list(filter(lambda x: not x["data"].get("source"), elements))


def get_edges(elements):
    return list(filter(lambda x: x["data"].get("source"), elements))


def get_degrees(elements):
    nodes = get_nodes(elements)
    edges = get_edges(elements)

    # enforce uniqueness
    node_ids = set(map(lambda x: x["data"]["id"], nodes))
    # edge (a,b) is the same as (b,a)
    edges_unique = set(
        {frozenset({edge["data"]["source"], edge["data"]["target"]}) for edge in edges}
    )

    # initialise degree with 0
    degrees = dict(zip(node_ids, len(node_ids) * [0]))
    for edge in edges_unique:
        src, tgt = edge
        degrees[src] += 1
        degrees[tgt] += 1
    return degrees


@app.callback(
    Output("cyto_graph", "elements", allow_duplicate=True),
    Input("btn-rm-lonely-nodes", "n_clicks"),
    State("cyto_graph", "elements"),
    prevent_initial_call=True,
)
def remove_lonely_actors(_, elements):
    degrees = get_degrees(elements)
    lonely_nodes_ids = [id for id, deg in degrees.items() if deg == 0]
    return rm_node_ids(lonely_nodes_ids, elements)


def get_single_node_info(data_node, elements):
    degrees = get_degrees(elements)
    nb_connections = degrees[data_node["id"]]
    # add s at the end of the word if required
    s = "s" if nb_connections > 1 else ""
    return html.P(
        [
            node_string(data_node),
            html.Br(),
            f"{nb_connections} connection{s} on the graph",
        ]
    )


def get_single_edge_info(data_edge, elements):
    edges = get_edges(elements)
    correct_edge = next(filter(lambda x: x["data"]["id"] == data_edge["id"], edges))
    common_movies = correct_edge["data"]["common_movies"]
    basic_str = edge_string(common_movies.values())
    lines = basic_str.split("\n")
    html_lines = html.Ul([html.Li(line) for line in lines[1:]])
    return html.P(
        [
            f"{data_edge['source']} <---> {data_edge['target']}",
            html.Br(),
            data_edge["id"],
            html.Br(),
            lines[0],
            html.Br(),
            html_lines,
        ]
    )


@app.callback(
    Output("node_info", "children"),
    Input("cyto_graph", "selectedNodeData"),
    State("cyto_graph", "elements"),
    prevent_initial_call=True,
)
def displayNodeData(data_nodes, elements):
    full_data = []
    for data_element in data_nodes:
        single_element_info = get_single_node_info(data_element, elements)
        full_data.append(single_element_info)
    return html.Div(full_data)


@app.callback(
    Output("edge_info", "children"),
    Input("cyto_graph", "selectedEdgeData"),
    State("cyto_graph", "elements"),
    prevent_initial_call=True,
)
def displayEdgeData(data_edges, elements):
    full_data = []
    for data_element in data_edges:
        single_element_info = get_single_edge_info(data_element, elements)
        full_data.append(single_element_info)
    return html.Div(full_data)


@app.callback(Output("cyto_graph", "layout"), Input("dropdown-layout", "value"))
def update_cytoscape_layout(layout):
    patched_layout = Patch()
    patched_layout["name"] = layout
    return patched_layout


@app.callback(Output("debug-info", "children"), Input("cyto_graph", "elements"))
def update_debug_panel(elements):
    return json.dumps(elements, indent=2, ensure_ascii=False)


@app.callback(Output("debug-info-node", "children"), Input("cyto_graph", "selectedNodeData"))
def update_debug_panel_node(nodes_data):
    return json.dumps(nodes_data, indent=2, ensure_ascii=False)


@app.callback(Output("debug-info-edge", "children"), Input("cyto_graph", "selectedEdgeData"))
def update_debug_panel_edge(edges_data):
    return json.dumps(edges_data, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    app.run(debug=True)
