from social_core.backends.oauth import BaseOAuth2
import urllib

class Cernauth2(BaseOAuth2):


    """CERN OAuth authentication backend"""
    name = 'cernauth2'
    AUTHORIZATION_URL = 'https://oauth.web.cern.ch/OAuth/Authorize'  #'https://github.com/login/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://oauth.web.cern.ch/OAuth/Token' #'https://github.com/login/oauth/access_token'
    SCOPE_SEPARATOR = ','
    REDIRECT_STATE = False
    EXTRA_DATA = [
        ('id', 'id'),
        ('expires', 'expires')
    ]

    def get_user_details(self, response):
         """Return user details from GitHub account"""
         return {'username': response.get('username'),
                 'email': response.get('email') or '',
                 'first_name': response.get('first_name'),
                 'last_name' : response.get('last_name'),
                 'federation' : response.get('federation'),
                 'name' : response.get('name'),
                 }

    # def user_data(self, access_token, *args, **kwargs):
    #     """Loads user data from service"""
    #     url = 'https://oauthresource.web.cern.ch/api/User?' + urllib.urlencode({
    #         'access_token': access_token
    #     })
    #     return self.get_json(url)



    def user_data(self, access_token, *args, **kwargs):
        """Load user data from the service"""
        return self.get_json(
            'https://oauthresource.web.cern.ch/api/User',
            headers=self.get_auth_header(access_token)
        )

    def get_auth_header(self, access_token):
        return {'Authorization': 'Bearer {0}'.format(access_token)}