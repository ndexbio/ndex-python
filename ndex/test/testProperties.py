import unittest

import ndex.client as nc
import time
from os import path


ndex_host = "http://dev.ndexbio.org"
ndex_network_resource = "/v2/network/"
username_1 = "ttt"
password_1 = "ttt"

example_network_1 = 'A549-SL-network.cx'



# Python Client APIs tested:
#
#   set_network_properties
#


class MyTestCase(unittest.TestCase):

    def test_network_system_properties(self):
        ndex = nc.Ndex(host=ndex_host, username=username_1, password=password_1)

        with open(path.join(path.abspath(path.dirname(__file__)),example_network_1), 'r') as file_handler:
            network_in_cx = file_handler.read()

        # test save_cx_stream_as_new_network
        test_network_1_uri = ndex.save_cx_stream_as_new_network(network_in_cx)
        self.assertTrue(test_network_1_uri.startswith(ndex_host + ndex_network_resource))

        network_UUID = str(test_network_1_uri.split("/")[-1])

        # get network summary
        network_summary = ndex.get_network_summary(network_UUID)

        if "subnetworkIds" in network_summary:
            number_of_subnetworks = len(network_summary["subnetworkIds"])
            self.assertTrue(number_of_subnetworks == 1, "Expected 1 subnetwork in network summary, but there are " \
                            + str(number_of_subnetworks))

        subnetwork_id = network_summary["subnetworkIds"][0]




        # test set_network_system_properties
        time.sleep(10)



        # test delete_network
        del_network_return = ndex.delete_network(network_UUID)
        self.assertTrue(del_network_return == '')




if __name__ == '__main__':
    unittest.main()

