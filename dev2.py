class Portfolio():
    def __init__(self):
        self.positions = {"GS": 0, "MS": 0, "WFC": 0, "XLF": 0, "VALE": 0, "VALBZ": 0}
        self.highestBuy = {'GS':0, 'MS':0, 'WFC':0, 'XLF':0, 'VALBZ':0, 'VALE':0, 'BOND':0}
        self.cheapestSell = {'GS':0, 'MS':0, 'WFC':0, 'XLF':0, 'VALBZ':0, 'VALE':0, 'BOND':0}
        self.orders = {}
        self.symbolToLimit = {'BOND':100, 'GS': 100, 'MS': 100, 'WFC': 100, 'XLF': 100, 'VALBZ': 10, 'VALE': 10}

    
