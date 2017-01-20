import unittest

import ndex.client as nc
import time
from os import path


ndex_host = "http://dev.ndexbio.org"
ndex_network_resource = "/v2/network/"
username_1 = "ttt"
password_1 = "ttt"

example_network_1 = './tiny_network.cx'

# Python Client APIs tested:
#
#   save_cx_stream_as_new_network
#   get_neighborhood_as_cx_stream
#   delete_network
#


class MyTestCase(unittest.TestCase):

    def test_query(self):
        ndex = nc.Ndex(host=ndex_host, username=username_1, password=password_1)

        with open(path.join(path.abspath(path.dirname(__file__)), example_network_1), 'r') as file_handler:
            network_in_cx_from_file = file_handler.read()

        # test save_cx_stream_as_new_network
        test_network_1_uri = ndex.save_cx_stream_as_new_network(network_in_cx_from_file)
        self.assertTrue(test_network_1_uri.startswith(ndex_host + ndex_network_resource))

        network_UUID = str(test_network_1_uri.split("/")[-1])

        time.sleep(10)

        search_string = 'AANAT-T3M'
        network_neighborhood = ndex.get_neighborhood_as_cx_stream(network_UUID, search_string, 1)
        self.assertTrue(network_neighborhood.status_code == 200)
        network_in_cx = network_neighborhood.text[0]

        t = type(network_in_cx)

        # get metadata








        # test delete_network
        del_network_return = ndex.delete_network(network_UUID)
        #self.assertTrue(del_network_return == '')



if __name__ == '__main__':
    unittest.main()


'''
{"data": [
          {"numberVerification":  [{"longNumber": 281474976710655}]},
          {"metaData": [{"idCounter": 4, "name": "nodes", "consistencyGroup": 2, "elementCount": 3, "version": "1.0", "properties": []},
                        {"idCounter": 5, "name": "edges", "consistencyGroup": 2, "elementCount": 2, "version": "1.0", "properties": []},
                        {"elementCount": 1, "properties": [], "version": "1.0", "consistencyGroup": 2, "name": "networkAttributes"},
                        {"elementCount": 7, "properties": [], "version": "1.0", "consistencyGroup": 2, "name": "nodeAttributes"},
                        {"elementCount": 6, "properties": [], "version": "1.0", "consistencyGroup": 2, "name": "edgeAttributes"},
                        {"elementCount": 1, "properties": [], "version": "1.0", "consistencyGroup": 2, "name": "ndexStatus"}]},
          {"networkAttributes": [{"v": "rudi", "n": "name"}]}, {"nodes": [{"@id": 1, "n": "MDFI"}]}, {"nodes": [{"@id": 2, "n": "BHLHE40"}]},
          {"nodes": [{"@id": 4, "n": "AANAT-T3M"}]}, {"edges": [{"i": "interacts_with", "s": 1, "@id": 2, "t": 4}]},
          {"edges": [{"i": "interacts_with", "s": 2, "@id": 5, "t": 4}]}, {"nodeAttributes": [{"v": "4188", "po": 1, "n": "Interactor_Gene_ID"},
                                                                                              {"v": "8553", "po": 2, "n": "Interactor_Gene_ID"},
                                                                                              {"v": "Non-disease variant", "po": 4, "n": "Category"},
                                                                                              {"v": "15_900207", "po": 4, "n": "Allele_ID"},
                                                                                              {"v": "NM_001088:c.8C>T", "po": 4, "n": "Mutation_RefSeq_NT"},
                                                                                              {"v": "15", "po": 4, "n": "Entrez_Gene_ID"},
                                                                                              {"v": "NP_001079:p.T3M", "po": 4, "n": "Mutation_RefSeq_AA"}]},
          {"edgeAttributes": [{"v": "1", "po": 2, "n": "In_Rolland_et_al_(Cell-2014)"}, {"v": "1", "po": 2, "n": "Y2H_score"}, {"v": "interacts_with", "po": 2, "n": "interaction"},
                              {"v": "1", "po": 5, "n": "In_Rolland_et_al_(Cell-2014)"}, {"v": "1", "po": 5, "n": "Y2H_score"}, {"v": "interacts_with", "po": 5, "n": "interaction"}]},
          {"provenanceHistory": [{"entity": {"creationEvent": {"eventType": "Neighborhood Query", "endedAtTime": 1484949549420, "startedAtTime": 1484949549420, "inputs":
              [{"creationEvent": {"inputs": [{"creationEvent": {"inputs": null, "endedAtTime": 1484003285186, "properties": [{"name": "user", "value": "j c"},
                                                                                                                             {"name": "user name", "value": "cj"}],
                                                                "startedAtTime": 1484003285186, "eventType": "Program Upload in CX"},
                                              "uri": "http://dev.ndexbio.org/v2/network/7a1833e3-d6c0-11e6-8835-06832d634f41/summary", "properties":
                                                  [{"name": "edge count", "value": "7"}, {"name": "node count", "value": "6"}, {"name": "dc:title", "value": "rudi"}]}],
                                  "endedAtTime": 1484949539281, "properties": [{"name": "user", "value": "ttt ttt"}, {"name": "user name", "value": "ttt"}],
                                  "startedAtTime": 1484949539281, "eventType": "Program Upload in CX"}, "uri": "http://dev.ndexbio.org/v2/network/a57c8d48-df5b-11e6-8835-06832d634f41/summary", "properties":
                  [{"name": "edge count", "value": "7"}, {"name": "node count", "value": "6"}, {"name": "dc:title", "value": "rudi"}]}]},
                                             "properties": [{"type": "SimplePropertyValuePair", "name": "query terms", "value": "AANAT\\-T3M"},
                                                            {"type": "SimplePropertyValuePair", "name": "query depth", "value": 1}]}}]},
          {"ndexStatus": [{"edgeCount": 7, "ndexServerURI": "http://dev.ndexbio.org", "creationTime": 1484949539281, "visibility": "PRIVATE", "modificationTime": 1484949539281,
                           "owner": "ttt", "readOnly": false, "externalId": "a57c8d48-df5b-11e6-8835-06832d634f41", "published": false, "nodeCount": 6}]}, {"status": [{"success": true, "error": ""}]}]}
'''