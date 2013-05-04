from httplib2 import Http
import json
from copy import copy
from string import upper

PIPEDRIVE_API_URL = "https://api.pipedrive.com/v1/"

#TODO remove
class PipedriveError(Exception):
    def __init__(self, response):
        self.response = response
    def __str__(self):
        return str(self.response)

#TODO remove
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

    POST: pipedrive.persons({'method': 'POST', 'name': 'YAY', 'email': [{'value': 'yay@pleasework.com'}]})
    PUT: pipedrive.persons({'method': 'PUT', 'name': 'Roger', 'id': 23})
    DELETE: pipedrive.persons({'method': 'DELETE', 'id': 23})
    GET: pipedrive.persons({'method': 'GET'})
    '''

    def _request(self, endpoint, data, method="POST"):
        if self.api_token:
            method = upper(method)
            if method in ["POST", "GET"]:
                qs = "%s%s?api_token=%s" % (PIPEDRIVE_API_URL, endpoint, self.api_token)
            elif method in ["PUT", "DELETE"]:
                qs = "%s%s/%s?api_token=%s" % (PIPEDRIVE_API_URL, endpoint, data['id'], self.api_token)

        else:
            #TODO throw error
            pass

        #In the below request, it assumes you entered the data 'correctly'
        # e.g. pipdrive.persons({'method': 'POST', 'name': 'Roger'})
        if method in ["POST", "PUT"]:
            response, data = self.http.request(qs,
                                               method,
                                               body=json.dumps(data),
                                               headers={'Content-Type': 'application/json'})
        else: #'GET' or 'DELETE'
            response, data = self.http.request(qs, method)

        return json.loads(data)

    def __init__(self, login = None, password = None):
        self.http = Http()
        if password:
            response = self._request("/auth/login", {"login": login, "password": password})

            if 'error' in response: #TODO don't use custom Exceptions
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
                raise PipedriveError(response) #TODO don't use custom Exceptions
            return response
        return wrapper
