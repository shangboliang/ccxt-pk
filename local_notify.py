# -*- coding: utf-8 -*-

import io
import sys
import ccxt
import asyncio
import telegram
from telegram.ext import ApplicationBuilder, ContextTypes, Updater, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import threading

import time
import pandas_ta as ta
import pandas as pd
from pytz import timezone
import traceback
import logging
import winsound
import time

from alarm_player import play_alarm_music


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
file = open("local.log", encoding="utf-8", mode="a")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=file,
    level=logging.INFO,
 )

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
timeframe = '5m'
limit = 300

def fetch_ohlcv():
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        return ohlcv
    except Exception as e:
        print(f'Error occurred: {e}')
        return []
while True:
    ohlcv = fetch_ohlcv()
    if len(ohlcv) >= 20:
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # 将时间从UTC转换为UTC+8
        utc = timezone('UTC')
        utc_plus_8 = timezone('Asia/Shanghai')
        df['datetime'] = df['datetime'].dt.tz_localize(utc).dt.tz_convert(utc_plus_8)
                
        # -------------------  EMA----------------------------------------------------------------
        ema20 =df.ta.ema(close='close',length=20)
        
        # 计算SMA20，添加到表头
        sema20 = ema20.rolling(window=20).mean()
        ema_sma_percent_diff = round(((ema20 - sema20) / sema20) * 100, 3)

        # 打印DataFrame
        # print(df)
        df['ema20'] = ema20
        df['sma20'] = sema20
        df['ema_sma_percent_diff'] = ema_sma_percent_diff
        if (ema_sma_percent_diff<=0.01):
            logging.info(f'警报:{symbol},text:')
            play_alarm_music()
        # --------------- RSI -----------------------------------------------------------------------   
        rsi_length = 100
        df = pd.concat([df, df.ta.rsi(length=rsi_length)], axis=1)


    time.sleep(60)  # 等待1分钟