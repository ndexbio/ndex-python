import networkx as nx
from networkx.classes.multidigraph import MultiDiGraph
import copy
import matplotlib.pyplot as plt
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

    def show_stats(self):
        '''Show the number of nodes and edges.'''
        print "Nodes: %d" % self.number_of_nodes()
        print "Edges: %d" % self.number_of_edges()

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
        '''Load NdexGraph from file.'''
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
        '''Annotate an NdexGraph with attributes from file'''
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

    def show(self):
        '''Show information about the graph and its data.'''
        print 'Graph Data:'
        print str(self.graph)
        print str(self.nodes(data=True))
        print str(self.edges(data=True, keys=True))

    def _get_labels(self):
        return {n:data['name'] if 'name' in data else n for n, data in self.nodes_iter(data=True)}

    def draw(self):
        '''Draw the graph to get a sense of its topology.'''
        G = self
        if self.pos:
            pos = self.pos
        else:
            pos = nx.spring_layout(G)
        labels = self._get_labels()
        nx.draw_networkx_labels(G, pos, labels=labels)
        node_size = 1600
        node_color = 'green'
        node_alpha = 0.5
        nx.draw_networkx_nodes(G, pos, node_size=node_size,
                               alpha=node_alpha, node_color=node_color)
        edge_thickness = 1
        edge_alpha = 0.3
        edge_color = 'green'
        nx.draw_networkx_edges(G, pos, width=edge_thickness,
                               alpha=edge_alpha, edge_color=edge_color)
        plt.show()

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

    def add_next_node(self):
        '''Add a node with an appropriate cx id'''
        return self.add_named_node(None)

    def add_named_node(self, name):
        '''Add a node with a particular name to the graph.'''
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


    def get_node_ids(self, value, attribute='name'):
        '''Get the node ids of all nodes having an attribute equal to a particular value.'''
        nodes = [n[0] for n in self.nodes_iter(data=True) if attribute in n[1] and n[1][attribute] == value]
        return nodes


    def _get_edge_ids_by_node_attribute(self, source_node_value, target_node_value, attribute_key='name'):
        source_node_ids = self.get_node_ids(source_node_value, attribute_key)
        target_node_ids = self.get_node_ids(target_node_value, attribute_key)
        edge_keys = []
        for s in source_node_ids:
            for t in target_node_ids:
                if s in self and t in self[s]:
                    edge_keys += self[s][t].keys()
        return edge_keys


    def add_edge_between(self, n1, n2, interaction=None):
        '''Add edges between to nodes with the specified ids.'''
        if type(n1) != type(n2):
            raise ValueError("The node parameters must be the same type.")
        if isinstance(n1, basestring):
            if not self._all_node_names_are_unique():
                raise ValueError(
                    "Names are not unique in this network. Therefore, node parameters must be integer node ids.")
            G = self._get_nice()
        elif type(n1) is int:
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
        G.add_edge(n1, n2, self.max_edge_id, interaction=interaction)
        self.edgemap[self.max_edge_id] = (n1, n2)
        if G != self:
            self._set_nice(G)
        return self.max_edge_id

    def _get_edge_attribute_value_by_id(self, id, attribute_key):
        '''Get the value of a particular edge attribute based on the id.'''
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
        '''Given a list of edge ids and particular attribute key, return a list of attribute values.'''
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

    def _get_node_attribute_value_by_id(self, id, attribute_key='name'):
        if id not in self.node:
            raise ValueError("Your ID is not in the network")
        node_attributes = nx.get_node_attributes(self, attribute_key)
        if len(node_attributes) == 0:
            raise ValueError("That node attribute name does not exist ANYWHERE in the network.")
        return self.node[id][attribute_key] if attribute_key in self.node[id] else None

    def get_node_attribute_values_by_id_list(self, id_list, attribute_key='name'):
        '''Returns a list of attribute values that correspond with the attribute key using the nodes in id_list.'''
        for id in id_list:
            if id not in self.node:
                raise ValueError("Your ID list has IDs that are not in the network")
        node_attributes = nx.get_node_attributes(self, attribute_key)
        if len(node_attributes) == 0:
            raise ValueError("That node attribute name does not exist ANYWHERE in the network.")
        return [self.node[id][attribute_key] if attribute_key in self.node[id] else None for id in id_list]

    def get_node_names_by_id_list(self, id_list):
        '''Given a list of node ids, return a list of node names.'''
        return self.get_node_attribute_values_by_id_list(id_list)

    def get_node_name_by_id(self, id):
        '''Given a node id, return the name of the node.'''
        return self._get_node_attribute_value_by_id(id)

    def set_node_attribute(self, id, key, value):
        '''Set the value of a particular node attribute.'''
        if id in self.node:
            self.node[id][key] = value
        else:
            node_ids = self.get_node_ids(id)
            if len(node_ids) != 1:
                raise ValueError("The node ID is not unique.")
            node_id = node_ids[0]
            self.node[node_id][key] = value

    def get_node_attribute_keys(self):
        '''Get all of the attribute keys that are on some node in the graph.'''
        keys = set()
        for _, attributes in self.nodes_iter(data=True):
            for key, value in attributes.iteritems():
                keys.add(key)
        return list(keys)


    def set_edge_attribute(self, id, key, value):
        '''Set the value of a particular edge attribute.'''
        s, t = self.edgemap[id]
        self.edge[s][t][id][key] = value


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

    def _rename(self, name_map):
        names = {}
        for n in self.nodes_iter(data=True):
            if n[1]['name']:
                name = n[1]['name']
                if name in names:
                    names[name].append(n[0])
                else:
                    names[name] = [n[0]]
        for old_name in name_map:
            if old_name in names:
                new_name = name_map[old_name]
                for id in names[old_name]:
                    self.node[id]['name'] = new_name

    def _generate_new_key_for_merge(self, key, matts):
        key_postfix = 2
        new_key = key + str(key_postfix)
        while new_key in matts:
            key_postfix += 1
            new_key = key + str(key_postfix)
        return new_key

    def _merge_nodes_for_expand(self, node_id_list, secondary_network_name, expand_key, preserve_id=None, preserve_list=None):
        if not preserve_list:
            preserve_list = []
        G = self
        # matts is short for merged attributes.
        matts = {}
        for node_id in node_id_list:
            # atts is short for attributes
            atts = G.node[node_id]
            for key in atts:
                if key in matts:
                    #Don't make two columns for the expand key.
                    if key == expand_key:
                        continue
                    new_key = key + ' from ' + secondary_network_name
                    if new_key in matts:
                        new_key = self._generate_new_key_for_merge(new_key, matts)
                    matts[new_key] = atts[key]
                else:
                    matts[key] = atts[key]

        max_node_id = max(G.nodes())
        new_node_id = max_node_id + 1
        G.add_node(new_node_id, matts)

        max_edge_id = 0
        if G.number_of_edges() > 0:
            max_edge_id = max([e[2] for e in G.edges(keys=True)])

        for n1, n2, data in G.edges(data=True):
            # If both nodes are in the list, we don't want a new edge.
            if n1 in node_id_list and n2 in node_id_list:
                continue

            if n1 in node_id_list:
                max_edge_id += 1
                G.add_edge(new_node_id, n2, max_edge_id, data)

            elif n2 in node_id_list:
                max_edge_id += 1
                G.add_edge(n1, new_node_id, max_edge_id, data)


        for id in node_id_list:  # remove the merged nodes and adjacent edges
            if id not in preserve_list:
                G.remove_node(id)

        if preserve_id:
            G.add_node(preserve_id, matts)
            for n1, _, key, data in self.in_edges([new_node_id], keys=True, data=True):
                G.add_edge(n1, preserve_id, key, data)
            for _, n2, key, data in self.out_edges([new_node_id], keys=True, data=True):
                G.add_edge(preserve_id, n2, key, data)
            G.remove_node(new_node_id)

    def _make_attribute_node_map(self, G, attribute_key):
        map = {}

        for n in G.nodes():
            if attribute_key in G.node[n]:
                v = G.node[n][attribute_key]
                if v not in map:
                    map[v] = [n]
                else:
                    map[v].append(n)

        return map


    def expand(self, secondary_network, expand_key='name'):
        '''Expand this network using a secondary reference network based on the identity of a particular attribute value.'''
        primary_network_name = self.graph['name'] if 'name' in self.graph else 'Unknown Network'
        secondary_network_name = secondary_network.graph['name'] if 'name' in secondary_network.graph else 'Unknown Network'

        self.graph['name'] = primary_network_name + ' expanded with data from ' + secondary_network_name


        primary_map = self._make_attribute_node_map(self, expand_key)
        secondary_map = self._make_attribute_node_map(secondary_network, expand_key)

        # 1st: Add Matching Nodes
        added_node_map_secondary_to_primary = {}
        added_secondary_node_ids = set()
        merge_lists = {}
        for primary_key in primary_map.keys():
            if primary_key in secondary_map:
                for secondary_node_id in secondary_map[primary_key]:
                    new_node_id = self.add_next_node()
                    self.node[new_node_id] = copy.deepcopy(secondary_network.node[secondary_node_id])
                    if primary_key in merge_lists:
                        merge_lists[primary_key].append(new_node_id)
                    else:
                        merge_lists[primary_key] = [new_node_id]
                    added_node_map_secondary_to_primary[secondary_node_id] = new_node_id
                    added_secondary_node_ids.add(secondary_node_id)

        #2nd Add Connected Nodes
        for secondary_node_id in list(added_secondary_node_ids):

            for _, c, secondary_edge_key in secondary_network.out_edges([secondary_node_id], keys=True):
                if c not in added_secondary_node_ids:
                    new_connected_node_id = self.add_next_node()
                    self.node[new_connected_node_id] = copy.deepcopy(secondary_network.node[c])
                    added_node_map_secondary_to_primary[c] = new_connected_node_id
                    added_secondary_node_ids.add(c)


            for c, _, secondary_edge_key in secondary_network.in_edges([secondary_node_id], keys=True):
                if c not in added_secondary_node_ids:
                    new_connected_node_id = self.add_next_node()
                    self.node[new_connected_node_id] = copy.deepcopy(secondary_network.node[c])
                    added_node_map_secondary_to_primary[c] = new_connected_node_id
                    added_secondary_node_ids.add(c)

        # Add Edges from Matching Nodes to Connecting Nodes
        # t is the id from the secondary network
        for t in added_node_map_secondary_to_primary:
            # s is the id from the primary network
            s = added_node_map_secondary_to_primary[t]
            # c is the id of the connected node in the target network
            for _, c, secondary_edge_key in secondary_network.out_edges([t], keys=True):
                if c in added_node_map_secondary_to_primary:
                    # n2 is the id of the node we want to connect to s in the source network
                    n2 = added_node_map_secondary_to_primary[c]
                    # e is the id of the newly created edge between s and n2 in the source network.
                    e = self.add_edge_between(s, n2)
                    self[s][n2][e] = copy.deepcopy(secondary_network[t][c][secondary_edge_key])

        # Now Merge
        for key, merge_list in merge_lists.iteritems():
            if key in primary_map:
                for i in range(len(primary_map[key]) - 1):
                    preserve_id = primary_map[key][i]
                    self._merge_nodes_for_expand([preserve_id] + merge_list, secondary_network_name, expand_key, preserve_id, preserve_list=merge_list)
                preserve_id = primary_map[key][-1]
                self._merge_nodes_for_expand([preserve_id] + merge_list, secondary_network_name, expand_key, preserve_id)

    def write_to(self, filename):
        '''Write this graph as a CX file to the specified filename.'''
        with open(filename, 'w') as outfile:
            json.dump(self.to_cx(), outfile, indent=4)

    def upload_to(self, server, username, password):
        '''Upload this graph to the specified server using the specified username and password.'''
        ndex = nc.Ndex(server,username,password)
        ndex.save_cx_stream_as_new_network(self.to_cx_stream())


