from ndex.networkn import NdexGraph
from ndex.client import Ndex


def test_create_from_edge_list():
    G = NdexGraph()
    edge_list = [('A', 'B'), ('B', 'C')]

    G.create_from_edge_list(edge_list, interaction=['A-B', 'B-C'])

    print G.edge
    print G.node

    G.upload_to("http://test.ndexbio.org", "scratch", "scratch")


test_create_from_edge_list()
