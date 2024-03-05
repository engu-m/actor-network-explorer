import networkx as nx
from typing import List


def add_nodes_edges_to_graph(g: nx.Graph, query_result: List) -> nx.Graph:
    for duo_data in query_result:
        actor1 = duo_data["main_actor"]
        actor2 = duo_data["companion_actor"]
        common_movies = duo_data["common_movies"]
        g.add_node(actor1["primaryName"], **actor1)
        g.add_node(actor2["primaryName"], **actor2)
        g.add_edge(
            actor1["primaryName"],
            actor2["primaryName"],
            common_movies=dict(enumerate(common_movies)),
        )
    return g


def remove_nodes_from_graph(g: nx.Graph, nodes) -> nx.Graph:
    """Also removes corresponding edges"""
    g.remove_nodes_from(nodes)
    return g


def remove_lonely_nodes_from_graph(g: nx.Graph) -> nx.Graph:
    """Removes nodes with no neighbors"""
    lonely_nodes = [n for n, d in g.degree if d == 0]
    return remove_nodes_from_graph(g, lonely_nodes)


def remove_all_nodes_from_graph(g: nx.Graph) -> nx.Graph:
    """Removes all nodes"""
    return remove_nodes_from_graph(g, g.nodes)


def cyto_elements_from_graph(g: nx.Graph) -> List:
    pos = nx.spring_layout(g, scale=400)
    graph_degrees = g.degree
    node_elements = [
        {
            "data": {"id": node, "label": node, "degree": graph_degrees[node]},
            "position": {"x": pos[node][0], "y": pos[node][1]},
        }
        for node in g.nodes()
    ]

    edge_elements = [
        {
            "data": {
                "id": f"{node1}-{node2}",
                "source": f"{node1}",
                "target": f"{node2}",
            }
        }
        for (node1, node2) in g.edges()
    ]
    elements = node_elements + edge_elements
    return elements
