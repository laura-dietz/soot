from flask import Flask, render_template, request , redirect, session
from soot.backend import *

DEFAULT_BASE_URL = 'https://mastodon.social'

app = Flask(__name__)
app.config['CREDS'] = Credentials(DEFAULT_BASE_URL)

def is_authenticated():
    return session.get('access_token') is not None

@app.route('/')
def index():
    return render_template('index.html', results=[], registered=is_authenticated())

@app.route('/register')
def register():
    creds = app.config['CREDS']
    return redirect(creds.sent_oauth_register())

@app.route('/authenticate')
def authenticate():
    auth_code = request.args['access_token']
    creds = app.config['CREDS']
    masto = creds.dummy_masto()
    access_token = masto.log_in(code=auth_code, scopes=['read'], to_file="soot.token")
    session['access_token'] = access_token
    return redirect('/')

@app.route('/logout')
def logout():
    session.__delitem__('access_token')
    creds = app.config['CREDS']
    masto = creds.dummy_masto()
    return render_template('index.html', results=[], query=None, registered=is_authenticated())

@app.route('/query')
def query():
    print('access_token', session.get('access_token'))
    query_raw = request.args['q'].split(" ")
    creds = app.config['CREDS']
    masto = creds.create_masto(session['access_token'])
    user_interface = TootInterface(masto)

    # Fetch the search query
    print("searching for terms: ", query_raw)

    # parameters for the information retrieval model (BM25)
    query_terms = [q.lower() for q in query_raw]  # normalize query terms for searching


    # Create search model and initialize statistics
    # Currently only statistics for this query are collected
    searcher = Searcher()
    searcher.seed_background_model(user_interface.getHomeToots(), query_terms)

    def getVerb(toot):
        if toot['reblog'] is not None:
             return "boosted"
        elif (toot['in_reply_to_id'] is not None):
            return "replied"
        else:
            return "tooted"


    # rank toots by relevance
    scoredToots = searcher.rank(user_interface.getHomeToots(), query_terms)
    for (toot, score) in scoredToots[0:10]:
        print(toot)

    toot_ranking = [{'content': toot['content']
                        , 'author': toot['account']['username']
                        , 'uri':toot['url']
                        , 'verb':getVerb(toot)
                     } for (toot,score) in scoredToots if not toot['muted']]

    return render_template('index.html', toots=toot_ranking, query=request.args['q'], base_url=creds.domain, registered=is_authenticated())

def main():
    p = argparse.ArgumentParser("soot-bm25-server", description="Mastodon web search interface"
                                                         "First create new application under mastadon/Settings/Development, select read only, submit, then identify client key, secret, and token.")

    p.add_argument('--access-token', help='client access token')
    p.add_argument('--base-url', help="base url of your mastodon instance", default=DEFAULT_BASE_URL)
    p.add_argument('--host',help="public facing web hostname", default='0.0.0.0')
    p.add_argument('--port',help="public facing web port", default=5000)
    p.add_argument('--client-id',help="Soot client ID (register one)", default='5a2d74cbb65b43ed8be11e72de8f856948a997f5bccc537ccc5c5b69b53687d0')
    p.add_argument('--client-secret',help="Soot client secret (register)", default="469ff3d723779fb43878f41fb6cdd07b43f56af30963ca455388afce4140cacf")
    args = p.parse_args()

    creds = Credentials(args.base_url)
    if not creds.is_client_registered():
        creds.client_register()

    app.config['CREDS'] = creds
    app.secret_key = creds.get_secret_session_key()
    app.run(host=args.host, port=args.port)
    

if __name__ == '__main__':
    main()
