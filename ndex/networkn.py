import networkx as nx
from networkx.classes.multidigraph import MultiDiGraph
import copy
import pandas as pd
import create_aspect
import io
import json
import numpy as np
import ndex.client as nc

class NdexGraph (MultiDiGraph):
    '''A graph compatible with NDEx'''
    def __init__(self, cx=None, server=None, username=None, password=None, uuid=None, data=None, **attr):
        '''There are generally four ways to create a graph.

            1. An empty graph. G = NdexGraph()
            2. Using a cx dictionary. G = NdexGraph(cx)
            3. Loading it from an NDEx server.
                G = NdexGraph(server='http://test.ndexbio.org' uuid='983a2b93-2c55-11e6-a7c5-0630eb0972a1')
            4. Just like any other NetworkX MultiDiGraph().

        '''
        MultiDiGraph.__init__(self, data, **attr)
        self.subnetwork_id = None
        self.view_id = None
        self.max_node_id = None
        self.max_edge_id = None
        self.pos = {}
        self.unknown_cx = []

        # Maps edge ids to node ids. e.g. { edge1: (source_node, target_node), edge2: (source_node, target_node) }
        self.edgemap = {}

        if not cx and server and uuid:
            ndex = nc.Ndex(server,username,password)
            cx = ndex.get_network_as_cx_stream(uuid).json()
            if not cx:
                raise RuntimeError("Failed to retrieve network with uuid " + uuid + " from " + server)

        # If there is no CX to process, just return.
        if cx == None:
            return

        # First pass, get information about subnetworks.
        for aspect in cx:
            if 'subNetworks' in aspect:
                for subnetwork in aspect['subNetworks']:
                    id = subnetwork['@id']
                    if self.subnetwork_id != None:
                        raise ValueError("networkn does not support collections!")
                    self.subnetwork_id = id
            elif 'cyViews' in aspect:
                for cyViews in aspect['cyViews']:
                    id = cyViews['@id']
                    if self.view_id != None:
                        raise ValueError("networkn does not support more than one view!")
                    self.view_id = id
            elif 'metaData' in aspect:
                # Strip metaData
                continue
            else:
                self.unknown_cx.append(aspect)
            cx = self.unknown_cx

        # Second pass, just build basic graph.
        self.unknown_cx = []
        for aspect in cx:
            if 'nodes' in aspect:
                for node in aspect['nodes']:
                    id = node['@id']
                    name = node['n'] if 'n' in node else None
                    if name:
                        self.add_node(id, name=name)
                    else:
                        self.add_node(id)
                    represents = node['r'] if 'r' in node else None
                    if represents:
                        self.node[id]['represents'] = represents

            elif 'edges' in aspect:
                for edge in aspect['edges']:
                    id = edge['@id']
                    interaction = edge['i'] if 'i' in edge else None
                    s = edge['s']
                    t = edge['t']
                    self.edgemap[id] = (s, t)
                    if interaction:
                        self.add_edge(s, t, key=id, interaction=interaction)
                    else:
                        self.add_edge(s, t, key=id)
            else:
                self.unknown_cx.append(aspect)
        cx = self.unknown_cx

        # Third pass, handle attributes
        # Notes. Not handled, datatypes.
        self.unknown_cx = []
        for aspect in cx:
            if 'networkAttributes' in aspect:
                for networkAttribute in aspect['networkAttributes']:
                    name = networkAttribute['n']
                    # special: ignore selected
                    if name == 'selected':
                        continue
                    value = networkAttribute['v']
                    if 'd' in networkAttribute:
                        d = networkAttribute['d']
                        if d == 'boolean':
                            value = value.lower() == 'true'
                    if 's' in networkAttribute or name not in self.graph:
                        self.graph[name] = value

            elif 'nodeAttributes' in aspect:
                for nodeAttribute in aspect['nodeAttributes']:
                    id = nodeAttribute['po']
                    name = nodeAttribute['n']
                    # special: ignore selected
                    if name == 'selected':
                        continue
                    value = nodeAttribute['v']
                    if 'd' in nodeAttribute:
                        d = nodeAttribute['d']
                        if d == 'boolean':
                            value = value.lower() == 'true'
                    if 's' in nodeAttribute or name not in self.node[id]:
                        self.node[id][name] = value
            elif 'edgeAttributes' in aspect:
                for edgeAttribute in aspect['edgeAttributes']:
                    id = edgeAttribute['po']
                    s, t = self.edgemap[id]
                    name = edgeAttribute['n']
                    # special: ignore selected and shared_name columns
                    if name == 'selected' or name == 'shared name':
                        continue
                    value = edgeAttribute['v']
                    if 'd' in edgeAttribute:
                        d = edgeAttribute['d']
                        if d == 'boolean':
                            value = value.lower() == 'true'
                    if 's' in edgeAttribute or name not in self[s][t][id]:
                        self[s][t][id][name] = value

            else:
                self.unknown_cx.append(aspect)
        cx = self.unknown_cx
        # Fourth pass, node locations
        self.pos = {}
        self.unknown_cx = []
        for aspect in cx:
            if 'cartesianLayout' in aspect:
                for nodeLayout in aspect['cartesianLayout']:
                    id = nodeLayout['node']
                    x = nodeLayout['x']
                    y = nodeLayout['y']
                    self.pos[id] = np.array([x,y], dtype='float32')
            else:
                self.unknown_cx.append(aspect)

    def clear(self):
        '''Eliminate all graph data and start from scratch.'''
        super(NdexGraph, self).clear()
        self.subnetwork_id = None
        self.view_id = None
        self.max_node_id = 0
        self.max_edge_id = 0
        self.pos = None
        self.edgemap = {}
        self.unknown_cx = []

    def _all_nodes_are_named(self):
        return all('name' in self.node[n] for n in self.nodes_iter())

    def _all_node_names_are_unique(self):
        names = [self.node[n]['name'] for n in self.nodes_iter() if 'name' in self.node[n]]
        return len(names) == len(set(names))

    def _get_nice(self):
        if not self._all_node_names_are_unique() or not self._all_nodes_are_named():
            return None
        G = copy.deepcopy(self)
        mapping = {n: G.node[n]['name'] for n in G.nodes_iter()}
        nx.relabel_nodes(G, mapping, copy=False)
        return G

    def _set_nice(self, G):
        self.clear()
        self.graph = copy.deepcopy(G.graph)
        self.node = copy.deepcopy(G.node)
        self.edge = copy.deepcopy(G.edge)
        G = self
        for n in G.nodes_iter():
            G.node[n]['name'] = n
        mapping = {n: i for i, n in enumerate(G.nodes_iter())}
        nx.relabel_nodes(G, mapping, copy=False)
        for i, e in enumerate(G.edges()):
            if 0 in G[e[0]][e[1]]:
                G[e[0]][e[1]][i] = G[e[0]][e[1]].pop(0)

    def _create_from_networkx(self, G):
        self.clear()
        for node_id, data in G.nodes_iter(data=True):
            self.add_node(node_id, data)
        if isinstance(G, nx.MultiGraph):
            for s, t, key, data in G.edges_iter(keys=True, data=True):
                self.add_edge(s,t,key,data)
        else:
            for s, t, data in G.edges_iter(data=True):
                self.add_edge(s, t, self.max_edge_id, data)
                self.max_edge_id +=1

    def load(self, filename, source=1, target=2, edge_attributes=None, sep='\t', header=False):
        '''Load NdexGraph from file.

            The parameters are:
            filename = The name of the file to load. Could include an absolute or relative path.
            source = The source node column. (An integer; start counting at 1.)
            target = The target node column. (An integer; start counting at 1.)
            edge_attributes = A list of names for other columns which are edge attributes.
            sep = The cell separator, often a tab (\t), but possibly a comma or other character.
            header = Whether the first row should be interpreted as column headers.
        '''
        G = nx.MultiDiGraph()
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
        nodes.apply(lambda x: G.add_node(x))
        edges = df[[source_index, target_index]]
        edges.apply(lambda x: G.add_edge(x[0], x[1]), axis=1)

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
                lambda x: nx.set_edge_attributes(G, name, {(x[source_header], x[target_header], 0): x[value_index]}),
                axis=1)

        self._set_nice(G)

    def annotate_network(self, filename, sep='\t'):
        '''Annotate this NdexGraph with attributes from file

            The parameters are:
            filename = The name of the file to load. Could include an absolute or relative path.
            sep = The cell separator, often a tab (\t), but possibly a comma or other character.
        '''
        G = self._get_nice()
        df = pd.read_csv(filename, sep=sep)
        num_attributes = df.shape[1] - 1
        node_header = df.columns.values[0]
        for i in range(num_attributes):
            attribute_header = df.columns.values[i + 1]
            att_df = df[[node_header, attribute_header]]
            att_df.apply((lambda x: nx.set_node_attributes(G, attribute_header, {x[0]: x[1]})), axis=1)
        self._set_nice(G)

    def set_name(self, name):
        '''Set the name of this graph'''
        self.graph['name'] = name

    def get_name(self):
        '''Get the name of this graph'''
        if 'name' in self.graph:
            return self.graph['name']
        return None

    def to_cx(self):
        '''Convert the graph to a CX dictionary'''
        G = self
        cx = []
        cx += create_aspect.number_verification()
        cx += create_aspect.metadata()
        cx += create_aspect.network_attributes(G)
        if self.subnetwork_id and self.view_id:
            cx += create_aspect.subnetworks(G, self.subnetwork_id, self.view_id)
        else:
            cx += create_aspect.subnetworks(G, 0, 0)
        cx += create_aspect.nodes(G)
        cx += create_aspect.edges(G)
        cx += create_aspect.node_attributes(G)
        cx += create_aspect.edge_attributes(G)
        if self.pos and len(self.pos):
            if self.subnetwork_id and self.view_id:
                cx += create_aspect.cartesian(G, self.view_id)
            else:
                cx += create_aspect.cartesian(G, 0)
        cx += self.unknown_cx

        return cx

    def add_cx_node(self, name=None):
        '''Add a cx node, possibly with a particular name, to the graph.'''
        if self.max_node_id == None:
            if self.number_of_nodes() > 0:
                self.max_node_id = max(self.nodes())
            else:
                self.max_node_id = 0
        self.max_node_id += 1
        if name:
            self.add_node(self.max_node_id, name=name)
        else:
            self.add_node(self.max_node_id)
        return self.max_node_id


    def get_node_ids(self, value, attribute_key='name'):
        '''Returns a list of node ids of all nodes where a particular attribute has a particular value.

            The parameters are:
            value = The value we want.
            attribute_key = The name of the attribute where we should look for the value.
        '''
        nodes = [n[0] for n in self.nodes_iter(data=True) if attribute_key in n[1] and n[1][attribute_key] == value]
        return nodes


    def get_edge_ids_by_node_attribute(self, source_node_value, target_node_value, attribute_key='name'):
        '''Returns a list of edge ids of all edges where the source node and target node has a particular value for particular attribute.

                The parameters are:
                source_node_value = The value we want in the source node.
                target_node_value = The value we want in the target node.
                attribute_key = The name of the attribute where we should look for the value.
            '''
        source_node_ids = self.get_node_ids(source_node_value, attribute_key)
        target_node_ids = self.get_node_ids(target_node_value, attribute_key)
        edge_keys = []
        for s in source_node_ids:
            for t in target_node_ids:
                if s in self and t in self[s]:
                    edge_keys += self[s][t].keys()
        return edge_keys


    # Need to document n1 and n2 options.
    # Document if node names are used, they must be unqiue.
    def add_edge_between(self, source_node, target_node, interaction=None):
        '''Add edges between two nodes in this NdexGraph, optionally specifying a type of interaction

        The parameters are:
        source_node_value = The source node, specified by either an id or name. If a name, it must be a string.
        target_node_value = The target node, specified by either an id or name. If a name, it must be a string.
        interaction = The type of interaction specified by the newly added edge.

        Notes:
        The source_node_value and target_node_value must be the same type (either both id or both name). If name
        is used, then all names on the network must be unique.
        '''
        if type(source_node) != type(target_node):
            raise ValueError("The node parameters must be the same type.")
        if isinstance(source_node, basestring):
            if not self._all_node_names_are_unique():
                raise ValueError(
                    "Names are not unique in this network. Therefore, node parameters must be integer node ids.")
            G = self._get_nice()
        elif type(source_node) is int:
            G = self
        else:
            raise ValueError("Node parameters must be either int or string.")

        if interaction == None:
            interaction = 'interacts with'
        if self.max_edge_id == None:
            if self.number_of_edges() > 0:
                self.max_edge_id = max([x[2] for x in self.edges(keys=True)])
            else:
                self.max_edge_id = 0
        self.max_edge_id += 1
        G.add_edge(source_node, target_node, self.max_edge_id, interaction=interaction)
        self.edgemap[self.max_edge_id] = (source_node, target_node)
        if G != self:
            self._set_nice(G)
        return self.max_edge_id

    def get_edge_attribute_value_by_id(self, id, attribute_key):
        '''Get the value of a particular edge attribute based on the id.

        The parameters are:
            id = The id of the edge.
            attribute_key = The name of the attribute whose value should be retrieved.

        '''
        edge_keys = {key: (s, t) for s, t, key in self.edges_iter(keys=True)}
        if id not in edge_keys:
            raise ValueError("Your ID is not in the network")
        s = edge_keys[id][0]
        t = edge_keys[id][1]
        edge_attributes = nx.get_edge_attributes(self, attribute_key)
        if len(edge_attributes) == 0:
            raise ValueError("That node edge name does not exist ANYWHERE in the network.")
        return self[s][t][id][attribute_key] if attribute_key in self[s][t][id] else None


    def get_edge_attribute_values_by_id_list(self, id_list, attribute_key):
        '''Given a list of edge ids and particular attribute key, return a list of corresponding attribute values.'

        The parameters are:
            id_list = A list of edge ids whose attribute values we wish to retrieve
            attribute_key = The name of the attribute whose corresponding values should be retrieved.
        '''

        edge_keys = {key: (s, t) for s, t, key in self.edges_iter(keys=True)}
        for id in id_list:
            if id not in edge_keys:
                raise ValueError("Your ID list has IDs that are not in the network")
        edge_keys = {id: edge_keys[id] for id in id_list}
        edge_attributes = nx.get_edge_attributes(self, attribute_key)
        if len(edge_attributes) == 0:
            raise ValueError("That node edge name does not exist ANYWHERE in the network.")
        return [self[v[0]][v[1]][k][attribute_key] if attribute_key in self[v[0]][v[1]][k] else None for k, v in
                edge_keys.iteritems()]

    def get_node_attribute_value_by_id(self, id, attribute_key='name'):
        '''Get the value of a particular node attribute based on the id.'''
        if id not in self.node:
            raise ValueError("Your ID is not in the network")
        node_attributes = nx.get_node_attributes(self, attribute_key)
        if len(node_attributes) == 0:
            raise ValueError("That node attribute name does not exist ANYWHERE in the network.")
        return self.node[id][attribute_key] if attribute_key in self.node[id] else None

    def get_node_attribute_values_by_id_list(self, id_list, attribute_key='name'):
        '''Returns a list of attribute values that correspond with the attribute key using the nodes in id_list.

        The parameters are:
            id_list = A list of node ids whose attribute values we wish to retrieve.
            attribute_key = The name of the attribute whose corresponding values should be retrieved.

        '''
        for id in id_list:
            if id not in self.node:
                raise ValueError("Your ID list has IDs that are not in the network")
        node_attributes = nx.get_node_attributes(self, attribute_key)
        if len(node_attributes) == 0:
            raise ValueError("That node attribute name does not exist ANYWHERE in the network.")
        return [self.node[id][attribute_key] if attribute_key in self.node[id] else None for id in id_list]

    def get_node_names_by_id_list(self, id_list):
        '''Given a list of node ids, return a list of node names.

        The parameters are:
            id_list = A list of node ids whose attribute values we wish to retrieve.
        '''
        return self.get_node_attribute_values_by_id_list(id_list)

    def get_node_name_by_id(self, id):
        '''Given a node id, return the name of the node.'''
        return self.get_node_attribute_value_by_id(id)

    def get_node_attribute_keys(self):
        '''Get a list of all of the attribute keys that are on at least one node in the graph.'''
        keys = set()
        for _, attributes in self.nodes_iter(data=True):
            for key, value in attributes.iteritems():
                keys.add(key)
        return list(keys)

    def set_edge_attribute(self, id, attribute_key, attribute_value):
        '''Set the value of a particular edge attribute.

        The parameters are:
            id = The edge id we wish to set an attribute on.
            attribute_key = The name of the attribute we wish to set.
            attribute_value = The value we wish to set the attribute to.

        '''
        s, t = self.edgemap[id]
        self.edge[s][t][id][attribute_key] = attribute_value

    def get_edge_attribute_keys(self):
        '''Get all of the attribute keys that are on some edge in the graph.'''
        keys = set()
        for _, _, attributes in self.edges_iter(data=True):
            for key, value in attributes.iteritems():
                keys.add(key)
        return list(keys)

    def to_cx_stream(self):
        '''Convert this graph to a CX stream'''
        cx = self.to_cx()
        return io.BytesIO(json.dumps(cx))

    def write_to(self, filename):
        '''Write this graph as a CX file to the specified filename.'''
        with open(filename, 'w') as outfile:
            json.dump(self.to_cx(), outfile, indent=4)

    def upload_to(self, server, username, password):
        '''Uploads this graph to the specified server using the specified username and password.

        Example:
            ndexGraph.upload_to('http://test.ndexbio.org', 'myusername', 'mypassword')
        '''

        ndex = nc.Ndex(server,username,password)
        ndex.save_cx_stream_as_new_network(self.to_cx_stream())