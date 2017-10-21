#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# chmod +x bot.py
# while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json
import random

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="orange"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = False

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=2
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())


# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    from random import random
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    write_to_exchange(exchange, {"type": "add", "order_id": 1, "symbol": "BOND", "dir": "BUY", "price": 998, "size": 20})
    write_to_exchange(exchange, {"type": "add", "order_id": 2, "symbol": "BOND", "dir": "SELL", "price": 1002, "size": 20})
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    n = random.randint(1, 999999)
    while True:
        hello_from_exchange = read_from_exchange(exchange)
        if hello_from_exchange["type"] == "book":
            if hello_from_exchange["symbol"] == "VALE":
        if hello_from_exchange["type"] == "ack":
            print("The exchange replied:", hello_from_exchange, file=sys.stderr)
            n += 4
            write_to_exchange(exchange, {"type": "add", "order_id": n+2, "symbol": "BOND", "dir": "BUY", "price": 999, "size": 20})
            write_to_exchange(exchange, {"type": "add", "order_id": n+3, "symbol": "BOND", "dir": "SELL", "price": 1002, "size": 20})

if __name__ == "__main__":
    main()
