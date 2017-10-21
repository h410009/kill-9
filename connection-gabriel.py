#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# chmod +x bot.py
# while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import socket
import json
import random

import numpy as np
import pandas as pd
import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
# just set the seed for the random number generator
#np.random.seed(107)
import sys
import matplotlib.pyplot as plt

class Market_Maker:
    def __init__(self):
        self._stocks = ["BOND", "GS", "MS", "WFC", "XLF", "VALBZ", "VALE"]
        self._limits = {"BOND": 100, "GS": 100, "MS": 100, "WFC": 100, \
            "XLF": 100, "VALBZ": 10, "VALE": 10}
        self._inventory = {"XLF": 0, "VALE": 0, "VALBZ": 0, "GS": 0, \
            "BOND": 0, "MS": 0,  "WFC": 0}
        self._buy = {"XLF": "", "GS": "", "MS": "", "WFC": "", "BOND": "", \
            "VALE": "", "VALBZ": ""}
        self._sell = {"XLF": "", "GS": "", "MS": "", "WFC": "", "BOND": "", \
            "VALE": "", "VALBZ": ""}
        self._buyprices = {"XLF": 0, "GS": 0, "MS": 0, "WFC": 0, "BOND": 0, \
            "VALE":0, "VALBZ":0}
        self._sellprices = {"XLF": 0, "GS": 0, "MS": 0, "WFC": 0, "BOND": 0, \
            "VALE":0, "VALBZ":0}
        self._quant = 5

        self._cancels = {"XLF": [], "GS": [], "MS": [], "WFC": [], \
            "BOND": [], "VALE": [], "VALBZ": []}

        self._buyidx = 1
        self._sellidx = 100000

        self._curr_bids = {"XLF": [], "GS": [], "MS": [], "WFC": [], \
            "BOND": [], "VALE": [], "VALBZ": []}
        self._curr_asks = {"XLF": [], "GS": [], "MS": [], "WFC": [], \
            "BOND": [], "VALE": [], "VALBZ": []}


    def update_inventory(self, fill_strings):
        ## go over the fill strings, delete the corresponding outstanding bids
        for _ in fill_strings:
            name, ord, stock, action = fill_strings[_].split()[0:4]
            ord = int(ord)
            if name == 'FILL' and action == 'BUY':
                to_delete = []
                # go over the bids and asks and cancel that one
                for idx in range(len(self._curr_bids[stock]))
                    if self._curr_bids[stock][idx][0] == ord
                    to_delete.append(idx)
                del self._curr_bids[stock][to_delete] # delte filled bids
                self._inventory[stock] += self._quant

            if name == 'FILL' and action == 'SELL':
                to_delete = []
                # go over the bids and asks and cancel that one
                for idx in range(len(self._curr_asks[stock]))
                    if self._curr_asks[stock][idx][0] == ord
                    to_delete.append(idx)
                del self._curr_asks[stock][to_delete] # delete filled asks
                self._inventory[stock] -= self._quant # 

         
    def get_avg_prices(self, books):
        # "book" is the book dictionary for this collection of stocks
        for _ in books:
            key = books[_]['symbol']

            self._buyprices[key] = 0.0
            length = len(books['buy'])
            for idx in range(length):
                self._buyprices[key] += books[_]['buy'][idx][0]
            self._buyprices[key] //= length

            self._sellprices[key] = 0.0
            length = len(books['sell'])
            for idx in range(length):
                self._sellprices[key] += books[_]['sell'][idx][0]
            self._sellprices[key] //= length

    def purge(self):
        for _ in self._stocks:
            self._cancels[_] = []
            # check if there are any existing stocks with outstanding
            # bids or asks and cancel them
            for order in self._curr_bids[_]:
                self.cancels[_].append("CANCEL " + str(order[0]))
            for order in self._curr_asks[_]:
                self.cancels[_].append("CANCEL " + str(order[0]))

            self._curr_bids = {"XLF": [], "GS": [], "MS": [], "WFC": [], \
                "BOND": [], "VALE": [], "VALBZ": []}
            self._curr_asks = {"XLF": [], "GS": [], "MS": [], "WFC": [], \
                "BOND": [], "VALE": [], "VALBZ": []}

        return self._cancels


    def update_orders(self): # dictionary of prices

        for _ in self._stocks: # stock key
            self._buyidx += 1
            self._sellidx += 1
            # update buy and sell orders
            self._buy[_] = "ADD " + self._buyidx + " " + key + " BUY " + \
                str(sell._buyprices[_])+" " + self._quant
            self._sell[_] = "ADD " + self.buyidx + " " + key + " SELL " + \
                str(sell._sellprices[_])+" " + self._quant

             if self._inventory[_] < self._limits[_] - self._quant:
                 self._curr_bids[_].append([self._buyidx, sell._buyprices[_], \
                     self._quant])
             if self._inventory[_] > -self._limits[_] + self._quant
                 self._curr_asks[_].append([self._sellidx, sell._sellprices[_],\
                     self._quant])

        return self._buy,self._sell



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
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    while True:
        msg = read_from_exchange(exchange)
        if msg["type"] == "ack":
            print("The exchange replied:", msg, file=sys.stderr)
            n += 4
            write_to_exchange(exchange, {"type": "add", "order_id": n+2, "symbol": "BOND", "dir": "BUY", "price": 999, "size": 20})
            write_to_exchange(exchange, {"type": "add", "order_id": n+3, "symbol": "BOND", "dir": "SELL", "price": 1002, "size": 20})

if __name__ == "__main__":
    main()
