from ndex.networkn import NdexGraph
from ndex.client import Ndex


def test_create_from_edge_list():
    G = NdexGraph()
    edge_list = [('A', 'B'), ('B', 'C')]

    G.create_from_edge_list(edge_list, interaction=['A-B', 'B-C'])

    G.set_name('create_from_edge_list')

    network_id = G.upload_to("http://test.ndexbio.org", "scratch", "scratch")
    print network_id

    ndex = Ndex("http://test.ndexbio.org", "scratch", "scratch")
    ndex.make_network_public(network_id)
    ndex.make_network_private(network_id)

def test_cartesian():
    G = NdexGraph(server="http://test.ndexbio.org",
                  username='scratch', password='scratch',
                  uuid='aa6e7426-3f14-11e6-a7fa-028f28cd6a5b')
    G.write_to('cartesian2.cx')



if __name__ == "__main__":
    test_create_from_edge_list()


