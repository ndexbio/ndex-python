import pytest

from ndex.networkn import NdexGraph

def test_types():
    G = NdexGraph()
    n = G.add_new_node('Node with Types')
    n1 = G.add_new_node('A')
    n2 = G.add_new_node('B')
    G.add_edge_between(n, n1)
    G.add_edge_between(n, n2)
    G.set_name('Test Types')

    G.node[n]['string'] = 'mystring'
    G.node[n]['bool'] = True
    G.node[n]['int'] = 5
    G.node[n]['double'] = 2.5
    G.node[n]['long'] = 5L

    G.node[n]['string_list'] = ['mystring','myotherstring']
    G.node[n]['bool_list'] = [False, True]
    G.node[n]['int_list'] = [5, -20]
    G.node[n]['double_list'] = [2.5, 3.7]
    G.node[n]['long_list'] = [5L, 75L]

    G.write_to('temp_test_type.cx')

    # G.upload_to('http://test.ndexbio.org', 'scratch', 'scratch')

def test_metadata():
    G = NdexGraph(server="http://dev.ndexbio.org", uuid="317332f7-ade8-11e6-913c-06832d634f41")
    print G.metadata_original

if __name__ == "__main__":
    test_types()
    test_metadata()