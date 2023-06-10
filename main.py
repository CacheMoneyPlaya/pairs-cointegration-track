import os
import time
import argparse
import pandas as pd
import ccxt as ccxt
import Scan.Scan as s
import ByBitApi.Actions.Actions as ac
from dotenv import load_dotenv, dotenv_values

CONFIG = None
load_dotenv()
ENV = dotenv_values(".env")

exchange = ccxt.bybit({
    "apiKey": ENV['BYBIT_API_KEY'],
    "secret": ENV['BYBIT_API_SECRET_KEY']
})


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-pair", "--pair", help="Pair to trade", required=False)
parser.add_argument("-side", "--side", help="Side i.e long or short on pair", required=False)
parser.add_argument("-tp", "--tp", help="Take profit trigger on the **PAIR**", required=False)
parser.add_argument("-api", "--api", help="Set up api", required=False, action="store_true")
parser.add_argument("-scan", "--scan", help="Scans active positions for net returns below threshold", required=False, action="store_true")

args, unknown = parser.parse_known_args()
CONFIG = vars(args)

PAIR = CONFIG['pair']
SIDE = CONFIG['side']
TAKE_PROFIT = CONFIG['tp']
SIDES = None
LEVERAGE = int(ENV['LEVERAGE'])
DRAWDOWN = float(ENV['DRAWDOWN'])


def entry():

    if input("You have input a {0} order for the pair {1}, is this correct? (y/n)".format(SIDE, PAIR)) != "y":
            exit()

    if SIDE.upper() == 'SELL':
        SIDES = ['sell', 'buy']
    elif SIDE.upper() == 'BUY':
        SIDES = ['buy', 'sell']
    else:#
        print('Invalid order side')
        exit()

    tickers = PAIR.split('-')

    ext_data  = [SIDE.upper(), float(TAKE_PROFIT)]
    csvData = tickers + ext_data

    df = pd.DataFrame([csvData])
    df.to_csv('active_pairs.csv', mode='a', index=False, header=False)

    pair_order_value = ac.get_free_balance(exchange) * DRAWDOWN

    ac.set_leverage(exchange, LEVERAGE, tickers[0])
    ac.set_leverage(exchange, LEVERAGE, tickers[1])

    t1 = ac.place_market_order(exchange, tickers[0], SIDES[0], pair_order_value, 10)
    t2 = ac.place_market_order(exchange, tickers[1], SIDES[1], pair_order_value, 10)


def scan():
    s.scan_pairs(exchange)


if __name__ == '__main__':

    if CONFIG['scan']:
        scan()

    else:
        entry()
