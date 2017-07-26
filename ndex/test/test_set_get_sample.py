import unittest

import ndex.client as nc
import time
from os import path
import ndex.test.test_NdexClient as tt
import json

ndex_network_resource = "/v2/network/"

example_network_1 = 'A549-SL-network.cx'
sample_network = "filtered.cx"


# Python Client APIs tested:
#
#   set_network_properties
#


class MyTestCase(unittest.TestCase):

    def test_get_set_sample_network(self):
        ndex = nc.Ndex(host= tt.TESTSERVER, username=tt.testUser1, password=tt.testUserpasswd, debug=True)

        with open(path.join(path.abspath(path.dirname(__file__)),example_network_1), 'r') as file_handler:
            network_in_cx = file_handler.read()

        # test save_cx_stream_as_new_network
        test_network_1_uri = ndex.save_cx_stream_as_new_network(network_in_cx)
        self.assertTrue(test_network_1_uri.startswith(tt.TESTSERVER + ndex_network_resource))

        network_UUID = str(test_network_1_uri.split("/")[-1])

        time.sleep(20)

        with open(path.join(path.abspath(path.dirname(__file__)),sample_network), 'r') as file_handler:
            sample_cx = file_handler.read()
        ndex.set_network_sample(network_UUID, sample_cx)

        time.sleep(3)
        # get network summary with the new properties
        sample_from_server = ndex.get_sample_network(network_UUID)
        putJson = json.loads(sample_cx)
        self.assertTrue(len(putJson) == len(sample_from_server))


        # test delete_network
        del_network_return = ndex.delete_network(network_UUID)
        self.assertTrue(del_network_return == '')

if __name__ == '__main__':
    unittest.main()

