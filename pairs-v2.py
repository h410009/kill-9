import numpy as np
import pandas as pd
import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
# just set the seed for the random number generator
#np.random.seed(107)
import sys
import matplotlib.pyplot as plt
import time

"""
class MovAvg:
    def __init__(self, n = 200, s = 1):
        self._window = n
        self._num = s
        self._vals = vQueue(self._num)
        self._last = np.zeros(s, dtype = np.float32)
        self._MA = np.zeros(s, dtype = np.float32)

    def update(self, vec): # vec assumed to be np array of size s
        self._vals.enqueue(vec)
        self._MA += vec
        if self._vals.size() > self._window:
            self._last = self._vals.dequeue()
            self._MA -= self._last

    def getMA(self, reset):
        if reset:  # allow the option of resetting the MA from time to time
            self._MA = self._vals.sum()
        return self._MA / self._vals.size()


class PairsTrading(MovAvg):
    def __init__(self, th_p = 0.05, nstocks = 1):
        self._thp = th_p # threshold for p-value
        self._n = nstocks
        self._smatrix = np.zeros((self._n, self._n),np.float32) # scores
        self._pmatrix = np.ones((self._n, self._n),np.float32) # pvalues
        # pvalues are the probabilities of the agreement being a coincidence
        self._pairs = [] # cointegrated pair indices
        self._spreads = [] # used in seeing if the current spread is
                           # above or below the medium spred - we are betting
                           # on mean-reversion for the spread
        self._MApairs = []

    def update_pairs(self, data):
        self._pairs = []
        for i in range(self._n):
            for j in range(i+1, self._n):
                score, pvalue = coint(data[:,i], data[:,j])[0:2]
                self._smatrix[i, j], self._smatrix[j, i] = score, score
                self._pmatrix[i, j], self._pmatrix[j, i] = pvalue, pvalue
                if pvalue < self._thp: # p values below confidence levels
                    self._pairs.append((i, j))

    def getPvals_Pairs(self):
        return self._pmatrix, self._pairs

    def update_spreads(self):
        self._spreads = []
        self._MApairs = []
        for _ in self._pairs:
            ?????????
"""
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


