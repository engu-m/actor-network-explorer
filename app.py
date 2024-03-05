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
    id="actor-graph",
    layout={"name": "preset", "fit": True, "animate": False},
    stylesheet=default_stylesheet,
    minZoom=1 / 30,
    maxZoom=30,
    style={"width": "100%", "height": "600px"},
    wheelSensitivity=0.1,
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

modebar = html.Div(
    [
        dbc.ButtonGroup(
            [
                dbc.Button(
                    children=html.I(className="fa-solid fa-broom px-1", style={"color": "white"}),
                    id="btn-rm-lonely-nodes",
                    color="info",
                ),
                dbc.Popover(
                    "Remove lonely nodes",
                    target="btn-rm-lonely-nodes",
                    body=True,
                    trigger="hover",
                    placement="top",
                ),
                dbc.Button(
                    children=html.I(
                        className="fa-solid fa-trash-can px-1", style={"color": "white"}
                    ),
                    id="btn-rm-selected-nodes",
                    color="warning",
                ),
                dbc.Popover(
                    "Remove selected nodes",
                    target="btn-rm-selected-nodes",
                    body=True,
                    trigger="hover",
                    placement="top",
                ),
                dbc.Button(
                    children=html.I(className="fa-solid fa-times px-1", style={"color": "white"}),
                    id="btn-rm-all-nodes",
                    color="danger",
                ),
                dbc.Popover(
                    "Remove ALL nodes",
                    target="btn-rm-all-nodes",
                    body=True,
                    trigger="hover",
                    placement="top",
                ),
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

app.layout = dbc.Container(
    [
        html.H1("Actor graph"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            dcc.Loading(cyto_graph),
                            modebar,
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
    Output(cyto_graph, "elements", allow_duplicate=True),
    Input("actor_add_button", "n_clicks"),
    Input("actor_add", "n_submit"),
    State("actor_add", "value"),
    State(cyto_graph, "elements"),
    # prevent_initial_call="initial_duplicate",
    prevent_initial_call=True,
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
    Output(cyto_graph, "elements", allow_duplicate=True),
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
    Output(cyto_graph, "elements", allow_duplicate=True),
    Input("actor_rm_button", "n_clicks"),
    Input("actor_rm", "n_submit"),
    State("actor_rm", "value"),
    State(cyto_graph, "elements"),
    prevent_initial_call=True,
)
def rm_actor(nclicks, nsubmit, actor, elements):
    """Pressing the red Remove btn or pressing the key enter when
    the input is in focus removes the actor from the graph"""
    if actor is None:
        raise PreventUpdate
    return rm_node_ids([actor], elements)


@app.callback(
    Output(cyto_graph, "elements", allow_duplicate=True),
    Input("btn-rm-selected-nodes", "n_clicks"),
    State(cyto_graph, "selectedNodeData"),
    State(cyto_graph, "elements"),
    prevent_initial_call=True,
)
def rm_selected_nodes(_, selected_nodes, elements):
    if not selected_nodes:
        raise PreventUpdate
    ids_to_remove = [node["id"] for node in selected_nodes]
    return rm_node_ids(ids_to_remove, elements)


@app.callback(
    Output(cyto_graph, "stylesheet", allow_duplicate=True),
    Input("actor_filter", "value"),
    State(cyto_graph, "elements"),
    prevent_initial_call=True,
)
def generate_filtered_stylesheet(filter_input, elements):
    # TODO: update z index as well so that filtered actors are easier to select
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
        {"selector": f"node[id = '{node_id}']", "style": {"opacity": 1}}
        for node_id in filtered_nodes
    ]
    on_stylesheet_edges = [
        {"selector": f"edge[id = '{edge_id}']", "style": {"opacity": 1}}
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
    Output(cyto_graph, "elements", allow_duplicate=True),
    Input("btn-rm-lonely-nodes", "n_clicks"),
    State(cyto_graph, "elements"),
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
    Input(cyto_graph, "selectedNodeData"),
    State(cyto_graph, "elements"),
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
    Input(cyto_graph, "selectedEdgeData"),
    State(cyto_graph, "elements"),
    prevent_initial_call=True,
)
def displayEdgeData(data_edges, elements):
    full_data = []
    for data_element in data_edges:
        single_element_info = get_single_edge_info(data_element, elements)
        full_data.append(single_element_info)
    return html.Div(full_data)


@app.callback(Output(cyto_graph, "layout"), Input("dropdown-layout", "value"))
def update_cytoscape_layout(layout):
    return {"name": layout}


@app.callback(Output("debug-info", "children"), Input(cyto_graph, "elements"))
def update_debug_panel(elements):
    return json.dumps(elements, indent=2, ensure_ascii=False)


@app.callback(Output("debug-info-node", "children"), Input(cyto_graph, "selectedNodeData"))
def update_debug_panel_node(nodes_data):
    return json.dumps(nodes_data, indent=2, ensure_ascii=False)


@app.callback(Output("debug-info-edge", "children"), Input(cyto_graph, "selectedEdgeData"))
def update_debug_panel_edge(edges_data):
    return json.dumps(edges_data, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    app.run(debug=True)
