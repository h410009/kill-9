#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# chmod +x bot.py
# while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import socket
import json
import random

import sys

class MarketMaker:
    def __init__(self):
        self._stocks = ["BOND", "GS", "MS", "WFC", "XLF", "VALBZ", "VALE"]
        self._limits = {"BOND": 100, "GS": 100, "MS": 100, "WFC": 100, \
            "XLF": 100, "VALBZ": 10, "VALE": 10}
        self._inventory = {"XLF": 0, "VALE": 0, "VALBZ": 0, "GS": 0, \
            "BOND": 0, "MS": 0,  "WFC": 0}
        self._buy = {"XLF": {}, "GS": {}, "MS": {}, "WFC": {}, "BOND": {}, \
            "VALE": {}, "VALBZ": {}}
        self._sell = {"XLF": {}, "GS": {}, "MS": {}, "WFC": {}, "BOND": {}, \
            "VALE": {}, "VALBZ": {}}
        self._buyprices = {"XLF": 0, "GS": 0, "MS": 0, "WFC": 0, "BOND": 0, \
            "VALE":0, "VALBZ":0}
        self._sellprices = {"XLF": 0, "GS": 0, "MS": 0, "WFC": 0, "BOND": 0, \
            "VALE":0, "VALBZ":0}
        self._spreads = {"XLF": 0, "GS": 0, "MS": 0, "WFC": 0, "BOND": 0, \
            "VALE":0, "VALBZ":0}
        self._quant = 5

        self._cancels = {"XLF": {}, "GS": {}, "MS": {}, "WFC": {}, \
            "BOND": {}, "VALE": {}, "VALBZ": {}}

        self._buyidx = 1
        self._sellidx = 100000

        self._curr_bids = {"XLF": [], "GS": [], "MS": [], "WFC": [], \
            "BOND": [], "VALE": [], "VALBZ": []}
        self._curr_asks = {"XLF": [], "GS": [], "MS": [], "WFC": [], \
            "BOND": [], "VALE": [], "VALBZ": []}
        self._pending = {"XLF": 0, "GS": 0, "MS": 0, "WFC": 0, "BOND": 0, \
            "VALE":0, "VALBZ":0}
        self.cash = 30000


    def get_cash(self):
        return self.cash

    def update_inventory(self, fill_dict):
        ## go over the fill strings, delete the corresponding outstanding bids
        action = fill_dict['dir']
        ord = fill_dict['order_id']
        stock = fill_dict['symbol']
        loc_quant = fill_dict['size']
        if action == 'BUY':
            to_delete = []
            # go over the bids and asks and cancel that one
            for idx in range(len(self._curr_bids[stock])):
                if self._curr_bids[stock][idx][0] == ord:
                    to_delete.append(idx)
            self._curr_bids[stock] = [i for j, i in \
                enumerate(self._curr_bids[stock]) if j not in to_delete]

            self._inventory[stock] += loc_quant
            self.cash -= self._buyprices[stock] * loc_quant

        if action == 'SELL':
            to_delete = []
            # go over the bids and asks and cancel that one
            for idx in range(len(self._curr_asks[stock])):
                if self._curr_asks[stock][idx][0] == ord:
                    to_delete.append(idx)
            self._curr_asks[stock] = [i for j, i in \
                enumerate(self._curr_asks[stock]) if j not in to_delete]

            self._inventory[stock] -= loc_quant # 
            self.cash += self._sellprices[stock] * loc_quant

    def get_class_prices(self, stock):
        return self._buyprices[stock], self._sellprices[stock], \
            self._spreads[stock]

    def get_avg_prices(self, book):
        # "book" is the book dictionary for this collection of stocks
        key = book['symbol']

        buyprices = 0.0
        sellprices = 0.0 

        length_buy, length_sell = len(book['buy']), len(book['sell'])
        if length_buy and length_sell:
            buyprices = max(book['buy'])[0]
            sellprices = min(book['sell'])[0]

            return buyprices, sellprices

        return None

    def update_avg_prices(self, book):
        # "book" is the book dictionary for this collection of stocks
        key = book['symbol']


        length_buy, length_sell = len(book['buy']), len(book['sell'])

        if length_buy and length_sell: # only update if we get both prices
            self._buyprices[key] = max(book['buy'])[0] + 1
            self._sellprices[key] = min(book['sell'])[0] - 1   

            self._spreads[key] = self._sellprices[key] - self._buyprices[key] 

    def purge(self, _):
        self._cancels[_] = {}
        # check if there are any existing stocks with outstanding
        # bids or asks and cancel them
        for order in self._curr_bids[_]:
            self._cancels[_] = {"type": "CANCEL", "order_id": order[0]}
        for order in self._curr_asks[_]:
            self._cancels[_] = {"type": "CANCEL", "order_id": order[0]}

        self._curr_bids[_] = []
        self._curr_asks[_] = []
        self._pending[_] = 0
        return self._cancels[_]

    def get_pending(self, stock):
        return self._pending[stock]

    def update_orders(self, _): # dictionary of prices
        self._buyidx += 1
        self._sellidx += 1
        # update buy and sell orders
        self._buy[_] = {"type": "add", "order_id": self._buyidx, \
            "symbol": _, "dir": "BUY", "price": self._buyprices[_], \
            "size": self._quant}
        self._sell[_] = {"type": "add", "order_id": self._sellidx, \
            "symbol": _, "dir": "SELL", "price": self._sellprices[_], \
            "size": self._quant}

        if self._inventory[_] < self._limits[_] - self._quant and \
           self._inventory[_] > -self._limits[_] + self._quant:

            self._curr_bids[_].append([self._buyidx, self._buyprices[_], \
                self._quant])
            self._curr_asks[_].append([self._sellidx, self._sellprices[_],\
                self._quant])
            self._pending[_] = 1
            return self._buy[_], self._sell[_]
        return None


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
test_exchange_index=1
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
MM = MarketMaker()


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
        print(MM.get_cash())
        if msg["type"] == "book":
            status = MM.get_pending(msg['symbol'])
            if status: # if pending, see if we need to purge and restart:
                prices = MM.get_avg_prices(msg)
                if prices is not None:
                    buyprice = prices[0]
                    sellprice = prices[0]
                class_buyprice, class_sellprice, class_spread = \
                    MM.get_class_prices(msg['symbol'])
     
                print(buyprice,class_buyprice,sellprice,class_sellprice,class_spread)
            
                purge_flag = 0   
                if abs((buyprice - sellprice) - \
                    (class_buyprice - class_sellprice)) >= class_spread:
                    purge_flag = 1

               #if purge_flag: # if we purge, reset status:
               #    print("purging")
               #    order = MM.purge(msg['symbol'])
               #    write_to_exchange(exchange, order)

            if not status: # if not pending start a new trade
                print("starting new")
                MM.update_avg_prices(msg)
                orders = MM.update_orders(msg['symbol'])
                if orders is not None:
                    print('ORDER', orders)
                    write_to_exchange(exchange, orders[0])
                    write_to_exchange(exchange, orders[1])
        if msg["type"] == "fill":
            MM.update_inventory(msg)
        if msg["type"] == "ack":
            print(msg)

if __name__ == "__main__":
    main()
