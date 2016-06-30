#!/usr/bin/env python

import requests
import json
from requests_toolbelt import MultipartEncoder
import os

class Ndex:
    '''A class to facilitate communication with an NDEx server.'''
    def __init__(self, host = "http://public.ndexbio.org", username = None, password = None):
        '''Creates a connection to a particular NDEx server.

                :param host: The URL of the server.
                :type host: string
                :param username: The username of the NDEx account to use. (Optional)
                :type username: string
                :param password: The account password. (Optional)
                :type password: string
        '''
        self.debug = False
        if "localhost" in host:
            self.host = "http://localhost:8080/ndexbio-rest"
        else:
            self.host = host + "/rest"
        # create a session for this Ndex
        self.s = requests.session()
        if username and password:
            # add credentials to the session, if available
            self.s.auth = (username, password)

# Base methods for making requests to this NDEx

    def set_debug_mode(self, debug):
        self.debug = debug

    def debug_response(self, response):
        if self.debug:
            print("status code: " + str(response.status_code))
            if not response.status_code == requests.codes.ok:
                print("response text: " + response.text)

    def require_auth(self):
        if not self.s.auth:
            raise Exception("this method requires user authentication")

    def put(self, route, put_json):
        url = self.host + route
        if self.debug:
            print("PUT route: " + url)
            print("POST json: " + put_json)
        headers = {'Content-Type' : 'application/json;charset=UTF-8',
                   'Accept' : 'application/json',
                   'Cache-Control': 'no-cache',
                   }
        response = self.s.put(url, data = put_json, headers = headers)
        self.debug_response(response)
        response.raise_for_status()
        if response.status_code == 204:
            return ""
        return response.json()


    def post(self, route, post_json):
        url = self.host + route
        if self.debug:
            print("POST route: " + url)
            print("POST json: " + post_json)
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'Cache-Control': 'no-cache',
                   }
        response = self.s.post(url, data=post_json, headers=headers)
        self.debug_response(response)
        response.raise_for_status()
        if response.status_code == 204:
            return ""
        return response.json()

    def delete(self, route):
        url = self.host + route
        if self.debug:
            print("DELETE route: " + url)
        response = self.s.delete(url)
        self.debug_response(response)
        response.raise_for_status()
        if response.status_code == 204:
            return ""
        return response.json()

    def get(self, route, get_params = None):
        url = self.host + route
        if self.debug:
            print("GET route: " + url)
        response = self.s.get(url, params = get_params)
        self.debug_response(response)
        response.raise_for_status()
        if response.status_code == 204:
            return ""
        return response.json()

    # The stream refers to the Response, not the Request
    def get_stream(self, route, get_params = None):
        url = self.host + route
        if self.debug:
            print("GET stream route: " + url)
        response = self.s.get(url, params = get_params, stream = True)
        self.debug_response(response)
        response.raise_for_status()
        if response.status_code == 204:
            return ""
        return response

    # The stream refers to the Response, not the Request
    def post_stream(self, route, post_json):
        url = self.host + route
        if self.debug:
            print("POST stream route: " + url)
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'Cache-Control': 'no-cache',
                   }
        response = self.s.post(url, data=post_json, headers=headers, stream = True)
        self.debug_response(response)
        response.raise_for_status()
        if response.status_code == 204:
            return ""
        return response

    # The Request is streamed, not the Response
    def put_multipart(self, route, fields):
        url = self.host + route
        multipart_data = MultipartEncoder(fields=fields)
        if self.debug:
            print("PUT route: " + url)

        headers = {'Content-Type' : multipart_data.content_type,
                   'Accept' : 'application/json',
                   'Cache-Control': 'no-cache',
                   }
        response = self.s.put(url, data=multipart_data, headers=headers)
        self.debug_response(response)
        response.raise_for_status()
        if response.status_code == 204:
            return ""
        try:
            result = response.json()
        except ValueError:
            result = response.text
        return result

    # The Request is streamed, not the Response
    def post_multipart(self, route, fields):
        url = self.host + route
        multipart_data = MultipartEncoder(fields=fields)
        if self.debug:
            print("POST route: " + url)
        headers = {'Content-Type': multipart_data.content_type,
                   'Accept': 'application/json',
                   'Cache-Control': 'no-cache',
                   }
        response = self.s.post(url, data=multipart_data, headers=headers)
        self.debug_response(response)
        response.raise_for_status()
        if response.status_code == 204:
            return ""
        try:
            result = response.json()
        except ValueError:
            result = response.text
        return result

