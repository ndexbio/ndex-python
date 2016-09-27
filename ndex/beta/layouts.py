import networkx as nx
import random

def _create_edge_tuples(attractor, target):
    return [(a,t) for a in attractor for t in target]

def _add_attractor(network, attracted_nodes, attractor_name):
    attractor_list =[]
    attractor_list.append(network.add_new_node(name=attractor_name))
    for attractor in attractor_list:
        for node in attracted_nodes:
            network.add_edge(node, attractor, interaction='in-complex-with')

            #network.add_edge_between(node, attractor, interaction='in-complex-with')
    #edge_tuples = _create_edge_tuples(attractor_list, attracted_nodes)
    #network.add_edges_from(edge_tuples, interaction='in-complex-with')
    return attractor_list[0]

def apply_directed_flow_layout(G, directed_edge_types=None):
    target_only_nodes = []
    source_only_nodes = []
    initial_pos = {}
    fixed = []
    upstream_attractor = None
    downstream_attractor = None
    random.seed()

    for node in G.nodes():
        out_count = 0
        in_count = 0
        x_pos = random.random()
        y_pos = random.random()
        initial_pos[node] = (x_pos, y_pos)
        edge_id = None
        for edge in G.out_edges([node], keys=True):
            edge_id = edge[2]
            interaction = G.get_edge_attribute_value_by_id(edge_id, "interaction")
            causal = G.get_edge_attribute_value_by_id(edge_id, "causal")
            if causal or interaction in directed_edge_types:
                out_count = out_count + 1
        for edge in G.in_edges([node], keys=True):
            edge_id = edge[2]
            interaction = G.get_edge_attribute_value_by_id(edge_id, "interaction")
            causal = G.get_edge_attribute_value_by_id(edge_id, "causal")
            if causal or interaction in directed_edge_types:
                in_count = in_count + 1

        if out_count is 0 and in_count > 0:
            target_only_nodes.append(node)

        if in_count is 0 and out_count > 0:
            source_only_nodes.append(node)

    if len(target_only_nodes) > 0:
        #print target_only_nodes
        downstream_attractor = _add_attractor(G, target_only_nodes, "downstream")
        initial_pos[downstream_attractor] = (1.0, 0.5)
        fixed.append(downstream_attractor)

    if len(source_only_nodes) > 0:
        #print source_only_nodes
        upstream_attractor = _add_attractor(G, source_only_nodes, "upstream")
        initial_pos[upstream_attractor] = (0.0, 0.5)
        fixed.append(upstream_attractor)

    #print fixed

    G.pos = nx.spring_layout(G.to_undirected(), pos=initial_pos, fixed=fixed)

    for node_id in G.nodes():
        node_name = G.get_node_attribute_value_by_id(node_id)
        if node_name is None:
            node_name = "Unknown " + str(node_id)

        if node_id in G.pos:
            pos = G.pos[node_id]
            # if pos is not None:
            #     print node_name + " : " + str(pos)
            # else:
            #     print node_name + "Null Position"

        else:
            print node_name + "No Position"

    G.remove_nodes_from([downstream_attractor])
    G.remove_nodes_from([upstream_attractor])

    # print G.pos