from flask import Flask, render_template, request
from soot_backend import *

app = Flask(__name__)


class FlaskUI(UserInterface):
    def __init__(self):
        super().__init__()
        p = argparse.ArgumentParser("soot-flask", description="Mastodon search interface prototype!"
                                                             "First create new application under mastadon/Settings/Development, select read only, submit, then identify client key, secret, and token.")
        p.add_argument('--client-key', help=' and get client key')
        p.add_argument('--client-secret', help='client secret')
        p.add_argument('--access-token', help='client access token')
        p.add_argument('-u','--user', help='your user id')
        p.add_argument('-p','--password', help='your password')
        p.add_argument('--handle', help='the user handle of your account')
        p.add_argument('--base-url', default="mastodon.social", help="base url of your instance")
        args = p.parse_args()
        self.client_key=args.client_key
        self.client_secret=args.client_secret
        self.base_url=args.base_url
        self.user=args.user
        self.password=args.password


user_interface = FlaskUI()


user_interface.login()


@app.route('/')
def index():
    return render_template('index.html', results=[], query=None)

@app.route('/query')
def query():
    query_raw = request.args['q'].split(" ")

    # Fetch the search query
    # query_raw = "@deeds people"# response.args.query
    print("searching for terms: ", query_raw)
    # parameters for the information retrieval model (BM25)
    query_terms = [q.lower() for q in query_raw]  # normalize query terms for searching


    # Create search model and initialize statistics
    # Currently only statistics for this query are collected
    searcher = Searcher()
    searcher.seed_background_model(user_interface.getHomeToots(), query_terms)


    # rank toots by relevance
    scoredToots = searcher.rank(user_interface.getHomeToots(), query_terms)
    toot_ranking = [{'content':toot['content'], 'author': toot['account']['username']} for (toot,score) in scoredToots]
    print(toot_ranking)

    #return render_template('search-ninja.html', query=" ".join(query_terms), result=toot_ranking)
    return render_template('index.html', toots=toot_ranking, query=request.args['q'])



app.run()
