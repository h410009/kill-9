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
    port.orders.update(Order(n, "BUY", symbol, size, price))
    write_to_exchange(exchange, {"type": "add", "order_id": n, "symbol": symbol, "dir": "BUY", "price": price, "size": units})
    return n

def sell(symbol, price, units):
    n = random.randint(1, 999999)
    port.orders.update(Order(n, "SELL", symbol, size, price))
    write_to_exchange(exchange, {"type": "add", "order_id": n, "symbol": symbol, "dir": "SELL", "price": price, "size": units})
    return n

def convert(symbol, direction, units):
    n = random.randint(1, 999999)
    write_to_exchange(exchange, {"type": "convert", "order_id": n, "symbol": symbol, "dir": direction, "size": units})
    return n

def do_VALE(bE, sE, bZ, sZ):
    print("Compare:", bE[0], sE[0], bZ[0], sZ[0], (bZ[0] - sE[0]) * min(sE[1], bZ[1]), (bE[0] - sZ[0]) * min(sZ[1], bE[1]))
    global VALE_orders
    global VALBZ_orders

    if((bZ[0] - sE[0]) * min(sE[1], bZ[1]) > 15):
        units = min(sE[1], bZ[1])
        buy("VALE", sE[0], min(0, units - VALE_orders[0]))
        convert("VALE", "SELL", units)
        sell("VALBZ", bZ[0], min(0, units - VALBZ_orders[0]))
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

class Order():
   def __init__(self, n, kind, symbol, size, price):
       self.n = n
       self.kind = kind
       self.symbol = symbol
       self.size = size
       self.price = price

class Portfolio():
   def __init__(self):
       self.positions = {“GS”: 0, “MS”: 0, “WFC”: 0, “XLF”: 0, “VALE”: 0, “VALBZ”: 0}
       self.highBuy = {‘GS’:0, ‘MS’:0, ‘WFC’:0, ‘XLF’:0, ‘VALBZ’:0, ‘VALE’:0, ‘BOND’:0}
       self.lowSell = {‘GS’:0, ‘MS’:0, ‘WFC’:0, ‘XLF’:0, ‘VALBZ’:0, ‘VALE’:0, ‘BOND’:0}
       self.highBuyQuant = {‘GS’:0, ‘MS’:0, ‘WFC’:0, ‘XLF’:0, ‘VALBZ’:0, ‘VALE’:0, ‘BOND’:0}
       self.lowSellQuant = {‘GS’:0, ‘MS’:0, ‘WFC’:0, ‘XLF’:0, ‘VALBZ’:0, ‘VALE’:0, ‘BOND’:0}
       self.buyTot = {‘GS’:0, ‘MS’:0, ‘WFC’:0, ‘XLF’:0, ‘VALBZ’:0, ‘VALE’:0, ‘BOND’:0}
       self.sellTot = {‘GS’:0, ‘MS’:0, ‘WFC’:0, ‘XLF’:0, ‘VALBZ’:0, ‘VALE’:0, ‘BOND’:0}
       self.orders = {}
       self.symbolLimit = {‘BOND’:100, ‘GS’: 100, ‘MS’: 100, ‘WFC’: 100, ‘XLF’: 100, ‘VALBZ’: 10, ‘VALE’: 10}

port = Portfolio();

def fill_Logic():
    global port
    if (port.buyTot["BOND"] < 80):
        Buy("BOND", 999, 20)
    if (port.selTot["BOND"] < 80):
        Sell("BOND", 1001, 20)

def main():
    global port
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    buy("BOND", 999, 100)
    sell("BOND", 1001, 100)

    while True:
        msg = read_from_exchange(exchange)

        if msg["type"] == "fill":
            port.positions += -1 * (msg["dir"] == "SELL") * msg["size"]

        if (msg["type"] == "book"):
            port.highBuy[msg["symbol"]] = (max(buy)[0] if msg["buy"] else 0)
            port.highBuyQuant[msg["symbol"]] = (max(buy)[1] if msg["buy"] else 0)
            port.lowSell[msg["symbol"]] = (min(sell)[0] if msg["buy"] else 10000)
            port.lowSellQuant[msg["symbol"]] = (min(sell)[1] if msg["buy"] else 0)

        if msg["type"] == "ack":
            print("ACK:", msg, file=sys.stderr)

        if msg["type"] == "reject":
            del port.orders[msg["order_id"]]
            print("ERROR:", msg, file=sys.stderr)

        if msg["type"] == "fill":
            if (msg["symbol"] == "VALE" or msg["symbol"] == "VALBZ"):
                ASSETS[msg["symbol"]] += -1 * (msg["dir"] == "SELL") * msg["size"]
            fill_Logic()


if __name__ == "__main__":
    main()
