import mastodon
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
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

client_id = "TODO"
client_secret = "TODO"
user = "ben@smart-cactus.org"
password = "TODO"

m = mastodon.Mastodon(client_id=client_id,
                      client_secret=client_secret,
                      api_base_url='https://mastodon.social')
m.log_in(user, password, to_file='test.secret')
account = m.search('deeds')['accounts'][0]
toots = list(toot for toot in m.account_statuses(account['id']))
#toots=[]
print(toots[:5])

import flask
from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def index():
    return flask.render_template('index.html', results=[], query=None)

@app.route('/query')
def query():
    query = request.args['q']
    results = []
    for toot in toots:
        if query in toot['content']:
            results.append({
                'content': strip_tags(toot['content']),
                'author': toot['account']['username']
            })

    return flask.render_template('index.html', toots=results, query=query)

app.run()
