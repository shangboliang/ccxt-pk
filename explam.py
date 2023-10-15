import ccxt.pro
from asyncio import run

print('CCXT Pro version', ccxt.pro.__version__)


async def main():
    exchange = ccxt.pro.binance({
    'enableRateLimit': True,
    'newUpdates': True
        }
    )
    exchange.socks_proxy='socks5://127.0.0.1:7890' 
    # Python
    if exchange.has['watchOHLCV']:
        while True:
            try:
                candles = await exchange.watch_ohlcv('HFT/USDT:USDT', timeframe='5m',  limit=100)
                print(exchange.iso8601(exchange.milliseconds()), candles)
            except Exception as e:
                print(e)
                # stop the loop on exception or leave it commented to retry
                # raise e
    exchange.close();



run(main())