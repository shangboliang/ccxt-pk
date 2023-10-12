import ccxt
import time
import numpy as np
import pandas_ta as ta  # 添加这一行

exchange = ccxt.binance({
    # 'apiKey': 'YOUR_API_KEY',
    # 'secret': 'YOUR_SECRET',
    'enableRateLimit': True,
    'proxies': {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890'
    }
})

symbol = 'BTC/USDT'
timeframe = '1m'
limit = 300

def fetch_ohlcv():
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        return ohlcv
    except Exception as e:
        print(f'Error occurred: {e}')
        return []

def calculate_sma(ohlcv, period):
    close_prices = np.array([ohlcv[i][4] for i in range(len(ohlcv))])
    sma = np.mean(close_prices[-period:])
    return sma

def calculate_ema(ohlcv, period):
    close_prices = np.array([ohlcv[i][4] for i in range(len(ohlcv))])
    ema = ta.ema(close_prices, period)[-1]
    return ema

while True:
    ohlcv = fetch_ohlcv()
    if len(ohlcv) >= 20:
        sma20 = calculate_sma(ohlcv, 20)
        ema20 = calculate_ema(ohlcv, 20)
        if abs(sma20 - ema20) < 0.001:  # 如果SMA20和EMA20接近
            print("SMA20和EMA20即将接近")
    time.sleep(60)  # 等待1分钟