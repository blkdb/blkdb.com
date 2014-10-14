import decimal
import json
from tornado import websocket, web, ioloop
from bitcoinrpc.authproxy import AuthServiceProxy
import thread
import zmq

lAuth = AuthServiceProxy("http://bitcoinrpc:A4MjCQEiCyMeK9b3w2aLL2P5m1wGaHFXV25TLPjM4yoS@127.0.0.1:4002")

cl = [] # this is for demo purposes, never ever use a global var in production!

filterList = ['all', 'tag','']
def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

class SocketHandler(websocket.WebSocketHandler):
    filterType = ['all']
    ''' websocket handler '''
    def open(self):
        ''' ran once an open ws connection is made'''
        if self not in cl:

           cl.append(self)

           info = lAuth.getinfo()
           blkhash = lAuth.getblockhash(int(info['blocks']) -9)
           blk = lAuth.getblock(blkhash)
           blk['item'] =  'block'
           tx = lAuth.getrawtransaction(blk['tx'][0],1)
           blk['out'] =  tx['valueOut']
           self.write_message(json.dumps(blk, default=decimal_default))
           for i in range(9):
               blk = lAuth.getblock(blk['nextblockhash'])
               blk['item'] =  'block'
               tx = lAuth.getrawtransaction(blk['tx'][0],1)
               blk['out'] =  tx['valueOut']
               self.write_message(json.dumps(blk, default=decimal_default))
 
           mx = lAuth.getrawmempool()

           for txhash in mx[:10]:
               tx = lAuth.getrawtransaction(txhash,1)
               del tx['hex']
               tx['item'] =  'tx'
               self.write_message(json.dumps(tx, default=decimal_default))

    def on_message(self, message):
        #self.write_message(u"Your message was: " + message)

        msg = json.loads(message)
        if 'filter' in msg:
            self.filterType = msg['filter']
            print "chang filter %s" % msg['filter'] 
 
    def on_close(self):
        ''' on close event, triggered once a connection is closed'''
        if self in cl:
            cl.remove(self)

app = web.Application([
    (r'/', SocketHandler),
])

def websocketServer():
    app.listen(8887)
    ioloop.IOLoop.instance().start()

thread.start_new_thread(websocketServer, ())


port = 28332
topic1 = "BLK"
topic2 = "TXN"
topic_len = len(topic1)

zmqContext = zmq.Context()
zmqSubSocket = zmqContext.socket(zmq.SUB)
zmqSubSocket.setsockopt(zmq.SUBSCRIBE, topic1)
zmqSubSocket.setsockopt(zmq.SUBSCRIBE, topic2)
zmqSubSocket.connect("tcp://127.0.0.1:%i" % port)
 
def handleBLK(blk):
    print "-BLKHDR-"
    blk = json.loads(blk)
    blk['item'] =  'block'
    tx = lAuth.getrawtransaction(blk['tx'][0],1)
    blk['out'] =  tx['valueOut']

    for c in cl:
       c.write_message(json.dumps(blk, default=decimal_default))

def handleTX(txdata):
    tx = json.loads(txdata)
    tx['item'] =  'tx'
    taglist =  []
    for txin in tx['vin']:
        if txin['preOutScriptPubKey']['type'] not in taglist:
            taglist.append(txin['preOutScriptPubKey']['type'])
    for txout in tx['vout']:
        if txout['scriptPubKey']['type'] not in taglist:
            taglist.append(txout['scriptPubKey']['type'])

    if tx['valueOut'] > 10:
       taglist.append('big')

    for c in cl:
        if 'all' in c.filterType:
            c.write_message(json.dumps(tx, default=decimal_default))
        else:
            for tag in taglist: 
                if tag in c.filterType:
                    c.write_message(json.dumps(tx, default=decimal_default))
                    break

try:
    while True:
        msg = zmqSubSocket.recv()
        msg_topic = msg[:topic_len]
        msg_data  = msg[topic_len:]

        if msg_topic == "TXN":
            handleTX(msg_data)
        elif msg_topic == "BLK":
            handleBLK(msg_data)

    pass
except KeyboardInterrupt:
    zmqContext.destroy()
 
          
