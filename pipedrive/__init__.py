# -*- coding: utf-8 -*-

from httplib2 import Http
from urllib import urlencode
import json
from copy import copy

PIPEDRIVE_API_URL = "https://api.pipedrive.com/v1/"

class PipedriveError(Exception):
    def __init__(self, response):
        self.response = response
    def __str__(self):
        return str(self.response)

class IncorrectLoginError(PipedriveError):
    pass

class Pipedrive(object):
    '''
    Provides an interface for PipeDrive's API.
    Official Documentation for PipeDrive's API: https://developers.pipedrive.com/v1

    When looking at the __getattr__() wrapper or _request():
        endpoint = What you are making a request towards. e.g. "persons".
        data = Dictionary of what to send.
        method = HTTP Method to use. GET, POST, PUT, and DELETE are whats supported

    GET: pipedrive.persons({'method': 'GET'})
    POST: pipedrive.persons({'method': 'POST', 'name': 'YAY', 'email': [{'value': 'yay@pleasework.com'}]})

    '''

    def _request(self, endpoint, data, method="POST"):
        if self.api_token:
            data = copy(data)
            qs = "%s%s?api_token=%s" % (PIPEDRIVE_API_URL, endpoint, self.api_token)
        else:
            #TODO throw error
            pass

        #In the below request, it assumes you entered the data 'correctly'
        # e.g. pipdrive.persons({'method': 'POST', 'name':
        if method in ["POST", "PUT"]:
            response, data = self.http.request(qs,
                                               method,
                                               body=json.dumps(data),
                                               headers={'Content-Type': 'application/json'}
                                              )
        else:
            response, data = self.http.request(qs, method)

        return json.loads(data)

    def __init__(self, login = None, password = None):
        self.http = Http()
        if password:
            response = self._request("/auth/login", {"login": login, "password": password})

            if 'error' in response:
                raise IncorrectLoginError(response)

            self.api_token = response['authorization'][0]['api_token']
        else:
            # Assume that login is actually the api token
            self.api_token = login

    def __getattr__(self, endpoint):
        def wrapper(data):
            if 'method' in data:
                method = data['method']
                del data['method']
            else:
                method = "POST"
            response = self._request(endpoint, data, method)
            if 'error' in response:
                raise PipedriveError(response)
            return response
        return wrapper
