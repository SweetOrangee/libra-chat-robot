from nonebot import on_startswith, Bot
from nonebot.adapters.onebot.v11 import Event
import asyncio

woshi_matcher = on_startswith(msg="我是", rule=None, priority=10, block=True)

async def get_history_chat(bot: Bot, group_id: int):
    messages = []
    try:
        history = await bot.get_group_msg_history(
            group_id=group_id,
            count=10,
        )
        for message in history["messages"]:
            sender = message["sender"]["card"] or message["sender"]["nickname"]
            text_messages = []
            if isinstance(message["message"], list):
                text_messages = [msg["data"]["text"] for msg in message["message"] if msg["type"] == "text"]
            elif isinstance(message["message"], str) and "CQ:" not in message["message"]:
                text_messages = [message["message"]]
            messages.extend([f"{sender}: {text}" for text in text_messages])
    except Exception as e:
        raise Exception(f"获取聊天记录失败,错误信息: {e!s}")
    print(messages)
    return messages

@woshi_matcher.handle()
async def handle_function(bot: Bot, event: Event):
    group_id = event.group_id
    message = event.get_plaintext()
    await get_history_chat(bot, group_id)
    await asyncio.sleep(2)
    if len(message) > 2:
        response = '我才是' + message[2:]
        await woshi_matcher.finish(response)

