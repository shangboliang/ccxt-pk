import ccxt
import time
    # 'apiKey': 'YOUR_API_KEY',
    # 'secret': 'YOUR_SECRET',
exchange = ccxt.binance({
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
        ohlcvs = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        print(ohlcvs)
    except Exception as e:
        print(f'Error occurred: {e}')

while True:
    fetch_ohlcv()
    time.sleep(60)  # 等待1分钟