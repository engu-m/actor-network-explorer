from dash import html

from formatting import edge_string, node_string


def rm_node_ids(ids_to_remove, elements):
    """Also removes obsolete edges"""
    for ele in elements[:]:  # make a copy of elements
        if ele["data"]["id"] in ids_to_remove:
            # remove node
            elements.remove(ele)
        if ele["data"].get("source") in ids_to_remove or ele["data"].get("target") in ids_to_remove:
            elements.remove(ele)
    return elements


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
            lines[0],
            html.Br(),
            html_lines,
        ]
    )
