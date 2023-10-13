# -*- coding: utf-8 -*-

import io
import sys
import ccxt
import asyncio
import telegram
from telegram.ext import Updater, CommandHandler
import time
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
    subscriptions = {
        ('BTC/USDT', '1h'): {
            'chat_id_1': {
                'indicator': 'price',
                'threshold': 100
            },
            'chat_id_2': {
                'indicator': 'volume',
                'threshold': 10000
            }
        },
        ('ETH/USDT', '4h'): {
            'chat_id_3': {
                'indicator': 'price',
                'threshold': 200
            }
        },
    }

    if  subscriptions:
        print(subscriptions)
        for symbol, timeframe in subscriptions.keys():
            try:
                # 查询 OHLCV 数据
                print(symbol, timeframe)
                ohlcv_data =  exchange.fetch_ohlcv(symbol, timeframe,limit=100)
                print('OHLCV sucess')
                # 获取最新的 OHLCV 数据
                latest_ohlcv = ohlcv_data[-1]
                close_price = latest_ohlcv[4]  # 收盘价
                # 获取最新的 10 行 OHLCV 数据
                latest_ohlcv = ohlcv_data[-10:]

                # 打印最新的 10 行
                for candle in latest_ohlcv:
                    print(candle)
                #
                for chat_id, user_sub in subscriptions[(symbol, timeframe)].items():
                    indicator = user_sub['indicator']
                    threshold = user_sub['threshold']
                    
                    if indicator == 'price':
                        if close_price >= threshold:
                            text = f"价格预警：{symbol} 当前收盘价：{close_price}"
                            print(text)
                            # bot.send_message(chat_id=chat_id, text=text)
                    
                    # 添加其他指标的逻辑
                    elif indicator == 'ema':
                        # 执行 EMA 预警逻辑
                        pass
                    elif indicator == 'sma':
                        # 执行 SMA 预警逻辑
                        pass
                    elif indicator == 'ma':
                        # 执行 MA 预警逻辑
                        pass
                    elif indicator == 'rsi':
                        # 执行 RSI 预警逻辑
                        pass
                    elif indicator == 'boll':
                        # 执行 Bollinger 预警逻辑
                        pass
            except Exception as e:
                # 处理异常
                print(f"发生异常：{str(e)}")
                pass
        print('--------------------------------')     
      



# 处理用户订阅命令
def subscribe(update, context):
    chat_id = update.message.chat_id
    text = "请输入订阅信息，格式为'symbol-timeframe-indicator-threshold'："
    context.bot.send_message(chat_id=chat_id, text=text)

# 处理用户输入的订阅信息，使用 - 作为分隔符
def handle_subscription(update, context):
    chat_id = update.message.chat_id
    subscription_info = update.message.text.split('-')
    
    if len(subscription_info) == 4:
        symbol, timeframe, indicator, threshold = subscription_info
        if (symbol, timeframe) not in subscriptions:
            subscriptions[(symbol, timeframe)] = {}
        subscriptions[(symbol, timeframe)][chat_id] = {
            'indicator': indicator,
            'threshold': float(threshold)
        }
        text = "您已成功订阅价格预警！"
    else:
        text = "请输入有效的订阅信息，格式为'symbol-timeframe-indicator-threshold'，使用连字符分隔。"
    context.bot.send_message(chat_id=chat_id, text=text)

# 主函数
def main():
    # # updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    # dispatcher = updater.dispatcher

    # # 添加处理程序
    # dispatcher.add_handler(CommandHandler('subscribe', subscribe))
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_subscription))

    # # 启动Bot
    # updater.start_polling()

    # 启动异步价格查询任务
    while True:
        check_ohlcv()
    # loop = asyncio.get_event_loop()
    # loop.create_task(check_prices())
    # loop.create_task(check_ohlcv())
    # loop.run_forever()

    # # 在这里加入外部睡眠
    # try:
    #     loop.run_forever()
    # except KeyboardInterrupt:
    #     print("Program terminated.")

if __name__ == "__main__":
    main()

