# -*- coding: utf-8 -*-

import io
import sys
import ccxt
import asyncio
import telegram
from telegram.ext import ApplicationBuilder, ContextTypes, Updater, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import threading
import json
import time
import pandas_ta as ta
import pandas as pd
from pytz import timezone
import traceback
import logging

from symbol_sub_option import add_subscription

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
file = open("execution1015.log", encoding="utf-8", mode="a")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=file,
    level=logging.INFO,
 )

exchange = ccxt.binance({
    'enableRateLimit': True,
    'proxies': {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890'
    }
})

TELEGRAM_TOKEN = '6503931335:AAFulgnXGn0CjFpvsUe7N6TA7IpDSV4kMZU'
bot = telegram.Bot(TELEGRAM_TOKEN)
logging.info(f'me:{bot.get_me}')
# subscriptions = {
#     ('BTC/USDT', '1h'): {
#         '5381545264': [
#             {
#                 'indicator': 'price',
#                 'threshold': 100,
#                 'metoh':'gt/le/amplitude',
#                 'notification_frequency':1
#             }
#         ]
#     }
# }
subscriptions = {
}
logging.info("Starting.... 开始")

user_sub_pre = {}

async def check_ohlcv(context: ContextTypes.DEFAULT_TYPE):
    # while True:
        if subscriptions:
            logging.info(f"subscriptions: {subscriptions}")
            for symbol, timeframe in subscriptions.keys():
                try:
                    logging.info(f"symbol: {symbol},timeframe:{timeframe}")
                    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
                    logging.info('OHLCV success ...')

                    for chat_id, indicator_thresholds in subscriptions[(symbol, timeframe)].items():
                        indicatorList = []
                        thresholdList = []
                        for indicator_threshold in indicator_thresholds:
                            indicatorList.append(indicator_threshold['indicator'])
                            thresholdList.append(indicator_threshold['threshold'])

                        latest_ohlcv = ohlcv[-1]
                        close_price = latest_ohlcv[4]

                        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')

                        utc = timezone('UTC')
                        utc_plus_8 = timezone('Asia/Shanghai')
                        df['datetime'] = df['datetime'].dt.tz_localize(utc).dt.tz_convert(utc_plus_8)

                        ema20 = df.ta.ema(close='close', length=20)
                        sma20 = df.ta.sma(close='close', length=20)
                        df['ema20'] = ema20
                        sema20 = ema20.rolling(window=20).mean()
                        df['sema20'] = sema20
                        ema_sma_percent_diff = round(((ema20 - sema20) / sema20) * 100, 3)
                        df['ema_sma_percent_diff'] = ema_sma_percent_diff
                        second_latest_data = df.iloc[-2]

                        latest_data = df.iloc[-1]
                        logging.info(f'latest_data:{latest_data}')

                        if 'price' in indicatorList:
                            threshold = thresholdList[indicatorList.index('price')]
                            if close_price >= threshold:
                                text = f"价格预警U+1F642：{symbol} 预警价格：{threshold} 当前价：{close_price}"
                                logging.info(f'chat_id:{chat_id},text:{text}')
                                await context.bot.send_message(chat_id=chat_id, text=text)

                        if 'ema' in indicatorList:
                            threshold = thresholdList[indicatorList.index('ema')]
                            pass
                        if 'sma' in indicatorList:
                            threshold = thresholdList[indicatorList.index('sma')]
                            pass
                        if 'ema_sma_percent_diff' in indicatorList:
                            threshold = thresholdList[indicatorList.index('ema_sma_percent_diff')]
                            threshold = float(threshold)
                            if abs(latest_data['ema_sma_percent_diff']) < threshold:
                                text = f"sema预警{symbol} 当前价：{close_price}"
                                logging.info(f'{text}')
                                await context.bot.send_message(chat_id=chat_id, text=text)
                            if (second_latest_data['ema_sma_percent_diff'] > 0 and latest_data['ema_sma_percent_diff'] < 0) or (second_latest_data['ema_sma_percent_diff'] < 0 and latest_data['ema_sma_percent_diff'] > 0):
                                text = f"sema预警{symbol} 当前价：{close_price},{timeframe}级别反转"
                                await context.bot.send_message(chat_id=chat_id, text=text)
                        if 'rsi' in indicatorList:
                            pass
                        if 'boll' in indicatorList:
                            pass
                        #发起请求间隔睡眠时间
                        await asyncio.sleep(1)
                except Exception as e:
                    traceback.print_exc()
                    logging.info(f"发生异常：{str(e)}")
                    pass
            logging.info('--------------------------------')
        logging.info('no data available???')
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    text = "欢迎使用预警工具！\n\n请使用/subscribe命令来订阅交易对。"
    await context.bot.send_message(chat_id=chat_id, text=text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("/sub BTC/USDT:USDT 5m sema 20000 1")

async def sub_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = context.args
    add_subscription(subscriptions=subscriptions, symbol=data[0], timeframe=data[1], chat_id=update.message.chat_id, indicator=data[2], threshold=data[3])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=str(subscriptions))

async def get_allsub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text=str(subscriptions))
async def set_allsub_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    subscriptions_str=''.join(context.args)
    logging.info(f'{subscriptions_str}')
    subscriptions = json.loads(subscriptions_str)
    logging.info(f'{subscriptions}')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=str(subscriptions))

def run_bot():
    proxy_url = 'http://127.0.0.1:7890'
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).proxy_url(proxy_url).get_updates_proxy_url(proxy_url).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler('sub', sub_handle))
    application.add_handler(CommandHandler('setup', set_allsub_handle))
    application.add_handler(CommandHandler("getall", get_allsub))
    job_queue = application.job_queue
    job_queue.run_repeating(check_ohlcv, interval=60, first=10)
    application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)


# 主函数
def main():
    run_bot()

if __name__ == "__main__":
    main()


