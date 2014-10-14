#!/usr/bin/env python2.7
"""
app_config.py will be storing all the module configs.
Here the db uses mysql.
"""

import os
_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

BABEL_DEFAULT_LOCALE ='zh-cn'
BABEL_DEFAULT_TIMEZONE='UTC'

BRAND = "blkdb.com"
DOMAIN = "blkdb.com"
ROOT_URL = "http://blkdb.com"

RPC = "http://rpcuser:rpcpass@127.0.0.1:8332"

STATIC_ROOT = "/srv/blockindex/blockindex/static/"
STATIC_URL = ROOT_URL + "/static/"
