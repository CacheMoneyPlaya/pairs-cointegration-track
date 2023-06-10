from dotenv import load_dotenv, dotenv_values

load_dotenv()
CONFIG = dotenv_values(".env")

def place_market_order(bb, ticker: str, side: str, pair_order_value: int, leverage: int):
    ticker_price = get_ticker_price(bb, ticker)
    side_value = (pair_order_value / 2) * leverage

    type = 'market'
    amount = side_value / ticker_price

    if side == 'sell':
        return bb.create_market_sell_order(ticker, amount)
    else:
        return bb.create_market_buy_order(ticker, amount)

def set_leverage(bb, leverage: int, ticker: str):
    try:
        bb.setLeverage(leverage, ticker)
    except Exception as e:
        pass


def get_ticker_price(bb, ticker: str):
    return float(bb.fetchTicker(ticker)['last'])


def get_free_balance(bb):
    return bb.fetch_free_balance()['USDT']

def get_balance(bb):
    balances = bb.fetch_balance(params = {"currency": "usdt"})['info']['result']['list']
    return float([d['equity'] for d in balances if d['coin'] == 'USDT'][0])
