import os
import argparse
import ccxt as ccxt
import ByBitApi.Actions.Actions as ac
from dotenv import load_dotenv, dotenv_values
import pandas as pd
import Scan.Scan as s

CONFIG = None
load_dotenv()
ENV = dotenv_values(".env")


exchange = ccxt.bybit({
    "apiKey": ENV['BYBIT_API_KEY'],
    "secret": ENV['BYBIT_API_SECRET_KEY']
})

def entry():
    pair = CONFIG['pair']
    side = CONFIG['side']

    tickers = pair.split('-')
    sides = None

    ext_data  = [ac.get_balance(exchange), side]
    csvData = tickers + ext_data

    df = pd.DataFrame([csvData])
    df.to_csv('active_pairs.csv', mode='a', index=False, header=False)

    if side == 'SELL':
        side = ['sell', 'buy']
    else:
        side = ['buy', 'sell']

    pair_order_value = ac.get_balance(exchange)*0.2

    ac.set_leverage(exchange, 10, tickers[0])
    ac.set_leverage(exchange, 10, tickers[1])

    t1 = ac.place_market_order(exchange, tickers[0], side[0], pair_order_value, 10)
    t2 = ac.place_market_order(exchange, tickers[1], side[1], pair_order_value, 10)

def scan():
    s.scan_pairs(exchange)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-pair", "--pair", help="Pair to trade", required=False)
    parser.add_argument("-side", "--side", help="Side i.e long or short on pair", required=False)
    parser.add_argument("-api", "--api", help="Set up api", required=False, action="store_true")
    parser.add_argument("-scan", "--scan", help="Scans active positions for net returns below threshold", required=False, action="store_true")

    args, unknown = parser.parse_known_args()
    CONFIG = vars(args)

    if CONFIG['scan']:
        scan()
    else:
        entry()
