from __future__ import absolute_import

import unittest
from os import path
import ndex.client as nc
import uuid
import time
import json

class NdexClientTestCase1(unittest.TestCase):

    def testConstructorException(self):
        with self.assertRaises(Exception):
            print "testing ndex client constructor."
            ndex = nc.Ndex(host="www.google.com", username="foo", password="bar")


class NdexClientTestCase2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._ndex = nc.Ndex(host="http://dev.ndexbio.org", username="pytest", password="pyunittest")
        here = path.abspath(path.dirname(__file__))
        with open(path.join(here, 'tiny_network.cx'),'r') as cx_file:
            cls._nrc = cls._ndex.save_cx_stream_as_new_network(cx_file)
            networkId = uuid.UUID('{'+cls._nrc[-36:] + '}')
            cls._networkId = str(networkId)

    @classmethod
    def tearDownClass(cls):
        cls._ndex.delete_network(cls._networkId)
        print "Network " + cls._networkId + " deleted from " + cls._ndex.username +" account " + cls._ndex.host

    #def setup(self):
    #    self.ndex = nc.Ndex(host="http://public.ndexbio.org", username="drh", passwor="drh")


    def testGetNetwork(self):
        summary = self._ndex.get_network_summary(self._networkId)
        self.assertEqual(summary.get(u'externalId'), self._networkId)
        print "get_network_summary() passed."

    def testGrantGroupPermission(self):
        ndex2 = nc.Ndex("http://dev.ndexbio.org", username='pytest2' , password = 'pyunittest')
        with self.assertRaises(Exception) as context:
            ndex2.get_network_summary(self._networkId)
#        print context.exception
        count = 0
        while count < 30 :
            try :
                self._ndex.update_network_group_permission('d7ef9957-de81-11e6-8835-06832d634f41', self._networkId, 'READ')
                count = 60
            except Exception as inst :
                d = json.loads(inst.response.content)
                if d.get('message').startswith("Can't modify locked network.") :
                    print "retry in 5 seconds(" + str(count) + ")"
                    count += 1
                    time.sleep(5)
                else :
                    raise inst

        summary = ndex2.get_network_summary(self._networkId)
        self.assertEqual(summary.get(u'externalId'), self._networkId)
        print "update_network_group_permission() passed."



class NdexClientTestCase3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._ndex = nc.Ndex(host="http://dev.ndexbio.org", username="pytest", password="pyunittest")
        here = path.abspath(path.dirname(__file__))
        with open(path.join(here, 'tiny_network.cx'),'r') as cx_file:
            cls._nrc = cls._ndex.save_cx_stream_as_new_network(cx_file)
            networkId = uuid.UUID('{'+cls._nrc[-36:] + '}')
            cls._networkId = str(networkId)

    @classmethod
    def tearDownClass(cls):
        cls._ndex.delete_network(cls._networkId)
        print "Network " + cls._networkId + " deleted from " + cls._ndex.username +" account " + cls._ndex.host

    #def setup(self):
    #    self.ndex = nc.Ndex(host="http://public.ndexbio.org", username="drh", passwor="drh")

    def testGrantUserPermission(self):
        ndex2 = nc.Ndex("http://dev.ndexbio.org", username='pytest2' , password = 'pyunittest')
        with self.assertRaises(Exception) as context:
            ndex2.get_network_summary(self._networkId)
#        print context.exception
        count = 0
        while count < 30 :
            try :
                self._ndex.update_network_user_permission('0a9d3b58-de82-11e6-8835-06832d634f41', self._networkId, 'READ')
                count = 60
            except Exception as inst :
                d = json.loads(inst.response.content)
                if d.get('message').startswith("Can't modify locked network.") :
                    print "retry in 5 seconds(" + str(count) + ")"
                    count += 1
                    time.sleep(5)
                else :
                    raise inst

        summary = ndex2.get_network_summary(self._networkId)
        self.assertEqual(summary.get(u'externalId'), self._networkId)
        print "update_network_user_permission() passed."

