import ccxt
import time
import matplotlib.pyplot as plt

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
        ohlcvs = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        return ohlcvs
    except Exception as e:
        print(f'Error occurred: {e}')
        return []

def plot_ohlcv(ohlcvs):
    if len(ohlcvs) == 0:
        return
    print(ohlcvs)
    timestamps = [ohlcv[0] for ohlcv in ohlcvs]
    closing_prices = [ohlcv[4] for ohlcv in ohlcvs]

    plt.plot(timestamps, closing_prices)
    plt.xlabel('Timestamp')
    plt.ylabel('Closing Price')
    plt.title('BTC/USDT OHLCV Data')
    plt.xticks(rotation=45)
    plt.show()

while True:
    ohlcvs = fetch_ohlcv()
    plot_ohlcv(ohlcvs)
    time.sleep(60)  # 等待1分钟