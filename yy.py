# -*- coding: utf-8 -*-

import io
import sys
import ccxt
import asyncio
import telegram
from telegram.ext import Updater, CommandHandler
import time
import pandas_ta as ta
import pandas as pd
from pytz import timezone  # 引入时区库
import traceback

# 初始化 CCXT 交易所和 Telegram Bot
exchange = ccxt.binance({
    'enableRateLimit': True,
    'proxies': {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890'
    }
})

TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# 存储用户的订阅信息，用于价格预警
subscriptions = {}
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
print("Starting.... 开始")



# 异步函数，check_ohlcv
async def check_ohlcv():
    while True:
        subscriptions = {
                    ('BTC/USDT', '1h'): {
                        'chat_id_1': [
                            {
                                'indicator': 'price',
                                'threshold': 100
                            },
                            {
                                'indicator': 'volume',
                                'threshold': 10000
                            }
                        ],
                    },
                    ('ETH/USDT', '4h'): {
                        'chat_id_3': [
                            {
                                'indicator': 'price',
                                'threshold': 200
                            },
                            {
                                'indicator': 'volume',
                                'threshold': 5000
                            }
                        ],
                    },
                }
        if subscriptions:
            print(subscriptions)
            for symbol, timeframe in subscriptions.keys():
                try:
                    # 查询 OHLCV 数据
                    print(symbol, timeframe)
                    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
                    print('OHLCV success ...')

                    for chat_id, indicator_thresholds  in subscriptions[(symbol, timeframe)].items():
                        indicatorList = [] 
                        thresholdList = []
                        for indicator_threshold in indicator_thresholds:
                            indicatorList.append(indicator_threshold['indicator'])
                            thresholdList.append(indicator_threshold['threshold'])

                        latest_ohlcv = ohlcv[-1]
                        close_price = latest_ohlcv[4]  # 收盘价
                        
                        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
                        
                        # 将时间从UTC转换为UTC+8
                        utc = timezone('UTC')
                        utc_plus_8 = timezone('Asia/Shanghai')
                        df['datetime'] = df['datetime'].dt.tz_localize(utc).dt.tz_convert(utc_plus_8)


                        # -------------------  EMA SMA---------------------------------------------------------------
                        ema20 =df.ta.ema(close='close',length=20)
                        sma20 =df.ta.sma(close='close',length=20)
                        df['ema20'] = ema20
                        df['sma20'] = sma20
                        sema20 = ema20.rolling(window=20).mean()
                        ema_sma_percent_diff = round(((ema20 - sema20) / sema20) * 100, 3)
                        df['ema_sma_percent_diff'] = ema_sma_percent_diff

                        latest_data = df.iloc[-1]
                        print (latest_data)

                        #-------------------  close price---------------------------------------------------------------
                        if 'price' in indicatorList:
                            threshold = thresholdList[indicatorList.index('price')] 
                            if close_price >= threshold:
                                text = f"价格预警：{symbol} 当前收盘价：{close_price}"
                                print(text)
                                # bot.send_message(chat_id=chat_id, text=text)
                                
                        # -------------------  SMA-EMA---------------------------------------------------------------
                        if 'ema' in indicatorList:
                            threshold = thresholdList[indicatorList.index('ema')] 
                            pass
                        if 'sma' in indicatorList:
                            threshold = thresholdList[indicatorList.index('sma')] 
                            # 执行 SMA 预警逻辑
                            pass
                        if 'ema_sma_percent_diff' in indicatorList:
                            threshold = thresholdList[indicatorList.index('ema_sma_percent_diff')] 
                            # 计算SEMA20，添加到表头
                            if abs(latest_data['ema_sma_percent_diff'])<0.01:
                                text = f"sema预警：{symbol} 当前收盘价：{close_price}"
                                print(text)
                                # bot.send_message(chat_id=chat_id, text=text)
                        
                        if 'rsi' in indicatorList:
                            # 执行 RSI 预警逻辑
                            pass
                        if 'boll' in indicatorList:
                            # 执行 Bollinger 预警逻辑
                            pass
                        await asyncio.sleep(1)
                except Exception as e:
                    traceback.print_exc()  # 打印异常的堆栈跟踪信息

                    # 处理异常
                    print(f"发生异常：{str(e)}")
                    pass
            print('--------------------------------')
        
        # 等待一分钟
            # await asyncio.sleep(2)

# 主函数
def main():
    asyncio.run(check_ohlcv())

if __name__ == "__main__":
    main()