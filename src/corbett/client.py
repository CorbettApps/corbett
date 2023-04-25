import requests
from corbett import config


class Client:

    def __init__(self, token=None, host=config.api_host):
        self.token = token
        self.host = host
        self.verify = not ('api-dev' in self.host)

    def send(self, method, route, json=None, headers=None):
        url = f"{self.host}{route}"
        default_headers = self.default_headers()
        if headers:
            default_headers.update(headers)
        resp = requests.request(method=method, url=url, json=json, headers=default_headers, timeout=10.0, verify=self.verify)
        return resp

    def default_headers(self):
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        return headers

    def healthcheck(self):
        """
        Query the public /healthcheck route
        """

        return self.send('GET', '/healthcheck')

    def register(self, email, password):
        """
        Register a new user
        """

        return self.send('POST', '/users', json={
            "email": email,
            "password": password
        })

    def login(self, email, password):
        """
        Log in an existing user
        """

        return self.send('POST', '/login', json={
            "email": email,
            "password": password
        })
    
    def whoami(self):
        """
        Retrieve information about the logged in user. Requires that the `profile`
        has already been set.
        """

        return self.send('GET', '/whoami')
    
    def api_key(self):
        """
        Retrieve the user's API key
        """

        return self.send('GET', '/apikey')

    def register_app(self, app_type):
        return self.send('POST', '/apps', json={
            'app_type': app_type
        })

    def get_app(self, app_id):
        return self.send('GET', f'/apps/{app_id}')
