import json
import os

import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import dotenv
from dash import Dash, Input, Output, Patch, State, dcc, html, ctx
from dash.exceptions import PreventUpdate

from db import database
from debug import tabs, built_layouts, layout_filters
from queries import get_actor_info_basic, get_actor_relations, get_random_actor
from style import default_stylesheet
from utils import (
    get_degrees,
    get_edges,
    get_nodes,
    get_single_edge_info,
    get_single_node_info,
    rm_node_ids,
)

dotenv.load_dotenv(override=True)

DEBUG = bool(os.getenv("DEBUG"))

cyto.load_extra_layouts()


app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
)
app.title = "Co-stardom network"
server = app.server

cyto_graph = cyto.Cytoscape(
    id="cyto_graph",
    layout={
        "name": "fcose",
        "animate": True,
        "fit": True,
        "padding": 20,
        "quality": "proof",
        "nodeDimensionsIncludeLabels": False,
        "samplingType": False,
        "sampleSize": 25,
        "nodeSeparation": 75,
        "nodeRepulsion": 6000,
        "edgeElasticity": 0.45,
        "idealEdgeLength": 50,
        "gravityRange": 1.9,
        "gravity": 0.25,
        "initialEnergyOnIncremental": 0.3,
    },
    stylesheet=default_stylesheet,
    minZoom=1 / 30,
    maxZoom=30,
    style={"width": "100%", "height": "max(600px,90vh)"},
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
                        dbc.Input(id="actor_add", type="text", value="Will Smith"),
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
                        dbc.Input(id="actor_rm", type="text", placeholder="Will Smith"),
                        dbc.Button(id="actor_rm_button", children="Remove", color="danger"),
                    ]
                ),
            ]
        ),
    ],
    body=True,
    className="my-2",
)


def modebar_button(btn_id, fa_icon, btn_color, popover, btn_className=""):
    button = dbc.Button(
        children=html.I(className=f"fa-solid fa-{fa_icon} px-1", style={"color": "white"}),
        id=btn_id,
        color=btn_color,
        className=btn_className,
    )
    popover = dbc.Popover(
        popover,
        target=btn_id,
        body=True,
        trigger="hover",
        placement="top",
    )
    return button, popover


filter_panel = dbc.Card(
    [
        html.Div(
            [
                dbc.Label("Filter actors on the graph", html_for="actor_filter"),
                dbc.InputGroup(
                    [
                        dbc.Input(id="actor_filter", type="text", placeholder="Angelina Jolie"),
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
                dbc.Label("Select an actor/relationship to get information"),
                html.Div(id="node_info", children=""),
                html.Div(id="edge_info", children=""),
            ]
        ),
    ],
    body=True,
    className="my-2 overflow-auto",
    style={"max-height": "33vh"},
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
                        dbc.ModalHeader(dbc.ModalTitle("Co-stardom network")),
                        dbc.ModalBody(
                            html.Div(
                                [
                                    html.P("Works best on Desktop"),
                                    html.H3("Adding actors"),
                                    html.P(
                                        [
                                            "Either search for your favorite actor in the appropriate input field and click ",
                                            dbc.Button("Add", color="success", className="btn-sm"),
                                            ", or hit ",
                                            modebar_button("", "dice", "dark", "", "btn-sm")[0],
                                            " to add a random actor. To add the relationships of an actor already present on the network, select his node and hit ",
                                            modebar_button(
                                                "", "user-plus", "success", "", "btn-sm"
                                            )[0],
                                            ".",
                                        ]
                                    ),
                                    html.H3("Selecting actors/relationships"),
                                    dcc.Markdown(
                                        """You can click and drag nodes and edges anywhere. 
A selected node will appear in red and a selected edge in black. 
Selecting a node reveals the number of connections the actor currently has in the graph, 
as well as basic personal information on the actor/actress. 
Selecting an edge reveals the common movies these two actors have in the bottom right panel. 
You can select simultaneously multiple nodes and edges with `Ctrl/Cmd+click` or with a click and drag rectangle box selection while holding `Ctrl/Cmd`."""
                                    ),
                                    html.H3("Removing actors"),
                                    html.P(
                                        [
                                            "Hit ",
                                            modebar_button("", "times", "danger", "", "btn-sm")[0],
                                            " to remove everbody from the graph. ",
                                            "Hit ",
                                            modebar_button(
                                                "", "trash-can", "warning", "", "btn-sm"
                                            )[0],
                                            " to remove the selected actors (those in red, default none). ",
                                            "Hit ",
                                            modebar_button("", "broom", "info", "", "btn-sm")[0],
                                            " to clear actors with no relationships in the network. ",
                                            "Alternatively, you can type the actor's name in the appropriate input field and hit ",
                                            dbc.Button(
                                                "Remove", color="danger", className="btn-sm"
                                            ),
                                            ".",
                                        ]
                                    ),
                                    html.P(
                                        [
                                            "Instead of removing an actor, you can filter the view more easily with the filtering text input ",
                                            dbc.Button(
                                                children=html.I(
                                                    className="fa-solid fa-filter px-1"
                                                ),
                                                color="light",
                                                className="btn-sm",
                                            ),
                                            ".",
                                        ]
                                    ),
                                    html.H3("Credit"),
                                    dcc.Markdown(
                                        """Disclaimer: the dataset is not exhaustive, some movies/actors may be missing.

The code lives [on my github](https://github.com/engu-m) (with other cool projects).
Datasets downloaded and edited from [IMDb](https://developer.imdb.com/non-commercial-datasets/).
Database stored in [MongoDB](https://https://www.mongodb.com/).
Interface using [Dash](https://dash.plotly.com/), [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) and [Dash Cytoscape](https://dash.plotly.com/cytoscape).
Favicon: [Share icons created by Smashicons - Flaticon](https://www.flaticon.com/free-icons/share).
Deployed with [Koyeb](https://koyeb.com).

---

© Enguerrand Monard, 2024""",
                                        style={"white-space": "pre-line"},
                                    ),
                                ]
                            ),
                        ),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Close", id="btn-helper-close", className="ms-auto", n_clicks=0
                            )
                        ),
                    ],
                    id="modal",
                    is_open=not DEBUG,
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


