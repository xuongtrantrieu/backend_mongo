from utils import get_dict
from google_auth_oauthlib import flow
from os import getenv
from os.path import join as join_path
from settings import BASE_DIR
from . import *
import requests


class GoogleOAuth:
    CLIENT_FILE_NAME = getenv('GOOGLE_CLIENT_FILE_NAME') or ''
    CLIENT_FILE_PATH = join_path(BASE_DIR, CLIENT_FILE_NAME)
    AUTH_TOKEN_HEADER = getenv('GOOGLE_AUTH_TOKEN_HEADER') or 'Bearer'
    API_KEY = getenv('GOOGLE_API_KEY') or ''
    SCOPES = ['https://www.googleapis.com/auth/userinfo.profile',
              'openid', 'https://www.googleapis.com/auth/userinfo.email']
    GET_PROFILE_BASE_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'

    def __init__(self):
        self.credential = None
        self.response = {}
        self.note = ''

    @property
    def email(self):
        return self.response.get('email') or ''

    @classmethod
    def build_redirect_uri(cls, base_url=''):
        return f'{base_url}?provider={GOOGLE_OAUTH}'

    @classmethod
    def get_login_url(cls, base_url):
        auth_flow = flow.Flow.from_client_secrets_file(cls.CLIENT_FILE_PATH, scopes=cls.SCOPES)
        auth_flow.redirect_uri = cls.build_redirect_uri(base_url)
        authorization_url, _ = auth_flow.authorization_url(access_type='offline', includes_granted_scopes='true')

        return authorization_url

    def exchange_for_tokens(self, request):
        state = request.args.get('state') or ''
        redirect_uri = self.__class__.build_redirect_uri(request.base_url)

        auth_flow = flow.Flow.from_client_secrets_file(
            self.CLIENT_FILE_PATH, scopes=self.SCOPES,
            state=state,
        )
        auth_flow.redirect_uri = redirect_uri
        authorization_response = request.url
        try:
            auth_flow.fetch_token(authorization_response=authorization_response)
        except Exception as err:
            self.note = str(err)
            return self

        self.credential = get_dict(auth_flow.credentials)
        google_token = self.credential['token']

        get_profile_url = f'{self.GET_PROFILE_BASE_URL}?key={self.API_KEY}'
        get_profile_headers = dict(
            authorization=f'{self.AUTH_TOKEN_HEADER} {google_token}'
        )
        self.response = requests.get(get_profile_url, headers=get_profile_headers).json()

        return self
