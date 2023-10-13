
import asyncio
import telegram


async def main():


    bot = telegram.Bot(":")
    async with bot:
        print(await bot.get_me())
        print((await bot.get_updates())[0])
        await bot.send_message(text='Hi Beck!', chat_id=5381545264)



if __name__ == '__main__':
    asyncio.run(main())




################################################################
# Update(message=
#        Message(channel_chat_created=False, chat=Chat(first_name='Beck', id=5381545264, type=<ChatType.PRIVATE>, username='sbl_2022'), 
#                date=datetime.datetime(2023, 10, 13, 10, 49, 5, tzinfo=<UTC>), delete_chat_photo=False, 
#                entities=(MessageEntity(length=6, offset=0, type=<MessageEntityType.BOT_COMMAND>),), 
#                        from_user=User(first_name='Beck', 
#                                       id=5381545264, is_bot=False,
#                                         language_code='zh-hans',
#                                        username='sbl_2022'), 
#                                        group_chat_created=False, message_id=1, 
#                                        supergroup_chat_created=False, 
#                                        text='/start'), 
#                                        update_id=675556209)