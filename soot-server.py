from flask import Flask, render_template, request , redirect
from soot_backend import *

app = Flask(__name__)

global masto

class FlaskUI(UserInterface):
    def __init__(self, mastodon):
        super().__init__(mastodon)
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


creds = Credentials("mastodon.social")
# creds.client_register()
# creds.user_register(args.user, args.password)


def is_registered():
    return creds.is_authenticated() #and creds.is_user_registered()

#
# if is_registered():
#     masto = creds.get_new_session()
# else:
#     creds.client_register()
#     masto = creds.get_new_session()

# user_interface.login()

@app.route('/')
def index():
    return render_template('index.html', results=[], query=None, registered=creds.is_authenticated())


@app.route('/register')
def register():
    print("Request auth: ", creds.sent_oauth_register())
    return redirect(creds.sent_oauth_register())




@app.route('/authenticate')
def authenticate():
    auth_code = request.args['access_token']
    masto = creds.dummy_masto()
    access_token = masto.log_in(code=auth_code, scopes=['read'], to_file="soot.token")

    creds.store_access_token(access_token)


    return render_template('index.html', results=[], query=None, is_registered=creds.is_authenticated())


#
# @app.route('/access_token')
# def access_token():
#     access_token = request.args['access_token']
#     creds.store_access_token(access_token)
#     masto = creds.create_masto(access_token)
#
#
#     return render_template('index.html', results=[], query=None, is_registered=creds.is_authenticated())


#
#
#
# @app.route('/auth_token')
# def auth_token():
#     print("auth token")
#     print(request.args)
#



@app.route('/logout')
def logout():
    creds.store_access_token(None)
    masto = creds.dummy_masto()
    return render_template('index.html', results=[], query=None, registered=is_registered())

#
# @app.route('/register_client')
# def clientregister():
#     creds.client_register()
#     return render_template('index.html', results=[], query=None, is_registered=is_registered())
#
#
# @app.route('/register')
# def register():
#     user = request.args['user']
#     passwd = request.args['password']
#     creds.client_register()
#     creds.user_register(user, passwd)
#     return render_template('index.html', results=[], query=None, is_registered=is_registered())
#





@app.route('/query')
def query():
    query_raw = request.args['q'].split(" ")

    print("access token", creds.access_token)

    masto = creds.create_masto()

    print ("masto.access_token", masto.access_token)

    user_interface = FlaskUI(masto)


    # Fetchh the search query
    # query_raw = "@deeds people"# response.args.query
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


    #return render_template('search-ninja.html', query=" ".join(query_terms), result=toot_ranking)
    return render_template('index.html', toots=toot_ranking, query=request.args['q'], base_url=user_interface.base_url, registered=creds.is_authenticated())



app.run(host="0.0.0.0")
