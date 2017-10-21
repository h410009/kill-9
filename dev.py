def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

def test_mode():
    test_mode = True
    EXCHANGE_HOSTNAME = "test-exch-" + TEAM_NAME if test_mode else PROD_EXCHANGE_HOSTNAME
    PORT = 25000 + (TEST_EXCHANGE_INDEX if test_mode else 0)

TEAM_NAME = "orange"
TEST_EXCHANGE_INDEX = 2
PROD_EXCHANGE_HOSTNAME = "production"
HELLO = {"type": "hello", "team": TEAM_NAME.upper()}

class Portfolio():
    def __init__(self):
        self.positions = {"GS": 0, "MS": 0, "WFC": 0, "XLF": 0, "VALE": 0, "VALBZ": 0}
        self.highestBuy = {'GS':0, 'MS':0, 'WFC':0, 'XLF':0, 'VALBZ':0, 'VALE':0, 'BOND':0}
        self.cheapestSell = {'GS':0, 'MS':0, 'WFC':0, 'XLF':0, 'VALBZ':0, 'VALE':0, 'BOND':0}
        self.orders = {}
        self.symbolToLimit = {'BOND':100, 'GS': 100, 'MS': 100, 'WFC': 100, 'XLF': 100, 'VALBZ': 10, 'VALE': 10}

def main():
    if len (sys.argv) != 2:
        print ('USAGE: python3 trader.py server_address')
        sys.exit(2)
        exchange = connect(sys.argv[1])
        write_to_exchange(exchange, HELLO)
        hello_from_exchange = read_from_exchange(exchange)
        print("The exchange replied:", hello_from_exchange, file=sys.stderr)