class ConvTrade:
    # convert XLF to/from a basket of 3 BOND, 3 GS, 3 MS, 2 WFC
    # 100 cost per conversion regardless of the number of stocks
    # ----------------------------------------------------------
    # VALE is an ADR of VALBZ 1-1 ratio, 10 dolars per conversion, 
    # regardless of number of shares - use the max number of 
    # check if the values of these diverge

    def __init__(self):
        self._costConvETF = 100
        self._limits = {"BOND": 100, "GS": 100, "MS": 100, "WFC": 100, \
            "XLF": 100, "VALBZ": 10, "VALE": 10}
        self._inventory = {"XLF": 0, "VALE": 0, "VALBZ": 0, "GS": 0, \
            "BOND": 0, "MS": 0,  "WFC": 0}
        self._buyETF = {"XLF": 0, "GS": 0, "MS": 0, "WFC": 0, "BOND": 0}
        self._sellETF = {"XLF": 0, "GS": 0, "MS": 0, "WFC": 0, "BOND": 0}
        self._begin_time =  int(round(time.time())) # time in seconds
        self._current_time = self._begin_time
        self._buyprices = {"XLF": 0, "GS": 0, "MS": 0, "WFC": 0, "BOND": 0}
        self._sellprices = {"XLF": 0, "GS": 0, "MS": 0, "WFC": 0, "BOND": 0}

    ## one should first check if the transaction was successful,
    ## if that is true
    def update_buy(self, buysignal):
        for _ in buysignal:
            self._inventory[_] += buysignal[_]
    def update_sell(self, sellsignal):
            self._inventory[_] -= sellsignal[_]

    def get_avg_prices(self, books):
        # "book" is a list of book dictionary for stocks
        for _ in books:
            key = books[_]['symbol']

            self._buyprices[key] = 0.0
            length = len(books['buy'])
            for idx in range(length):
                self._buyprices[key] += books[_]['buy'][idx][0]
            self._buyprices[key] /= length

            self._sellprices[key] = 0.0
            length = len(books['sell'])
            for idx in range(length):
                self._sellprices[key] += books[_]['sell'][idx][0]
            self._sellprices[key] /= length

    def updateETF(self, prices): # dictionary of prices
        diff_1 = 10 * prices["XLF"] - self._costConvETF - 3 * prices["BOND"] -\
            2 * prices["GS"] - 3 * prices["MS"] - 2 * prices["WFC"]
        diff_2 = 3 * prices["BOND"] + 2 * prices["GS"] + 3 * prices["MS"] + \
            2 * prices["WFC"] - 10 * prices["XLF"] - self._costConvETF

        # update time
        self._curent_time = int(round(time.time()))
        
        if diff_1 > 0.0:
            quant_MS = (100 - self.inventory["MS"]) // 3
            quant_GS = (100 - self.inventory["GS"]) // 2
            quant_BOND = (100 - self.inventory["BOND"]) // 3
            quant_WFC = (100 - self.inventory["WFC"]) // 2
            quant_XLF = (100 + self.inventory["XLF"]) // 10
            quant = min(quant_MS,quant_GS,quant_BOND,quant_WFC,quant_XLF)
    
            self._buyETF = {"XLF": 0, "GS": 2*quant, "MS": 3*quant, 
                "WFC": 2*quant, "BOND": 3*quant}
            self._sellETF = {"XLF":10*quant,"GS":0,"MS":0,"WFC":0,"BOND":0}
            self._inventory["XLF"] -= 10 * quant 
            self._inventory["GS"] += 2*quant
            self._inventory["BOND"] += 3*quant
            self._inventory["WFC"] += 2*quant
            self._inventory["MS"] += 3*quant
   
        if diff_2 > 0.0:
            quant_MS = (100 + self.inventory["MS"]) // 3
            quant_GS = (100 + self.inventory["GS"]) // 2
            quant_BOND = (100 + self.inventory["BOND"]) // 3
            quant_WFC = (100 + self.inventory["WFC"]) // 2
            quant_XLF = (100 - self.inventory["XLF"]) // 10
            quant = min(quant_MS, quant_GS, quant_BOND, quant_WFC,quant_XLF)
    
            self._sellETF = {"XLF": 0, "GS": 2*quant, "MS": 3*quant, 
                "WFC": 2*quant, "BOND": 3*quant}
            self._buyETF = {"XLF":10*quant,"GS":0,"MS":0,"WFC":0,"BOND":0}

            self._inventory["XLF"] += 10 * quant
            self._inventory["GS"] -= 2*quant
            self._inventory["BOND"] -= 3*quant
            self._inventory["WFC"] -= 2*quant
            self._inventory["MS"] -= 3*quant

         # BE CAREFUL, WHEN BUYING XLF, THE SYNTAX MUST BE "CONVERT"
         # NOT "BUY"

        return self._buyETF,self._sellETF  

"""

class MarketMaker(MovAvg):
    def __init__(self, nstocks = 1):
        self._n = nstocks
        self._currbids = np.array(self._n, np.int32) # 1/0 for each stock
        self._currasks = np.array(self._n, np.int32) # 1/0 for each stock
        self._inventory = np.array(self._n, np.int32)
        self._MAs = np.array(self._n, np.float32) # moving averages
        self._MVs = np.array(self._n, np.float32) # moving volatilities
        self._currbidprices = np.array(self._n, np.float32) 
        self._curraskprices = np.array(self._n, np.float32) 

    def update_





Strat = PairsTrading(nstocks = 2)

data_fslr = pd.read_csv('fslr.csv')
data_abgby = pd.read_csv('abgby.csv')


data_1 = data_fslr['Close'].ravel()
ndays = data_1.shape[0]
some_noise = np.random.normal(3, 1, ndays)
data_2 = data_1 + some_noise

stock_1 = pd.Series(data_1,name='FSLR')
stock_2 = pd.Series(data_2,name='FSLRP')

df = pd.concat([stock_1,stock_2], axis=1)
df.plot()
plt.show()

Strat.update(df.values)
pvalues, pairs = Strat.getPvals_Pairs()
print(pvalues,pairs)
"""
