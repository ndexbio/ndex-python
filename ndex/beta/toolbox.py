import pandas as pd
import networkx as nx


def load(G, filename, source=1, target=2, edge_attributes=None, sep='\t', header=False):
    '''Load NdexGraph from file.

        :param filename: The name of the file to load. Could include an absolute or relative path.
        :param source: The source node column. (An integer; start counting at 1.)
        :param target: The target node column. (An integer; start counting at 1.)
        :param edge_attributes: A list of names for other columns which are edge attributes.
        :param sep: The cell separator, often a tab (\t), but possibly a comma or other character.
        :param header: Whether the first row should be interpreted as column headers.
    '''
    G.clear()
    if edge_attributes != None:
        if not header and not all(type(i) is int for i in edge_attributes):
            raise ValueError(
                "If there is no header, all edge_attributes must be either a list of integers or None.")
    header = 0 if header else None
    df = pd.read_csv(filename, sep=sep, header=header)
    if type(source) is int:
        source = source - 1
        source_index = df.columns.values[source]
    else:
        if header == False:
            raise ValueError("If a string is used for source or target, then there must be a header.")
        source_index = source
    if type(target) is int:
        target = target - 1
        target_index = df.columns.values[target]
    else:
        if header == False:
            raise ValueError("If a string is used for source or target, then there must be a header.")
        target_index = target
    if edge_attributes is None:
        edge_attributes = []
    edge_attributes = [c - 1 if type(c) is int else c for c in edge_attributes]

    nodes = pd.concat([df.ix[:, source_index], df.ix[:, target_index]],
                      ignore_index=True).drop_duplicates().reset_index(drop=True)
    nodes.apply(lambda x: G.add_new_node(name=x))
    # Map node names to ids
    n_id = {data['name']: n for n, data in G.nodes_iter(data=True)}
    edges = df[[source_index, target_index]]
    edges.apply(lambda x: G.add_edge_between(n_id[x[0]], n_id[x[1]]), axis=1)
    e_id = {}
    for s, t, key in G.edges_iter(keys=True):
        if s not in e_id:
            e_id[s] = {}
        e_id[s][t] = key

    for edge_attribute in edge_attributes:
        source_header = df.columns.values[source]
        target_header = df.columns.values[target]
        if type(edge_attribute) is int:
            edge_attribute = edge_attribute - 1
            value_index = df.columns.values[edge_attribute]
        else:
            value_index = edge_attribute
        edge_col = df[[source_index, target_index, value_index]]
        if header is not None:
            name = value_index
        else:
            name = "Column %d" % value_index
        edge_col.apply(
            lambda x: nx.set_edge_attributes(G, name, {
                (n_id[x[source_header]], n_id[x[target_header]], e_id[n_id[x[source_header]]][n_id[x[target_header]]]):
                    x[value_index]}),
            axis=1)