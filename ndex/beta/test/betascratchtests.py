from ndex.networkn import NdexGraph
import ndex.beta.toolbox as toolbox


def test_load():
    G = NdexGraph()
    toolbox.load(G, 'loadexample.txt', edge_attributes=['strength'], header=True)
    print G.node
    print G.edge
    # G.write_to('loadexample.cx')
    # network_id = G.upload_to('http://public.ndexbio.org', 'scratch', 'scratch')
    # print network_id

test_load()