# Network methods

    # CX Methods
    # Create a network based on a stream from a source CX format
    def save_cx_stream_as_new_network (self, cx_stream, provenance=None):
        ''' Create a new network from a CX stream, optionally providing a provenance history object to be included in the new network.

        :param cx_stream: The network stream.
        :param provenance: The desired provenance history associated with the network.
        :return: The response.
        :rtype: `response object <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_
        '''
        self.require_auth()
        fields = {
        'CXNetworkStream': ('filename', cx_stream, 'application/octet-stream')
        }
        if provenance:
            if isinstance(provenance, dict):
                fields['provenance'] = json.dumps(provenance)
            else:
                fields['provenance'] = provenance

        route = '/network/asCX'

        return self.post_multipart(route, fields)

    # Create a network based on a JSON string or Dict in CX format
    def update_cx_network(self, cx_stream, network_id, provenance=None):
        '''Update the network specified by UUID network_id using the CX stream cx_stream.

        :param cx_stream: The network stream.
        :param network_id: The UUID of the network.
        :type network_id: str
        :param provenance: The desired provenance history associated with the network.
        :return: The response.
        :rtype: `response object <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_

        '''
        self.require_auth()
        fields = {
            'CXNetworkStream': ('filename', cx_stream, 'application/octet-stream')
        }
        if provenance:
            if isinstance(provenance, dict):
                fields['provenance'] = json.dumps(provenance)
            else:
                fields['provenance'] = provenance

        route = '/network/asCX/%s' % (network_id)


        return self.put_multipart(route, fields)

    # Get a CX stream for a network
    def get_network_as_cx_stream(self, network_id):
        '''Get the existing network with UUID network_id from the NDEx connection as a CX stream.

        :param network_id: The UUID of the network.
        :type network_id: str
        :return: The response.
        :rtype: `response object <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_

        '''
        route = "/network/%s/asCX" % (network_id)
        return self.get_stream(route)

    def get_neighborhood_as_cx_stream(self, network_id, search_string, search_depth=1, edge_limit=2500):
        ''' Get a CX stream for a subnetwork of the network specified by UUID network_id and a traversal of search_depth steps around the nodes found by search_string.

        :param network_id: The UUID of the network.
        :type network_id: str
        :param search_string: The search string used to identify the network neighborhood.
        :type search_string: str
        :param search_depth: The depth of the neighborhood from the core nodes identified.
        :type search_depth: int
        :param edge_limit: The maximum size of the neighborhood.
        :type edge_limit: int
        :return: The response.
        :rtype: `response object <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_

        '''
        route = "/network/%s/asCX/query" % (network_id)
        post_data = {'searchString': search_string,
                   'searchDepth': search_depth,
                   'edgeLimit': edge_limit}
        post_json = json.dumps(post_data)
        return self.post_stream(route, post_json=post_json)


    # Search for networks by keywords
    #    network    POST    /network/search/{skipBlocks}/{blockSize}    SimpleNetworkQuery    NetworkSummary[]
    def search_networks(self, search_string="", account_name=None, skip_blocks=0, block_size=100):
        ''' Search for networks based on the search_text, optionally limited to networks owned by the specified account_name.

        :param search_string: The text to search for.
        :type search_string: str
        :param account_name: The account to search
        :type account_name: str
        :param skip_blocks: The number of blocks to skip. Usually zero, but may be used to page results.
        :type skip_blocks: int
        :param block_size: The size of the block.
        :type block_size: int
        :return: The response.
        :rtype: `response object <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_

        '''
        route = "/network/search/%s/%s" % (skip_blocks, block_size)
        post_data = {"searchString" : search_string}
        if account_name:
            post_data["accountName"] = account_name
        post_json = json.dumps(post_data)
        return self.post(route, post_json)

    def find_networks(self, search_string="", account_name=None, skip_blocks=0, block_size=100):
        print("find_networks is deprecated, please use search_networks")
        return self.search_networks(search_string, account_name, skip_blocks, block_size)

    def search_networks_by_property_filter(self, search_parameter_dict="", account_name=None, limit=100):
        self.require_auth()
        route = "/network/searchByProperties"
        if account_name:
            search_parameter_dict["admin"] = account_name
        search_parameter_dict["limit"] = limit
        post_json = json.dumps(search_parameter_dict)
        return self.post(route, post_json)

    #    network    GET    /network/{networkUUID}       NetworkSummary
    def get_network_summary(self, network_id):
        ''' Gets information about a network.

        :param network_id: The UUID of the network.
        :type network_id: str
        :return: The response.
        :rtype: `response object <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_

        '''
        route = "/network/%s" % (network_id)
        return self.get(route)

    def get_task_by_id (self, task_id):
        route = "/task/%s" % (task_id)
        return self.get(route)

    def delete_network(self, network_id):
        self.require_auth()
        route = "/network/%s" % (network_id)
        return self.delete(route)

    def get_provenance(self, network_id):
        route = "/network/%s/provenance" % (network_id)
        return self.get(route)

    def set_provenance(self, network_id, provenance):
        self.require_auth()
        route = "/network/%s/provenance" % (network_id)
        if isinstance(provenance, dict):
            putJson = json.dumps(provenance)
        else:
            putJson = provenance
        return self.put(route, putJson)

    def set_network_flag(self, network_id, parameter, value):
        self.require_auth()
        route = "/network/%s/setFlag/%s=%s" % (network_id, parameter, value)
        return self.get(route)

    def set_read_only(self, network_id, value):
        self.require_auth()
        return self.set_network_flag(network_id, "readOnly", value)

    def set_network_properties(self, network_id, network_properties):
        self.require_auth()
        route = "/network/%s/properties" % (network_id)
        if isinstance(network_properties, list):
            putJson = json.dumps(network_properties)
        else:
            putJson = network_properties
        return self.put(route, putJson)

    def update_network_profile(self, network_id, network_profile):
        self.require_auth()
        route = "/network/%s/summary" % (network_id)
        if isinstance(network_profile, dict):
            postJson = json.dumps(network_profile)
        else:
            postJson = network_profile
        return self.post(route, postJson)

    def upload_file(self, filename):
        self.require_auth()
        fields = {

            'fileUpload': (filename, open(filename, 'rb'), 'application/octet-stream'),
            'filename': os.path.basename(filename)#filename
        }
        route = '/network/upload'
        return self.post_multipart(route, fields)