# soot
search tool for toots on mastodon

Experimental prototype


# Installation

Tested with Python 3.9 and 3.7

Requires a keyring backend to be installed

1. git clone this repository

2. cd into repository

3. run `pip install .`


This should install [Mastodon.py 1.5.1](https://pypi.org/project/Mastodon.py/)


# Run Debug Script from Command line

The command line script does not require the web service and authentication setup.

You only need to register your soot app under mastodon website / Preferences / Development / New Application

Keep note of the `client-key` (aka client-id), `client-secret` and `access_token` as you will need to provide this information to soot.

Run the soot script by following instructions on

```
python3 soot/bm25.py -h
```


# Run via Web Service

The web service provides a web front end for searching and filtering toots available to you. 

You start the web server with the following command (also see help with `-h`)

```
python3 soot/server.py --base-url=mastodon.social --host=$domain --port=5000
```

# Using the Soot Web Service

Authentication:

1. Directing your client to your soot server's url
2. you are asked to authenticate: Follow the link and login to your mastodon account and copy the authentication code. 
3. Navigate back to your soot server and paste the authentication token in the field. 
4. The access token will be stored in the web session (but not the password or your login handle)


Searching:
1. Navigate to the soot server; you will now see the search box. 
2. enter query terms and/or mentions and hit "Search"
3. you will see toots that contain the search terms (BM25 ranking)
4. Note that for efficiency reasons you can only search the past 100 toots at the moment.



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


