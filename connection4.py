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
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=0
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


def split (buy, sell):
    if buy and sell:
        return [min(sell), max(buy)]
    return []

def buy(symbol, price, units):
    n = random.randint(1, 999999)
    write_to_exchange(exchange, {"type": "add", "order_id": n, "symbol": symbol, "dir": "BUY", "price": price, "size": units})
    return n

def sell(symbol, price, units):
    n = random.randint(1, 999999)
    write_to_exchange(exchange, {"type": "add", "order_id": n, "symbol": symbol, "dir": "SELL", "price": price, "size": units})
    return n

def convert(symbol, direction, units):
    n = random.randint(1, 999999)
    write_to_exchange(exchange, {"type": "convert", "order_id": n, "symbol": symbol, "dir": direction, "size": units})
    return n

def do_VALE(bE, sE, bZ, sZ):
    print("Compare:", bE[0], sE[0], bZ[0], sZ[0], (bZ[0] - sE[0]) * min(sE[1], bZ[1]), (bE[0] - sZ[0]) * min(sZ[1], bE[1]))

    if((bZ[0] - sE[0]) * min(sE[1], bZ[1]) > 15):
        units = min(sE[1], bZ[1])
        buy("VALE", sE[0], units)
        convert("VALE", "SELL", units)
        sell("VALBZ", bZ[0], units)
        return True

    if((bE[0] - sZ[0]) * min(sZ[1], bE[1]) > 15):
        units = min(sZ[1], bE[1])
        buy("VALEZ", sZ[0], units)
        convert("VALE", "BUY", units)
        sell("VALBZ", bE[0], units)
        return True

    return False


# ~~~~~============== MAIN LOOP ==============~~~~~

exchange = None

def main():
    global exchange
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    buy("BOND", 998, 100)
    sell("BOND", 1002, 100)
    write_to_exchange(exchange, {"type": "add", "order_id": 1, "symbol": "BOND", "dir": "BUY", "price": 998, "size": 20})
    write_to_exchange(exchange, {"type": "add", "order_id": 2, "symbol": "BOND", "dir": "SELL", "price": 1002, "size": 20})
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    VALE = []
    VALE_orders = [0,0]
    VALEZ = []
    VALBZ_orders = [0,0]
    while True:
        msg = read_from_exchange(exchange)
        print("The exchange replied:", msg, file=sys.stderr)
        if (msg["type"] == "book"):
            #print("The exchange replied:", msg, file=sys.stderr)
            if (msg["symbol"] == "VALE"):
                VALE = split(msg["buy"], msg["sell"])
                if VALE and VALEZ:
                    if do_VALE(VALE[0],VALE[1], VALEZ[0],VALEZ[1]):
                        VALE = []
                        VALEZ = []
            if (msg["symbol"] == "VALBZ"):
                VALEZ = split(msg["buy"], msg["sell"])
                if VALE and VALEZ:
                    if do_VALE(VALE[0],VALE[1], VALEZ[0],VALEZ[1]):
                        VALE = []
                        VALEZ = []

        if msg["type"] == "ack":
            print("The exchange replied:", msg, file=sys.stderr)

        if msg["type"] == "fill":
            print("The exchange replied:", msg, file=sys.stderr)
            buy("BOND", 998, 20)
            sell("BOND", 1002, 20)

if __name__ == "__main__":
    main()
