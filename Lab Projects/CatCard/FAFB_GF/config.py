#Enter user catmaid info into token and password
#X-Authorization: Token "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
from requests.auth import AuthBase

class CatmaidApiTokenAuth(AuthBase):
    """Attaches HTTP X-Authorization Token headers to the given Request."""
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['X-Authorization'] = 'Token {}'.format(self.token)
        return r

project_id = 1

token = "d40cbc75a9fc777895aea4bfd1c1e02930378769"              #enter your token generated in CATMAID here
http_password = 'tenshawe'      #enter your CATMAID login password here