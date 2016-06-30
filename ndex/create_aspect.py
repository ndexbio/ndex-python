def number_verification():
    return [{'numberVerification': [{'longNumber': 281474976710655}]}]

def metadata(max_node_id=0, max_edge_id=0):
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
    if all( abs(pos[n][0]) < 1.01 and abs(pos[n][1]) < 1.01 for n in pos):
        pos = {id:pos[id]*100 for id in pos }
    return [{'cartesianLayout': [
        {'node':n, 'view':id, 'x':float(pos[n][0]), 'y':float(pos[n][1])}
        for n in pos
    ]}]



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