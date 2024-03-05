import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import networkx as nx
from dash import Dash, Input, Output, State, ctx, dcc, html, Patch

from db import database
from formatting import edge_string, node_string
from graph import (
    add_nodes_edges_to_graph,
    cyto_elements_from_graph,
    remove_all_nodes_from_graph,
    remove_lonely_nodes_from_graph,
    remove_nodes_from_graph,
)
from queries import get_actor_relations
from style import default_stylesheet


global g
g = nx.Graph()

pos = nx.spring_layout(g)

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
)

cyto_graph = cyto.Cytoscape(
    id="actor-graph",
    layout={"name": "preset"},
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
                        dbc.Input(id="actor_add", type="text", value="Arletty"),
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
                        dbc.Input(id="actor_rm", type="text", placeholder="Arletty"),
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
                    id="btn-rm-node",
                    color="warning",
                ),
                dbc.Popover(
                    "Remove selected nodes",
                    target="btn-rm-node",
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
                    html.Div([add_remove_actor_panel, filter_panel, info_panel]),
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
    prevent_initial_call=True,
)
def add_actor(nclicks, nsubmit, actor):
    global g
    query_result = get_actor_relations(actor, database)
    g = add_nodes_edges_to_graph(g, query_result)
    elements = cyto_elements_from_graph(g)
    return elements


@app.callback(
    Output(cyto_graph, "stylesheet", allow_duplicate=True),
    Input("actor_filter", "value"),
    prevent_initial_call=True,
)
def generate_stylesheet(filter_input):
    if not filter_input:
        return default_stylesheet
    global g
    filtered_nodes = [node for node in g.nodes if filter_input.lower() in node.lower()]
    filtered_edges = [
        possible_id
        for edge in g.edges
        if any(filtered_node in edge for filtered_node in filtered_nodes)
        for possible_id in (f"{edge[0]}-{edge[1]}", f"{edge[1]}-{edge[0]}")
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


@app.callback(
    Output(cyto_graph, "elements", allow_duplicate=True),
    Input("actor_rm_button", "n_clicks"),
    Input("actor_rm", "n_submit"),
    State("actor_rm", "value"),
    prevent_initial_call=True,
)
def rm_actor(nclicks, nsubmit, actor):
    global g
    g = remove_nodes_from_graph(g, [actor])
    elements = cyto_elements_from_graph(g)
    return elements


@app.callback(
    Output(cyto_graph, "elements", allow_duplicate=True),
    Input("btn-rm-lonely-nodes", "n_clicks"),
    prevent_initial_call=True,
)
def remove_lonely_actors(_):
    global g
    g = remove_lonely_nodes_from_graph(g)
    elements = cyto_elements_from_graph(g)
    return elements


@app.callback(
    Output(cyto_graph, "elements", allow_duplicate=True),
    Input("btn-rm-all-nodes", "n_clicks"),
    prevent_initial_call=True,
)
def remove_all_actors(_):
    global g
    g = remove_all_nodes_from_graph(g)
    elements = cyto_elements_from_graph(g)
    return elements


@app.callback(
    Output(cyto_graph, "elements", allow_duplicate=True),
    Input("btn-rm-node", "n_clicks"),
    State(cyto_graph, "selectedNodeData"),
    prevent_initial_call=True,
)
def rmNodeFromGraph(_, selected_nodes):
    global g
    g = remove_nodes_from_graph(g, [node["id"] for node in selected_nodes])
    elements = cyto_elements_from_graph(g)
    return elements


def get_single_node_info(data_node):
    global g
    nb_connections = g.degree[data_node["id"]]
    # add s at the end of the word if required
    s = "s" if nb_connections > 1 else ""
    return html.P(
        [
            node_string(g.nodes[data_node["id"]]),
            html.Br(),
            f"{nb_connections} connection{s} on the graph",
        ]
    )


def get_single_edge_info(data_edge):
    global g
    common_movies = g.edges[data_edge["source"], data_edge["target"]]["common_movies"]
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
    prevent_initial_call=True,
)
def displayNodeData(data_nodes):
    full_data = []
    for data_element in data_nodes:
        single_element_info = get_single_node_info(data_element)
        full_data.append(single_element_info)
    return html.Div(full_data)


@app.callback(
    Output("edge_info", "children"),
    Input(cyto_graph, "selectedEdgeData"),
    prevent_initial_call=True,
)
def displayEdgeData(data_edges):
    full_data = []
    for data_element in data_edges:
        single_element_info = get_single_edge_info(data_element)
        full_data.append(single_element_info)
    return html.Div(full_data)


if __name__ == "__main__":
    app.run(debug=True)
