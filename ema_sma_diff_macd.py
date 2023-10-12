import os
import sys
import pandas_ta as ta
import pandas as pd
from pytz import timezone  # 引入时区库

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

import ccxt


# ema、sema、macd、rsi
print('CCXT Version:', ccxt.__version__)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def main():
    exchange = ccxt.binance({
        'proxies': {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890'
        }
    })

    markets = exchange.load_markets()
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', '4h')
    if len(ohlcv):
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # 将时间从UTC转换为UTC+8
        utc = timezone('UTC')
        utc_plus_8 = timezone('Asia/Shanghai')
        df['datetime'] = df['datetime'].dt.tz_localize(utc).dt.tz_convert(utc_plus_8)
                
        
        # -------------------  EMA----------------------------------------------------------------
        # sma20 = df.ta.sma(close='close', length=20)
        # 打印DataFrame的最新10行
                # 计算20周期EMA，添加到表头
        ema20 =df.ta.ema(close='close',length=20)
        
        # 计算SMA20，添加到表头
        sema20 = ema20.rolling(window=20).mean()
        ema_sma_percent_diff = round(((ema20 - sema20) / sema20) * 100, 3)

        # --------------- MACD -----------------------------------------------------------------------
        since = None
        fast = 12
        slow = 26
        signal = 9
        # 计算MACD指标，使用给定的快速、慢速和信号周期
        macd = df.ta.macd(fast=fast, slow=slow, signal=signal)
        # 将MACD指标添加到DataFrame中
        df = pd.concat([df, macd], axis=1)

        # 打印DataFrame
        # print(df)
        df['ema20'] = ema20
        df['sma20'] = sema20
        df['ema_sma_percent_diff'] = ema_sma_percent_diff

        # --------------- RSI -----------------------------------------------------------------------   
        rsi_length = 100
        df = pd.concat([df, df.ta.rsi(length=rsi_length)], axis=1)

        print(df.tail(10))



main()
