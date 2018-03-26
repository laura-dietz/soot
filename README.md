# soot
search tool for toots on mastodon

Experimental prototype


# Installation

Requires Python 3.5
a keyring backend to be installed


git clone git@github.com:halcy/Mastodon.py.git
setup.py install

git clone this repository
cd into repository
run `pip install`

# Usage
Run the server.py to bring up the web server.

Debug Script: Run `pyton soot-bm25.py -h` and follow instructions

# Changes

## 25/03/2018

- Runs on flask web microframework
- supports copy&paste authentication via authorization tokens
- BM25 retrieval model on substrings
- No indexing, no caching
- Searches only 100 most recent posts in home timeline


