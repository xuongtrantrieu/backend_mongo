from utils import get_dict
from google_auth_oauthlib import flow
from os import getenv as get_env
from os.path import join as join_path
from settings import BASE_DIR, LOGGER
from time import time
from hashlib import md5
from . import *
import requests


class OAuth:
    def __init__(self, provider='', request=None):
        self.request = request
        self.engine = None
        self.auth = None
        self.decide_engine(provider)

    def decide_engine(self, provider):
        if provider == GOOGLE_OAUTH:
            self.engine = GoogleOAuth
        elif provider == FACEBOOK_OAUTH:
            self.engine = FacebookOAuth

    def get_auth(self, *args, **kwargs):
        if not self.auth:
            provider = self.request.args.get('provider')
            self.decide_engine(provider)
        self.auth = self.engine().get_auth(self.request, *args, **kwargs) if self.engine else None
        return self.auth

    def get_login_url(self, *args, **kwargs):
        return self.engine.get_login_url(*args, **kwargs) if self.engine else None


class GoogleOAuth:
    CLIENT_FILE_NAME = get_env('GOOGLE_CLIENT_FILE_NAME') or ''
    CLIENT_FILE_PATH = join_path(BASE_DIR, CLIENT_FILE_NAME)
    AUTH_TOKEN_HEADER = get_env('GOOGLE_AUTH_TOKEN_HEADER') or 'Bearer'
    API_KEY = get_env('GOOGLE_API_KEY') or ''
    SCOPES = ['https://www.googleapis.com/auth/userinfo.profile',
              'openid', 'https://www.googleapis.com/auth/userinfo.email']
    GET_PROFILE_BASE_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'

    def __init__(self):
        self.credential = {}
        self.response = {}
        self.note = ''

    @property
    def provider(self):
        return GOOGLE_OAUTH

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

    def get_auth(self, request):
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


class FacebookOAuth:
    LOGIN_URI = 'https://www.facebook.com/v3.3/dialog/oauth?client_id={app_id}&redirect_uri={redirect_uri}&state={state_param}&scope=email'
    EXCHANGE_TOKEN_URI = 'https://graph.facebook.com/v3.3/oauth/access_token?client_id={app_id}&redirect_uri={redirect_uri}&client_secret={app_secret}&code={code_parameter}'
    APP_ACCESS_TOKEN_URI = 'https://graph.facebook.com/oauth/access_token?client_id={app_id}&client_secret={app_secret}&grant_type=client_credentials'
    INSPECT_TOKEN_URI = 'https://graph.facebook.com/debug_token?input_token={token}&access_token={access_token}'
    GET_PROFILE_URI = 'https://graph.facebook.com/{user_id}?fields=email&access_token={token}'
    APP_ID = get_env('FACEBOOK_APP_ID') or ''

    def __init__(self):
        self.credential = {}
        self.response = {}
        self.note = ''

    @classmethod
    def build_state(cls):
        return md5(str(time()).encode()).hexdigest()

    @classmethod
    def build_redirect_uri(cls, base_url=''):
        return f'{base_url}?provider={FACEBOOK_OAUTH}'

    @classmethod
    def get_login_url(cls, base_url):
        redirect_uri = cls.build_redirect_uri(base_url)
        state = cls.build_state()
        authorization_url = cls.LOGIN_URI.format(
            app_id=cls.APP_ID,
            redirect_uri=redirect_uri,
            state_param=state,
        )

        return authorization_url

    def get_auth(self, request):
        code = request.args.get('code') or ''
        redirect_uri = self.build_redirect_uri(request.base_url)
        app_secret = get_env('FACEBOOK_APP_SECRET') or ''

        exchange_token_uri = self.EXCHANGE_TOKEN_URI.format(
            app_id=self.APP_ID,
            redirect_uri=redirect_uri,
            app_secret=app_secret,
            code_parameter=code,
        )
        self.credential = requests.get(exchange_token_uri).json()
        token = self.credential.get('access_token') or ''
        if not token:
            self.note = 'cannot get token | {}'.format(self.credential)
            return self

        app_access_token_uri = self.APP_ACCESS_TOKEN_URI.format(
            app_id=self.APP_ID,
            app_secret=app_secret,
        )
        app_access_token_response = requests.get(app_access_token_uri).json()
        app_access_token = app_access_token_response.get('access_token') or ''
        if not app_access_token:
            self.note = 'cannot get app access token | {}'.format(app_access_token_response)
            return self

        inspect_token_uri = self.INSPECT_TOKEN_URI.format(
            token=token,
            access_token=app_access_token,
        )
        inspect_result = requests.get(inspect_token_uri).json()
        user_id = (inspect_result.get('data') or {}).get('user_id') or ''
        if not user_id:
            self.note = 'token is invalid | {}'.format(inspect_result)
        self.credential.update(dict(user_id=user_id))

        get_profile_uri = self.GET_PROFILE_URI.format(
            user_id=user_id,
            token=token,
        )
        self.response = requests.get(get_profile_uri).json()

        return self

    @property
    def email(self):
        return self.response.get('email') or ''

    @property
    def provider(self):
        return FACEBOOK_OAUTH
