import networkn


class ndexGraphBuilder:
    def __init__(self):
        self.ndexGraph = networkn.NdexGraph()
        self.nodeIdCounter = 0
        self.sidTable = {}  # external id to nodeIt mapping table
        self.edgeIdCounter = 0

    def addNamespaces(self, namespaces):
        self.ndexGraph.set_namespace(namespaces)

    def addNode(self,ext_id, name= None, represent=None, attributes=None ):
        """Add a cx node, possibly with a particular name, to the graph.

        :param ext_id: external id for this node
        :type ext_id str
        :param name: The name of the node. (Optional).
        :type name: str
        :param attr_dict: Dictionary of node attributes.  Key/value pairs will update existing data associated with the node.
        :type attr_dict: dict
        :param attr: Set or change attributes using key=value.

        """
        nodeId = self.sidTable[ext_id]
        if  not nodeId :
            nodeId = self.nodeIdCounter
            self.nodeIdCounter +=1
            self.sidTable[ext_id]=nodeId
            self.ndexGraph.add_cx_node(nodeId, name,represent, attributes)
        return nodeId

    def addEdge(self, src_ext_id, tgt_ext_id, interaction=None, attributes=None):
        s = self.addNode(src_ext_id)
        t = self.addNode(tgt_ext_id)
        id = self.edgeIdCounter
        if interaction:
            self.ndexGraph.add_edge(s, t, key=id, attr_dict= attributes,interaction=interaction)
        else:
            self.ndexGraph.add_edge(s, t, key=id, attr_dict = attributes)

        self.edgeIdCounter +=1
        return id




    def getNdexGraph(self):
        return self.ndexGraph
