#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

from flask import Flask, render_template, url_for,redirect,request
from werkzeug.routing import BaseConverter
from flask.ext.cache import Cache
#from flask.ext.babel import Babel
from flask import send_from_directory

import json

from jsonrpc import ServiceProxy

from bitcoinrpc.authproxy import AuthServiceProxy

app = Flask(__name__, static_url_path='/static')
app.config.from_object('config')
app.debug = app.config['DEBUG']
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

access = AuthServiceProxy(app.config['RPC'])

@app.route('/fonts/<filename>')
def fonts(filename):
    return send_from_directory(app.root_path + '/static/fonts/', filename)

@app.route('/js/<filename>')
def js(filename):
    return send_from_directory(app.root_path + '/static/js/', filename)

@app.route('/css/<filename>')
def css(filename):
    return send_from_directory(app.root_path + '/static/css/', filename)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def not_found(error):
    return render_template('500.html'), 500

@app.route('/about', methods=['GET'])
def about():
    return render_template("about.html")

def custom_render(template, *args, **kwargs):
    """
    custom template rendering including some blockindex vars
    """
    return render_template(template, *args, **kwargs)

@app.route('/tx/<txid>')
def tx(txid):                                                                                                                                                                  
    """
    """

    tx = access.getrawtransaction(txid,1)

    if 'coinbase' in tx['vin'][0]:
        tx['coinbase'] = True
        tx['decode'] = tx['vin'][0]['coinbase'].decode('hex').decode('ascii','replace')
    return render_template('tx.html', tx=tx)

@app.route('/height/<hi>')
def hheight(hi=0):                                                                                                                                                                  
    print hi
    blkhash = access.getblockhash(int(hi))
    return redirect("/blk/%s" % blkhash, code=302)

@app.route('/blk/<blkid>')
def blk(blkid):                                                                                                                                                                  
    """
    """
    blk = access.getblock(blkid,True)
    blk['txnum'] = len(blk["tx"])
    blk['txper'] = blk["size"]/len(blk["tx"])
    return render_template('blk.html', blk=blk)
 
@app.route('/addr/<address>')
@app.route('/addr/<address>/<page>')
def address(address, page=0):
    """
    """
    num = 10
    page = int(page)
    balance = access.getallbalance(address)
    try:
        txs = access.listalltransactions(address, 1,page * num, (page + 1) *num, 1)
    except:
        return render_template('404.html'), 404
    return render_template('address.html', txs=txs, balance=balance, page=page, address=address)

@app.route('/search/<sid>')
@app.route('/search', methods=['GET', 'POST'])
def search(q=0):                                                                                                                                                                  
    """
    """
    # check addr
    #if len(id) < 33:
    #    info = "Error input!"
    #elif id[0] == 0x4 and len(id) != 65:
    #    info = "Error input!"
    #elif len(id) != 33:
    #    info = "Error input!"

    sid = request.args.get('q', 0)

    slen = len(sid)
    if slen == 64:
        #should be tx hash or blk hash
        try:
            access.getrawtransaction(sid,1)
            return redirect("/tx/%s" % sid, code=302)
        except:
            try:
               access.getblock(sid,True)
               return redirect("/blk/%s" % sid, code=302)
            except:
               return redirect("/", code=302)
    if slen <= 34 and slen >=26:
         return redirect("/addr/%s" % sid, code=302)
    elif slen <9:
        #as blk height
        return redirect("/height/%s" % sid, code=302)
    else:
        return redirect("/", code=302)
 
@app.route('/')
def home():                                                                                                                                                                  
    """
    """
    return render_template('home.html')
 
if __name__ == '__main__':
    app.run()
