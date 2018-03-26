import mastodon
from html.parser import HTMLParser
import argparse
import math
from credentials import Credentials

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


creds = Credentials("soot")


class TootInterface():
    def __init__(self, masto):
        self.mastodon=masto

    def getHomeToots(self):
        return self.mastodon.timeline_home()

    def getPublicToots(self):
        return self.mastodon.timeline_local()




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
        df = self.docfreqs.get(q,0.0)
        #print('q',q,'df',df, 'totaltoots',self.total_toots)
        if tf == 0 or doc_length == 0 or df == self.total_toots:
            return 0.0
        else:

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
        self.colfreqs = {q:0 for q in query_terms}
        doc_lens = []

        for toot in toots:
            text = strip_tags(toot['content'])
            for q in query_terms:
                count = text.count(q)
                self.colfreqs[q] += count
                if(count>0):
                    self.docfreqs[q] += 1
            doc_lens.append(text.count(" "))

        self.avgdl = sum(doc_lens) / len(doc_lens)
        self.total_toots = len(toots)

        self.model = BM25(self.docfreqs, self.total_toots, self.avgdl)

    def rank(self, toots, query_terms):
        if not query_terms:
            return []
        else:
            # fetch and score toots, kick out dropped toots (None)
            scoredToots = [(toot, self.model.bm25_score(toot, query_terms)) for toot in toots]
            scoredToots = [ pair for  pair in scoredToots if pair[1] is not None]

            # sort descendingly by search score
            scoredToots.sort(key=lambda pair: -pair[1])
            return scoredToots




def crawl_and_search(user_interface, query_raw):

    # Fetch the search query
    print("searching for terms: ", ", ".join(query_raw))
    # parameters for the information retrieval model (BM25)
    query_terms = [q.lower() for q in query_raw]  # normalize query terms for searching


    # Create search model and initialize statistics
    # Currently only statistics for this query are collected
    searcher = Searcher()
    searcher.seed_background_model(user_interface.getHomeToots(), query_terms)


    # rank toots by relevance
    scoredToots = searcher.rank(user_interface.getHomeToots(), query_terms)
    return scoredToots
