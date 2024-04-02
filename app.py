import json
import os

import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import dotenv
from dash import Dash, Input, Output, Patch, State, dcc, html, ctx

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
    style={"width": "clamp(50px, 100%, 2000px)", "height": "clamp(200px, 90vh, 1000px)"},
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


def myAlert(message, color):
    duration = 2000 if color == "warning" else 4000
    return dbc.Alert(message, is_open=True, color=color, fade=True, duration=duration)


alerts = []


app.layout = dbc.Container(
    [
        dbc.Row(
            [
                html.Div(
                    alerts,
                    style={"width": "clamp(200px,33vw,500px)", "z-index": "1200"},
                    className="position-fixed top-0 end-0 m-1",
                    id="alert-container",
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


def rm_node_ids(ids_to_remove, elements, alert_container):
    """Also removes obsolete edges"""
    alert_accumulator = []
    previous_elements_length = len(elements)
    for ele in elements[:]:  # make a copy of elements
        if ele["data"]["id"] in ids_to_remove:
            # generate alert
            alert_rm_node = myAlert(
                f"Successfully removed {ele['data']['id']} from the network.", "success"
            )
            alert_accumulator.append(alert_rm_node)
            # remove node
            elements.remove(ele)
        if ele["data"].get("source") in ids_to_remove or ele["data"].get("target") in ids_to_remove:
            # remove edge
            elements.remove(ele)

    if len(alert_accumulator) > 8:
        # prevent display of too many alerts at once
        alert_rm_actors_summary = myAlert(
            f"Successfully removed {len(alert_accumulator)} actors from the graph.", "success"
        )
        alert_container.append(alert_rm_actors_summary)
    else:
        # normal display of all alerts
        alert_container += alert_accumulator

    if previous_elements_length == len(elements):
        # no actor was removed
        if len(ids_to_remove) == 0:
            one_or_many_message = ""
        elif len(ids_to_remove) == 1:
            one_or_many_message = f" Make sure {ids_to_remove[0]} is in the network."
        else:
            one_or_many_message = (
                f" Make sure at least one of {', '.join(ids_to_remove)} is in the network."
            )
        alert_no_removal = myAlert(
            f"No actor was removed from the network.{one_or_many_message}",
            "warning",
        )
        alert_container.append(alert_no_removal)

    return elements, alert_container


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
    Output("alert-container", "children", allow_duplicate=True),
    Input("actor_add_button", "n_clicks"),
    Input("actor_add", "n_submit"),
    State("actor_add", "value"),
    State("cyto_graph", "elements"),
    State("alert-container", "children"),
    prevent_initial_call="initial_duplicate" if DEBUG else True,
)
def add_actor(nclicks, nsubmit, actor, elements, alert_container):
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
            actor_not_found_alert = myAlert(f"{actor} not found in the database.", "danger")
            alert_container.append(actor_not_found_alert)
            return elements, alert_container

        # solo actor
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
            alert_solo_node = myAlert(f"{actor} added, did not play with anyone else.", "warning")
            alert_container.append(alert_solo_node)
            return elements, alert_container

    for duo_data in query_result:
        # sort actors by alphabetical order
        actor1, actor2 = sorted(
            [duo_data["main_actor"], duo_data["companion_actor"]], key=lambda x: x["primaryName"]
        )

        # add actors if not already there
        for actor_data in (actor1, actor2):
            actor_id = actor_data["primaryName"]
            if actor_id not in [ele["data"]["id"] for ele in elements]:
                node_info = {
                    "id": actor_data["primaryName"],
                    "label": actor_data["primaryName"],
                }
                node_info.update(actor_data)
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

    alert_added_actor = myAlert(
        f"{actor} successfully added. {len(query_result)} connections added, if not already there.",
        "success",
    )
    alert_container.append(alert_added_actor)
    return elements, alert_container


@app.callback(
    Output("cyto_graph", "elements", allow_duplicate=True),
    Output("alert-container", "children", allow_duplicate=True),
    Input("btn-rm-all-nodes", "n_clicks"),
    State("alert-container", "children"),
    prevent_initial_call=True,
)
def remove_all_nodes(_, alert_container):
    alert_rm_all_actors = myAlert("Successfully removed all actors", "success")
    alert_container.append(alert_rm_all_actors)
    return [], alert_container


@app.callback(
    Output("cyto_graph", "elements", allow_duplicate=True),
    Output("alert-container", "children", allow_duplicate=True),
    Input("actor_rm_button", "n_clicks"),
    Input("actor_rm", "n_submit"),
    State("actor_rm", "value"),
    State("cyto_graph", "elements"),
    State("alert-container", "children"),
    prevent_initial_call=True,
)
def rm_actor_from_text(nclicks, nsubmit, actor, elements, alert_container):
    """Clicking the red Remove btn or pressing the key enter when
    the input is in focus removes the actor from the graph"""
    actor_list = [actor] if actor is not None else []
    return rm_node_ids(actor_list, elements, alert_container)


@app.callback(
    Output("cyto_graph", "elements", allow_duplicate=True),
    Output("alert-container", "children", allow_duplicate=True),
    Input("btn-rm-selected-nodes", "n_clicks"),
    State("cyto_graph", "selectedNodeData"),
    State("cyto_graph", "elements"),
    State("alert-container", "children"),
    prevent_initial_call=True,
)
def rm_selected_nodes(_, selected_nodes, elements, alert_container):
    if not selected_nodes:
        ids_to_remove = []
        alert_no_selected_actor = myAlert(
            "No actor was removed from the network. Select a node before hitting the button.",
            "warning",
        )
        alert_container.append(alert_no_selected_actor)
        return elements, alert_container
    else:
        ids_to_remove = [node["id"] for node in selected_nodes]
        return rm_node_ids(ids_to_remove, elements, alert_container)


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
    Output("alert-container", "children", allow_duplicate=True),
    Input("btn-add-random-actor", "n_clicks"),
    State("cyto_graph", "elements"),
    State("alert-container", "children"),
    prevent_initial_call=True,
)
def add_random_actor(_, elements, alert_container):
    random_actor = get_random_actor(database)
    elements, alert_container = add_actor(None, None, random_actor, elements, alert_container)
    return elements, alert_container


@app.callback(
    Output("cyto_graph", "elements", allow_duplicate=True),
    Output("alert-container", "children", allow_duplicate=True),
    Input("btn-expand-seleted-nodes", "n_clicks"),
    State("cyto_graph", "selectedNodeData"),
    State("cyto_graph", "elements"),
    State("alert-container", "children"),
    prevent_initial_call=True,
)
def expand_selected_actors(_, data_nodes, elements, alert_container):
    # no actor was selected
    if not data_nodes:
        alert_no_selected_actor = myAlert(
            "No actor was added to the network. Select a node before hitting the button.", "warning"
        )
        alert_container.append(alert_no_selected_actor)
        return elements, alert_container

    # else add all selected actors
    for data_element in data_nodes:
        actor = data_element["id"]
        elements, alert_container = add_actor(None, None, actor, elements, alert_container)
    return elements, alert_container


@app.callback(
    Output("cyto_graph", "elements", allow_duplicate=True),
    Output("alert-container", "children", allow_duplicate=True),
    Input("btn-rm-lonely-nodes", "n_clicks"),
    State("cyto_graph", "elements"),
    State("alert-container", "children"),
    prevent_initial_call=True,
)
def remove_lonely_actors(_, elements, alert_container):
    degrees = get_degrees(elements)
    lonely_nodes_ids = [id for id, deg in degrees.items() if deg == 0]
    return rm_node_ids(lonely_nodes_ids, elements, alert_container)


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
