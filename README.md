# soot
search tool for toots on mastodon

Experimental prototype


# Installation

Requires Python 3.9
a keyring backend to be installed


f2f2b907d154c5767651a67f870fe869cdd7e132e5daa16102a1bc4911ea4fb5git clone git@github.com:halcy/Mastodon.py.git

setup.py install

git clone this repository
cd into repository
run `pip install .`

# Usage
Run the server.py to bring up the web server.

Debug Script: Run `python soot/bm25.py -h` and follow instructions

# Changes

## 04/11/2022
- Update to recent python 
- Update to recent mastodon API
- Fix installation instructions

## 25/03/2018

- Runs on flask web microframework
- supports copy&paste authentication via authorization tokens
- BM25 retrieval model on substrings
- No indexing, no caching
- Searches only 100 most recent posts in home timeline


