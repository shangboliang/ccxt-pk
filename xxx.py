import ccxt
import telegram
from telegram.ext import Updater, CommandHandler

# 设置Telegram Bot的API令牌
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# 创建Telegram Bot的实例
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# 创建CCXT交易所实例
exchange = ccxt.binance({
    'enableRateLimit': True,
    'proxies': {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890'
    }
})

# 存储用户订阅的交易对和预警设置
subscriptions = {}

print('CCXT Version:', ccxt.__version__)

# 处理/start命令
def start(update, context):
    chat_id = update.message.chat_id
    text = "欢迎使用行情预警工具！\n\n请使用/subscribe命令来订阅交易对。"
    context.bot.send_message(chat_id=chat_id, text=text)

# 处理/subscribe命令
def subscribe(update, context):
    chat_id = update.message.chat_id
    text = "请输入您要订阅的交易对，格式为'交易对:基准货币'（例如：BTC/USDT:USDT）："
    context.bot.send_message(chat_id=chat_id, text=text)
    subscriptions[chat_id] = {}

# 处理输入的交易对
def handle_symbol(update, context):
    chat_id = update.message.chat_id
    symbol = update.message.text.upper()
    subscriptions[chat_id]['symbol'] = symbol
    text = f"您已成功订阅交易对：{symbol}\n\n请输入阈值："
    context.bot.send_message(chat_id=chat_id, text=text)

# 处理输入的阈值
def handle_threshold(update, context):
    chat_id = update.message.chat_id
    threshold = float(update.message.text)
    subscriptions[chat_id]['threshold'] = threshold
    text = "您已成功设置预警功能！"
    context.bot.send_message(chat_id=chat_id, text=text)

# 异步监听行情数据变化
def listen_market_data():
    while True:
        for chat_id, subscription in subscriptions.items():
            symbol = subscription['symbol']
            threshold = subscription['threshold']
            try:
                # 获取最新的行情数据
                ticker = exchange.fetch_ticker(symbol)
                # 进行相应的行情分析并发送通知
                if ticker['last'] > threshold:
                    text = f"价格超过阈值：{symbol} 当前价格：{ticker['last']}"
                    bot.send_message(chat_id=chat_id, text=text)
            except Exception as e:
                # 发生异常时，发送通知给Bot管理员
                admin_chat_id = 'ADMIN_CHAT_ID'
                text = f"获取行情数据出错：{str(e)}"
                bot.send_message(chat_id=admin_chat_id, text=text)

# 创建Updater和Dispatcher，并添加处理程序
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('subscribe', subscribe))
dispatcher.add_handler(CommandHandler('threshold', handle_threshold))

# 启动Bot
updater.start_polling()

# 异步监听行情数据变化
listen_market_data()