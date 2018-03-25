import mastodon
from html.parser import HTMLParser
import argparse
import math

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


# Configure command line arguments


class UserInterface():
    def __init__(self):
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
        self.args = p.parse_args()

    def login(self):
        '''logon to mastodon'''

        client_key = self.args.client_key
        client_secret = self.args.client_secret
        base_url= self.args.base_url
        user = self.args.user
        password = self.args.password

        self.mastodon = mastodon.Mastodon(client_id=client_key,
                                          client_secret=client_secret,
                                          api_base_url=base_url)
        self.mastodon.log_in(user, password, scopes=['read'])

    def getTootsOfUser(self, handle):
        ''' Recent toots of user `handle` '''
        #handle = self.args.handle
        account = self.mastodon.search(handle)['accounts'][0]
        return self.mastodon.account_statuses(account['id'])

    def getHomeToots(self):
        return self.mastodon.timeline_home()

    def getPublicToots(self):
        return self.mastodon.timeline_local()

    def getQuery(self):
        return self.args.query.split(" ")


class BM25():
    '''Implementation of the BM25 retrieval model'''

    def __init__(self, docfreqs, total_toots, avgdl):
        # BM25 parameters
        self.avgdl = avgdl
        self.total_toots = total_toots
        self.docfreqs = docfreqs
        self.bm25_b=0.75
        self.bm25_k1=1.2
        self.min_query_matches = 1  # adjust how many terms must be in a toot for it to show up in the search

    def bm25_term(self,q,tf, doc_length):
        ''' Score for a single search term '''
        df=self.docfreqs[q]
        idf = math.log(self.total_toots - df + 0.5) - math.log(df + 0.5)
        term1 = tf * (self.bm25_k1+1.0) / (tf + self.bm25_k1 * (1.0-self.bm25_b + self.bm25_b * doc_length/self.avgdl))

        return idf * term1

    def bm25_score(self, toot, query_terms):
        ''' Search score for a toot'''
        text = strip_tags(toot['content']).lower()
        if sum((1 for q in query_terms if text.count(q) > 0)) >= self.min_query_matches:
            doc_len = text.count(" ")
            score = sum((self.bm25_term(q, tf=text.count(q), doc_length=doc_len) for q in query_terms))
            return score
        else:
            return None


class Searcher():
    def __init__(self):
        pass

    def seed_background_model(self, toots, query_terms):
        '''collect statistics for the retrieval model.
        '''

        self.docfreqs = {q:0 for q in query_terms}
        doc_lens = []

        for toot in toots:
            text = strip_tags(toot['content'])
            for q in query_terms:
                self.docfreqs[q] += text.count(q)
            doc_lens.append(text.count(" "))

        self.avgdl = sum(doc_lens) / len(doc_lens)
        self.total_toots = len(user_interface.getHomeToots())

        self.model = BM25(self.docfreqs, self.total_toots, self.avgdl)

    def rank(self, toots, query_terms):
        # fetch and score toots, kick out dropped toots (None)
        scoredToots = [(toot, self.model.bm25_score(toot, query_terms)) for toot in toots]
        scoredToots = [ pair for  pair in scoredToots if pair[1] is not None]

        # sort descendingly by search score
        scoredToots.sort(key=lambda pair: -pair[1])
        return scoredToots



user_interface = UserInterface()
user_interface.login()

query_raw = user_interface.getQuery()

print("searching for terms: ", ", ".join(query_raw))


# parameters for the information retrieval model (BM25)
query_terms = [q.lower() for q in query_raw]  # normalize query terms for searching

searcher = Searcher()
searcher.seed_background_model(user_interface.getHomeToots(), query_terms)

scoredToots = searcher.rank(user_interface.getHomeToots(), query_terms)


# print
for (toot, score) in scoredToots[0:10]:
    print (f"({score}, id: {toot['id']})  {toot['content']} \n")



