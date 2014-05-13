from httplib2 import Http
from json import dumps, loads
from types import DictType

PIPEDRIVE_API_URL = "https://api.pipedrive.com/v1/"

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
    or
    GET: pipedrive.persons({'method': 'GET', 'id': 23})
    '''
    def _request(self, endpoint, data, method="POST"):
        method = method.upper()
        endpoint = endpoint.replace('_','/') # Allow for find methods, and be pythonic
        if method in ["POST", "GET"]: #for if it is a "GET" all request.
            qs = "%s%s?api_token=%s" % (PIPEDRIVE_API_URL, endpoint, self.api_token)
        if method in ["PUT", "DELETE"] or 'id' in data: #This will work for GETing by 'id'
            qs = "%s%s/%s?api_token=%s" % (PIPEDRIVE_API_URL, endpoint, data['id'], self.api_token)

        #In the below request, it assumes you entered the data 'correctly'
        # e.g. pipdrive.persons({'method': 'POST', 'name': 'Roger'})
        if method in ["POST", "PUT"]:
            response, data = self.http.request(qs,
                                               method,
                                               body=dumps(data),
                                               headers={'Content-Type': 'application/json'})
        else: #'GET' or 'DELETE'
            response, data = self.http.request(qs, method)

        return loads(data)

    def __init__(self, login = None, password = None):
        self.http = Http()
        if login is None:
            raise Exception('Must include either login/password or API key when instantiating a Pipedrive object')
        if password:
            response = self._request("/auth/login", {"login": login, "password": password})

            if 'error' in response:
                raise ValueError(response)

            self.api_token = response['authorization'][0]['api_token']
        else:
            # Assume that login is actually the api token
            self.api_token = login

    def __getattr__(self, endpoint):
        def wrapper(data):
            if type(data) is not DictType:
                raise TypeError('Check your data. This function only accepts dictionaries.')
            if 'method' in data:
                method = data['method']
                del data['method']
            else:
                method = "POST"
            response = self._request(endpoint, data, method)
            if 'error' in response:
                raise ValueError(response)
            return response
        return wrapper
