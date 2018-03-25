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


client_key = args.client_key
client_secret = args.client_secret
base_url= args.base_url
user = args.user
password = args.password
handle = args.handle

query_raw = args.query.split(" ")

print("searching for terms: ", ", ".join(query_raw))


# parameters for the information retrieval model (BM25)

bm25_b=0.75
bm25_k1=1.2

min_query_matches = 1  # adjust how many terms must be in a toot for it to show up in the search
query_terms = [q.lower() for q in query_raw]  # normalize query terms for searching


# logon to mastodon

m = mastodon.Mastodon(client_id=client_key,
                      client_secret=client_secret,
                      api_base_url=base_url)
m.log_in(user, password, scopes=['read'])
account = m.search(handle)['accounts'][0]



# collect statistics for the retrieval model.
# Here: all fetched toots
# Should be using public sources

docfreqs = {q:0 for q in query_terms}
doc_lens = []

for toot in m.account_statuses(account['id']):
    text = strip_tags(toot['content'])
    for q in query_terms:
        docfreqs[q] += text.count(q)
    doc_lens.append(text.count(" "))

avgdl = sum(doc_lens) / len(doc_lens)
total_toots = len(m.account_statuses(account['id']))


# Implementation of the BM25 retrieval model

def bm25_term(q,tf, doc_length):
    ''' Score for a single search term '''
    df=docfreqs[q]
    idf = math.log(total_toots - df + 0.5) - math.log(df + 0.5)
    term1 = tf * (bm25_k1+1.0) / (tf + bm25_k1 * (1.0-bm25_b + bm25_b * doc_length/avgdl))

    return idf * term1

def bm25_score(toot):
    ''' Search score for a toot'''
    text = strip_tags(toot['content']).lower()
    if sum((1 for q in query_terms if text.count(q) > 0)) >= min_query_matches:
        doc_len = text.count(" ")
        score = sum((bm25_term(q, tf=text.count(q), doc_length=doc_len) for q in query_terms))
        return score
    else:
        return None

# fetch and score toots, kick out dropped toots (None)
scoredToots = [(toot, bm25_score(toot)) for toot in m.account_statuses(account['id'])]
scoredToots = [ pair for  pair in scoredToots if pair[1] is not None]

# sort descendingly by search score
scoredToots.sort(key=lambda pair: -pair[1])


# print
for (toot, score) in scoredToots[0:10]:
    print (f"({score}, id: {toot['id']})  {toot['content']} \n")



