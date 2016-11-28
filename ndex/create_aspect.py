def number_verification():
    return [{'numberVerification': [{'longNumber': 281474976710655}]}]

def metadata(metadata_dict=None, max_node_id=0, max_edge_id=0):
    if(metadata_dict is not None):
        metadata_list = [{'name': k, 'idCounter': v, 'consistencyGroup': 2} for k, v in metadata_dict.items()]
        return [{'metaData': metadata_list}]
    else:
        return [{'metaData': [{'name': 'nodes', 'idCounter': max_node_id}, {'name': 'edges', 'idCounter': max_edge_id}]}]

def subnetworks(G, id, view_id):
    result = [{'subNetworks': [{'@id': id, 'nodes': G.nodes(), 'edges': [e[2] for e in G.edges_iter(keys=True)]}]}]
    result += [{'cyViews': [{'s': id, '@id': view_id}]}]
    return result

def nodes(G):
    return [{'nodes': [{'@id': n[0], 'n': n[1]['name'], 'r': n[1]['represents']}]} if 'name' in n[1] and 'represents' in n[1] else
            {'nodes': [{'@id': n[0], 'n': n[1]['name']}]} if 'name' in n[1] and 'represents' not in n[1] else
            {'nodes': [{'@id': n[0], 'r': n[1]['represents']}]} if 'name' not in n[1] and 'represents' in n[1] else
            {'nodes': [{'@id': n[0]}]}
            for n in G.nodes_iter(data=True)]

def edges(G):
    return [
        {'edges':[{'i': e[3]['interaction'], 's': e[0], '@id': e[2], 't': e[1]}]}
        if 'interaction' in e[3] else
        {'edges': [{'s': e[0], '@id': e[2], 't': e[1]}]}
        for e in G.edges_iter(data=True, keys=True)]

def network_attributes(G):
    return [{'networkAttributes': [
        {'n': k, 'v': G.graph[k]} if isinstance(G.graph[k], basestring) else
        {'n': k, 'v': cv(G.graph[k]), 'd': domain(G.graph[k])}
        for k in G.graph]}]

def node_attributes(G):
    return [{'nodeAttributes': [
        {'po': n[0], 'n': k, 'v': n[1][k]} if isinstance(n[1][k], basestring) else
        {'po': n[0], 'n': k, 'v': cv(n[1][k]), 'd': domain(n[1][k])}
        for k in n[1] if k != 'name' and k != 'represents']} for n in G.nodes_iter(data=True)
            if ('name' in n[1] and 'represents' in n[1] and len(n[1]) > 2) or
            ('name' in n[1] and 'represents' not in n[1] and len(n[1]) > 1) or
            ('name' not in n[1] and 'represents' in n[1] and len(n[1]) > 1) or
            ('name' not in n[1] and 'represents' not in n[1] and len(n[1]) > 0)]

def edge_attributes(G):
    return [{'edgeAttributes': [
        {'po': e[2], 'n': k, 'v': e[3][k]} if isinstance(e[3][k], basestring) else
        {'po': e[2], 'n': k, 'v': cv(e[3][k]), 'd': domain(e[3][k])}
        for k in e[3]] } for e in G.edges_iter(data=True, keys=True) if e[3]]

def cartesian(G, id):
    pos = G.pos
    scale_factor = 40 * G.number_of_nodes()
    if all( abs(pos[n][0]) < 2.01 and abs(pos[n][1]) < 2.01 for n in pos):
        pos = {id:pos[id]*scale_factor for id in pos }
    return [{'cartesianLayout': [
        {'node':n, 'view':id, 'x':float(pos[n][0]), 'y':float(pos[n][1])}
        for n in pos
    ]}]

def citations(G):
    citations = []
    for citation_id in G.citation_map:
        citation = G.citation_map[citation_id]
        citation["@id"] = citation_id
        citations.append(citation)
    return [{"citations" : citations}]

def node_citations(G):
    node_citations = []
    for node_id in G.node_citation_map:
        citations = G.node_citation_map[node_id]
        node_citations.append({"citations": citations, "po": [node_id]})
    return [{"nodeCitations" : node_citations}]

def edge_citations(G):
    edge_citations = []
    for edge_id in G.edge_citation_map:
        citations = G.edge_citation_map[edge_id]
        edge_citations.append({"citations": citations, "po": [edge_id]})
    return [{"edgeCitations" : edge_citations}]

def supports(G):
    supports = []
    for support_id in G.support_map:
        support = G.support_map[support_id]
        support["@id"] = support_id
        supports.append(support)
    return [{"supports" : supports}]

def node_supports(G):
    node_supports = []
    for node_id in G.node_support_map:
        supports = G.node_support_map[node_id]
        node_supports.append({"supports": supports, "po": [node_id]})
    return [{"nodeSupports" : node_supports}]

def edge_supports(G):
    edge_supports = []
    for edge_id in G.edge_support_map:
        supports = G.edge_support_map[edge_id]
        edge_supports.append({"supports": supports, "po": [edge_id]})
    return [{"edgeSupports" : edge_supports}]

# cv stands for convert value. This converts a type to a string representation for CX purposes.
def cv(val):
    return val


def domain(val):
    if type(val) is list:
        if isinstance(val[0], basestring):
            return 'list_of_string'
        elif type(val[0]) is bool:
            return 'list_of_boolean'
        elif type(val[0]) is int:
            return 'list_of_integer'
        elif type(val[0]) is long:
            return 'list_of_long'
        elif type(val[0]) is float:
            return 'list_of_double'
        else:
            return 'list_of_unknown'

    if isinstance(val, basestring):
        return 'string'
    elif type(val) is bool:
        return 'boolean'
    elif type(val) is int:
        return 'integer'
    elif type(val) is long:
        return 'long'
    elif type(val) is float:
        return 'double'
    else:
        return 'unknown'