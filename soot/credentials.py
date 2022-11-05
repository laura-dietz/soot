from mastodon import Mastodon
from soot import config
import keyring
import random

class Credentials:
    def __init__(self,domain, config = config.Config()):
        self.domain = domain
        self.config = config
        self.id_client = "soot-client-id"
        self.secret_client = "soot-client-secret"
        self.secret_key = "soot-session-secret"

    def get_secret_session_key(self):
        secret = keyring.get_password(self.config.APP_NAME, self.secret_key)
        if secret is None:
            secret = hex(random.getrandbits(1024))
            keyring.set_password(self.config.APP_NAME, self.secret_key, secret)
            return secret
        else:
            return secret

    def client_register(self):
        if not self.is_client_registered():
            client_id, client_secret = Mastodon.create_app(self.config.APP_NAME,
                                                           api_base_url=self.domain,
                                                           scopes=['read'],
                                                           website=self.config.APP_WEBSITE)
            keyring.set_password(self.config.APP_NAME, self.id_client, client_id)
            keyring.set_password(self.config.APP_NAME, self.secret_client, client_secret)

    def get_client_id(self):
            return keyring.get_password(self.config.APP_NAME, self.id_client)

    def get_client_secret(self):
            return keyring.get_password(self.config.APP_NAME, self.secret_client)


    def is_client_registered(self):
        return keyring.get_password(self.config.APP_NAME, self.id_client) is not None and \
               keyring.get_password(self.config.APP_NAME, self.secret_client) is not None \


    def sent_oauth_register(self):
        masto = self.dummy_masto()
        access_url = masto.auth_request_url(client_id=self.get_client_id(), scopes=['read'])
        return access_url



    def dummy_masto(self):
        return Mastodon(client_id=self.get_client_id(), client_secret=self.get_client_secret(), api_base_url=self.domain)

    def create_masto(self,access_token):
        return Mastodon(client_id=self.get_client_id(), client_secret=self.get_client_secret(), api_base_url=self.domain, access_token=access_token)
        #return Mastodon(access_token=access_token)

