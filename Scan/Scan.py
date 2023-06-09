import pandas as pd
import ByBitApi.Actions.Actions as ac

def scan_pairs(bb):
    df = pd.read_csv('active_pairs.csv', usecols= ['t1','t2', 'side', 'take_profit'])
    df.apply(get_position_returns_and_determine_close,args=(bb,), axis=1)

def get_position_returns_and_determine_close(x, bb):
    hedge1 = bb.fetchPosition(x.t1)['info']
    hedge2 = bb.fetchPosition(x.t2)['info']

    net_returns  = float(hedge1['unrealisedPnl']) + float(hedge2['unrealisedPnl'])

    if x.side == 'SELL':
        x.t1_close_side = 'buy'
        x.t2_close_side = 'sell'
    else:
        x.t1_close_side = 'sell'
        x.t2_close_side = 'buy'

    accountBalance = float(ac.get_balance(bb))

    if is_below_close_threshold(bb, net_returns, accountBalance) or is_pair_price_exceeding_take_profit(bb, x):
        bb.create_order(x.t1, amount=hedge1['size'], type='Market', side=x.t1_close_side, params={'reduce_only': True})
        bb.create_order(x.t2, amount=hedge2['size'], type='Market', side=x.t2_close_side, params={'reduce_only': True})
        remove_row_from_csv_tracking(x)


def is_below_close_threshold(bb, net_pair_returns: float, account_value_at_t: float):
    # Get total account value change from pair
    net_pct_change = (((account_value_at_t + net_pair_returns) - account_value_at_t) / account_value_at_t) * 100

    # 1 % used as max SL
    return net_pct_change <= -1

def is_pair_price_exceeding_take_profit(bb, x):
    # Get ticker 1 and divide by ticker 2
    # If sell type we check that price is below or equal to trigger
    # if buy type we check that price is above or equal to trigger
    t1_price = ac.get_ticker_price(bb, x.t1)
    t2_price = ac.get_ticker_price(bb, x.t2)

    pair_price = float(t1_price) / float(t2_price)

    if x.side == 'SELL':
        return pair_price <= x.take_profit
    elif x.side == 'BUY':
        return pair_price >= x.take_profit

def remove_row_from_csv_tracking(x):
    df = pd.read_csv('active_pairs.csv', usecols= ['t1','t2', 'side', 'take_profit'])
    df = df.loc[df['t1'] != x.t1]

    df.to_csv('active_pairs.csv', mode='w', index=False, columns=['t1','t2', 'side', 'take_profit'])
