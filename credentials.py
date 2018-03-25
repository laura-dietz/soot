#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Attribution to:

    Mastodome - Desktop Client for Mastodon
    Copyright (C) 2018 Bobby Moss bob[at]bobstechsite.com
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from mastodon import Mastodon
import config
import keyring


class Credentials:

    def __init__(self, domain):
        self.id_client = "cid-" + domain
        self.secret_client = "csec-" + domain
        self.secret_user = "usec-" + domain
        self.domain = domain
        self.config = config.Config()

    def is_client_registered(self):
        return keyring.get_password(self.config.APP_NAME, self.id_client) is not None and \
               keyring.get_password(self.config.APP_NAME, self.secret_client) is not None

    def client_register(self):
        if not self.is_client_registered():
            client_id, client_secret = Mastodon.create_app(self.config.APP_NAME,
                                                           api_base_url=self.domain,
                                                           scopes=['read', 'write', 'follow'],
                                                           website=self.config.APP_WEBSITE)
            keyring.set_password(self.config.APP_NAME, self.id_client, client_id)
            keyring.set_password(self.config.APP_NAME, self.secret_client, client_secret)

    def is_user_registered(self):
        return keyring.get_password(self.config.APP_NAME, self.secret_user) is not None

    def user_register(self, cusername=None, cpassword=None):
        if not self.is_client_registered():
            raise Exception("Client app has not been registered for this domain yet")

        if not self.is_user_registered():
            mastodon = Mastodon(
                client_id=keyring.get_password(self.config.APP_NAME, self.id_client),
                client_secret=keyring.get_password(self.config.APP_NAME, self.secret_client),
                api_base_url=self.domain
            )

            user_secret = mastodon.log_in(
                username=cusername,
                password=cpassword,
                scopes=['read', 'write', 'follow']
            )
            keyring.set_password(self.config.APP_NAME, self.secret_user, user_secret)

    def get_new_session(self):
        if not self.is_client_registered():
            raise Exception("Client app has not been registered for this domain yet")

        if not self.is_user_registered():
            raise Exception("User has not authenticated with this domain yet")

        return Mastodon(client_id=keyring.get_password(self.config.APP_NAME, self.id_client),
                        client_secret=keyring.get_password(self.config.APP_NAME, self.secret_client),
                        access_token=keyring.get_password(self.config.APP_NAME, self.secret_user),
                        api_base_url=self.domain
                        )

    def user_logout(self):
        keyring.delete_password(self.config.APP_NAME, self.secret_user)