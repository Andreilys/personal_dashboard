import json
import urllib
import requests
import types


class MovesAPIError(Exception):
    """Raised if the Moves API returns an error."""
    pass

class MovesAPINotModifed(Exception):
    """Raised if the document requested is unmodified. Need the use of etag header"""
    pass

class MovesClient(object):
    """OAuth client for the Moves API"""
    api_url = "https://api.moves-app.com/api/1.1"
    app_auth_url = "moves://app/authorize"
    web_auth_uri = "https://api.moves-app.com/oauth/v1/authorize"
    token_url = "https://api.moves-app.com/oauth/v1/access_token"
    tokeninfo_url = "https://api.moves-app.com/oauth/v1/tokeninfo"
    
    
    
    def __init__(self, client_id=None, client_secret=None,
                 access_token=None, use_app=False):

        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.auth_url = self.app_auth_url if use_app else self.web_auth_uri
        self.use_app = use_app
        self._last_headers = None

    def parse_response(self, response):
        """Parse JSON API responses."""

        return json.loads(response.text)

    def build_oauth_url(self, redirect_uri=None, scope="activity location"):
        params = {
            'client_id': self.client_id,
            'scope': scope
        }

        if not self.use_app:
            params['response_type'] = 'code'

        if redirect_uri:
            params['redirect_uri'] = redirect_uri

        # Moves hates +s for spaces, so use %20 instead.
        encoded = urllib.urlencode(params).replace('+', '%20')
        return "%s?%s" % (self.auth_url, encoded)

    def get_oauth_token(self, code, **kwargs):

        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': kwargs.get('grant_type', 'authorization_code')
        }

        if 'redirect_uri' in kwargs:
            params['redirect_uri'] = kwargs['redirect_uri']
        response = requests.post(self.token_url, params=params)
        response = json.loads(response.content)
        try:
            return response['access_token']
        except:
            error = "<%(error)s>: %(error_description)s" % response
            raise MovesAPIError(error)

    def tokeninfo(self):
        
        params = {
            'access_token': self.access_token
        }

        response = requests.get(self.tokeninfo_url, params=params)
        response = json.loads(response.content)
        try:
            return response
        except:
            error = "<%(error)s>: %(error_description)s" % response
            raise MovesAPIError(error)


    def api(self, path, method='GET', **kwargs):

        params = kwargs['params'] if 'params' in kwargs else {}
        data = kwargs['data'] if 'data' in kwargs else {}

        if not self.access_token and 'access_token' not in params:
            raise MovesAPIError("You must provide a valid access token.")

        url = "%s/%s" % (self.api_url, path)
        if 'access_token' in params:
            access_token = params['access_token']
            del(params['access_token'])
        else:
            access_token = self.access_token

        headers = {
            "Authorization": 'Bearer ' + access_token
        }

        if 'etag' in params:
            headers['If-None-Match'] = params['etag']
            del(params['etag'])
        
        resp = requests.request(method, url,
                                data=data,
                                params=params,
                                headers=headers)
        if str(resp.status_code)[0] not in ('2', '3'):
            raise MovesAPIError("Error returned via the API with status code (%s):" %
                                resp.status_code, resp.text)
        if resp.status_code == 304:
            raise MovesAPINotModifed("Unmodified")
        
        self._last_headers = resp.headers
        return resp

    def get(self, path, **params):
        return self.parse_response(
            self.api(path, 'GET', params=params))

    def post(self, path, **data):
        return self.parse_response(
            self.api(path, 'POST', data=data))

    def set_first_date(self):
        if not self.first_date:
            response = self.user_profile()
            self.first_date = response['profile']['firstDate']

    def __getattr__(self, name):
        '''\
Turns method calls such as "moves.foo_bar(...)" into
a call to "moves.api('/foo/bar', 'GET', params={...})"
and then parses the response.
'''
        base_path = name.replace('_', '/')

        # Define a function that does what we want.
        def closure(*path, **params):
            'Accesses the /%s API endpoints.'
            path = list(path)
            path.insert(0, base_path)
            return self.parse_response(
                self.api('/'.join(path), 'GET', params=params)
                )

        # Clone a new method with the correct name and doc string.
        retval = types.FunctionType(
            closure.func_code,
            closure.func_globals,
            name,
            closure.func_defaults,
            closure.func_closure)
        retval.func_doc =  closure.func_doc % base_path

        # Cache it to avoid additional calls to __getattr__.
        setattr(self, name, retval)
        return retval

# Give Access to last attribute
_move_client_status = ['etag', 'x-ratelimit-hourlimit', 'x-ratelimit-hourremaining',
                       'x-ratelimit-minutelimit', 'x-ratelimit-minuteremaining']
for att in _move_client_status:
    att = att.replace('-', '_')
    setattr(MovesClient, att, property(lambda self,att=att: self._last_headers.get(att, None)
                                       if self._last_headers else att))
    
