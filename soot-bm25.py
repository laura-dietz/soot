import mastodon
from html.parser import HTMLParser
import argparse
import math
from soot_backend import *


class CmdLineUI(UserInterface):
    def __init__(self):

        super().__init__()
        p = argparse.ArgumentParser("soot-bm25", description="Mastodon search interface prototype!"
                                                             "First create new application under mastadon/Settings/Development, select read only, submit, then identify client key, secret, and token.")
        p.add_argument('--client-key', help=' and get client key')
        p.add_argument('--client-secret', help='client secret')
        p.add_argument('--access-token', help='client access token')
        p.add_argument('-u','--user', help='your user id')
        p.add_argument('-p','--password', help='your password')
        p.add_argument('--handle', help='the user handle of your account')
        p.add_argument('--base-url', default="mastodon.social", help="base url of your instance")
        p.add_argument('--query',help="free-text search query, space-separated. Example \"@friend Cool stuff #awesome\"  ")
        args = p.parse_args()
        self.client_key=args.client_key
        self.client_secret=args.client_secret
        self.base_url=args.base_url
        self.user=args.user
        self.password=args.password
        self.query=args.query



# Logon to mastodon
user_interface = CmdLineUI()



scoredToots = login_crawl_and_search(user_interface)
# poor woman's ugly output of relevant toots
for (toot, score) in scoredToots[0:10]:
    print (f"({score}, id: {toot['id']})  {toot['content']} \n")