modebar = html.Div(
    [
        dbc.ButtonGroup(
            [
                *modebar_button("btn-add-random-actor", "dice", "dark", "Add random actor"),
                *modebar_button(
                    "btn-expand-seleted-nodes", "user-plus", "success", "Expand selected nodes"
                ),
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

app.layout = dbc.Container(
    [
        dbc.Row(
            [
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
                    html.Div(
                        tabs([add_remove_actor_panel, filter_panel, info_panel], debug=DEBUG),
                        className="mt-4 overflow-auto",
                    ),
                    md="3",
                ),
            ],
            align="start",
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
    prevent_initial_call="initial_duplicate" if DEBUG else True,
)
def add_actor(nclicks, nsubmit, actor, elements):
    """Clicking the green Add btn or pressing the key enter when
    the input is in focus adds the actor to the graph"""
    query_result = get_actor_relations(actor, database)

    # make elements iterable if None, e.g. during init
    if elements is None:
        elements = []

    # actor did not play with anyone
    if not query_result:
        # try to retrieve basic info on actor
        actor_info = get_actor_info_basic(actor, database)

        # check actor exists
        if not actor_info:
            # actor not found
            return elements

        for actor_entry in actor_info:
            actor_id = actor_entry["primaryName"]
            if actor_id not in [ele["data"]["id"] for ele in elements]:
                node_info = {
                    "id": actor_entry["primaryName"],
                    "label": actor_entry["primaryName"],
                }
                node_info.update(actor_entry)
                actor_to_add = {"data": node_info}
                elements.append(actor_to_add)
            return elements

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


@app.callback(
    Output("cyto_graph", "elements", allow_duplicate=True),
    Input("actor_rm_button", "n_clicks"),
    Input("actor_rm", "n_submit"),
    State("actor_rm", "value"),
    State("cyto_graph", "elements"),
    prevent_initial_call=True,
)
def rm_actor(nclicks, nsubmit, actor, elements):
    """Clicking the red Remove btn or pressing the key enter when
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


@app.callback(
    Output("cyto_graph", "elements", allow_duplicate=True),
    Input("btn-add-random-actor", "n_clicks"),
    State("cyto_graph", "elements"),
    prevent_initial_call=True,
)
def add_random_actor(_, elements):
    random_actor = get_random_actor(database)
    elements = add_actor(None, None, random_actor, elements)
    return elements


@app.callback(
    Output("cyto_graph", "elements", allow_duplicate=True),
    Input("btn-expand-seleted-nodes", "n_clicks"),
    State("cyto_graph", "selectedNodeData"),
    State("cyto_graph", "elements"),
    prevent_initial_call=True,
)
def expand_selected_actors(_, data_nodes, elements):
    for data_element in data_nodes:
        actor = data_element["id"]
        elements = add_actor(None, None, actor, elements)
    return elements


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


generic_parameters = ["name", "animate", "animationDuration", "fit", "padding"]


@app.callback(
    Output("layout_specific_parameters", "children"), Input("layout-generic-name", "value")
)
def update_cytoscape_layout_name(name):
    additional_parameters = built_layouts.get(name, html.Div())
    return additional_parameters


def update_cytoscape_layout_generic(**dico):
    changed_component_id = ctx.triggered_id

    # when app init, update everything
    if changed_component_id is None:
        return dico

    # else update only changed property
    changed_property = changed_component_id.split("-")[-1]
    layout_dict = Patch()
    layout_dict[changed_property] = dico[changed_property]

    return layout_dict


_ = app.callback(
    Output(cyto_graph, "layout", allow_duplicate=True),
    inputs={param: Input(f"layout-generic-{param}", "value") for param in generic_parameters},
    prevent_initial_call="initial_duplicate",
)(update_cytoscape_layout_generic)


for layout_name in layout_filters.keys():
    app.callback(
        Output(cyto_graph, "layout", allow_duplicate=True),
        inputs={
            param: Input(f"layout-{layout_name}-{param}", "value")
            for param in layout_filters[f"{layout_name}"]
        },
        prevent_initial_call="initial_duplicate",
    )(update_cytoscape_layout_generic)


@app.callback(
    Output("copy_paste_layout", "content"),
    Input("copy_paste_layout", "n_clicks"),
    State(cyto_graph, "layout"),
)
def custom_copy(_, layout_dict):
    return str(layout_dict)


def update_debug_panel(elements):
    return json.dumps(elements, indent=2, ensure_ascii=False)


info_debug_func = app.callback(Output("debug-info", "children"), Input(cyto_graph, "elements"))(
    update_debug_panel
)
node_debug_func = app.callback(
    Output("debug-info-node", "children"), Input(cyto_graph, "selectedNodeData")
)(update_debug_panel)
edge_debug_func = app.callback(
    Output("debug-info-edge", "children"), Input(cyto_graph, "selectedEdgeData")
)(update_debug_panel)


if __name__ == "__main__":
    app.run(debug=DEBUG)
