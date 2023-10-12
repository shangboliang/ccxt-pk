# -*- coding: utf-8 -*-

import os
import sys
import pandas_ta as ta
import pandas as pd
from pytz import timezone  # 引入时区库


root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

import ccxt  # noqa: E402


print('CCXT Version:', ccxt.__version__)


def main():
    exchange = ccxt.binance({
            'proxies': {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890'
            }
        }
    )
    
    markets = exchange.load_markets()
    # exchange.verbose = True  # uncomment for debugging purposes
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', '4h')
    if len(ohlcv):
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')

          # 将时间从UTC转换为UTC+8
        utc = timezone('UTC')
        utc_plus_8 = timezone('Asia/Shanghai')  # 你可以根据需要选择不同的时区
        df['datetime'] = df['datetime'].dt.tz_localize(utc).dt.tz_convert(utc_plus_8)
       
        # 计算20周期EMA并将其添加到DataFrame
        ema20 = df.ta.ema(close='close', length=20)
        df['ema20'] = ema20
        # ema = df.ta.ema()
        # df = pd.concat([df, ema], axis=1)
        df['ema20'] = ema20
        print(df)


main()