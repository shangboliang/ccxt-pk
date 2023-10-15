def add_subscription(subscriptions, symbol, timeframe, chat_id, indicator, threshold):
    if (symbol, timeframe) not in subscriptions:
        subscriptions[(symbol, timeframe)] = {}
    if chat_id not in subscriptions[(symbol, timeframe)]:
        subscriptions[(symbol, timeframe)][chat_id] = []
    subscriptions[(symbol, timeframe)][chat_id].append({'indicator': indicator, 'threshold': threshold})

def remove_subscription(subscriptions, symbol, timeframe, chat_id):
    if (symbol, timeframe) in subscriptions and chat_id in subscriptions[(symbol, timeframe)]:
        del subscriptions[(symbol, timeframe)][chat_id]
        if not subscriptions[(symbol, timeframe)]:
            del subscriptions[(symbol, timeframe)]

def update_subscription(subscriptions, symbol, timeframe, chat_id, old_indicator, old_threshold, new_indicator, new_threshold):
    if (symbol, timeframe) in subscriptions and chat_id in subscriptions[(symbol, timeframe)]:
        for subscription in subscriptions[(symbol, timeframe)][chat_id]:
            if subscription['indicator'] == old_indicator and subscription['threshold'] == old_threshold:
                subscription['indicator'] = new_indicator
                subscription['threshold'] = new_threshold
                break

def get_all_subscriptions(subscriptions):
    return subscriptions

def get_symbol_timeframe_subscriptions(subscriptions, symbol, timeframe):
    if (symbol, timeframe) in subscriptions:
        return subscriptions[(symbol, timeframe)]
    return {}

def get_chat_subscriptions(subscriptions,chat_id):
    chat_subscriptions = []
    for symbol_timeframe, subscriptions_dict in subscriptions.items():
        for sub_chat_id, indicator_thresholds in subscriptions_dict.items():
            if sub_chat_id == chat_id:
                chat_subscriptions.extend(indicator_thresholds)
    return symbol_timeframe,chat_subscriptions

# 示例用法
# subscriptions = {
#     ('BTC/USDT', '1h'): {
#         'chat_id_1': [
#             {
#                 'indicator': 'price',
#                 'threshold': 100
#             },
#             {
#                 'indicator': 'volume',
#                 'threshold': 10000
#             }
#         ],
#     },
#     ('ETH/USDT', '4h'): {
#         'chat_id_3': [
#             {
#                 'indicator': 'price',
#                 'threshold': 200
#             },
#             {
#                 'indicator': 'volume',
#                 'threshold': 5000
#             }
#         ],
#     },
# }

# chat_id = 'chat_id_1'
# chat_subscriptions = get_chat_subscriptions(chat_id)
# print(chat_subscriptions)

# 添加订阅信息
# add_subscription(subscriptions, 'BTC/USDT', '1h', 'chat_id_2', 'rsi', 70)
# # 删除订阅信息
# remove_subscription(subscriptions, 'ETH/USDT', '4h', 'chat_id_3')

# # 更新订阅信息
# update_subscription(subscriptions, 'BTC/USDT', '1h', 'chat_id_1', 'price', 100, 'price', 150)

# # 获取所有订阅信息
# all_subscriptions = get_all_subscriptions(subscriptions)

# # 获取特定交易对和时间段的订阅信息
# symbol_timeframe_subscriptions = get_symbol_timeframe_subscriptions(subscriptions, 'BTC/USDT', '1h')

# # 获取特定聊天ID的订阅信息
# chat_subscriptions = get_chat_subscriptions(subscriptions, 'BTC/USDT', '1h', 'chat_id_1')
# print(subscriptions)
