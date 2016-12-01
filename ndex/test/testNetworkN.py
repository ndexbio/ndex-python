__author__ = 'aarongary'

import unittest
from ndex.networkn import NdexGraph, FilterSub

class NetworkNTests(unittest.TestCase):
    #==============================
    # TEST LARGE NETWORK
    #==============================
    def test_data_to_type(self):
        self.assertTrue(self, NdexGraph.data_to_type('true','boolean'))
        print type(NdexGraph.data_to_type('1.3','double'))
        print type(NdexGraph.data_to_type('1.3','float'))
        print type(NdexGraph.data_to_type('1','integer'))
        print type(NdexGraph.data_to_type('1','long'))
        print type(NdexGraph.data_to_type('1','short'))
        print type(NdexGraph.data_to_type('1','string'))
        list_of_boolean = type(NdexGraph.data_to_type('["true","false"]','list_of_boolean'))
        print list_of_boolean

        list_of_double = NdexGraph.data_to_type('[1.3,1.4]','list_of_double')
        print list_of_double

        list_of_float = NdexGraph.data_to_type('[1.3,1.4]','list_of_float')
        print list_of_float

        list_of_integer = NdexGraph.data_to_type('[1,4]','list_of_integer')
        print list_of_integer

        list_of_long = NdexGraph.data_to_type('[1,4]','list_of_long')
        print list_of_long

        list_of_short = NdexGraph.data_to_type('[1,4]','list_of_short')
        print list_of_short

        list_of_string = NdexGraph.data_to_type(['abc'],'list_of_string')
        print list_of_string


