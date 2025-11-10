from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment

from plugins.group_chat.group_chatbot import GroupChatbot
from utils.tts_client import TTSService
import random

chatbots = {}
tts_client = TTSService(model="qwen-tts")

normal_chat_matcher = on_message(rule=None, priority=100, block=True)

@normal_chat_matcher.handle()
async def handle_normal_chat(event: GroupMessageEvent):
    chatid = event.group_id
    if chatid not in chatbots:
        chatbots[chatid] = GroupChatbot()
    message = event.get_plaintext()
    userid = event.get_user_id()
    response = chatbots[chatid].dealMessage(message=message, userid=userid, is_mentioned=event.is_tome())
    if response:
        if random.random() < 0.1:
            response = MessageSegment.record(tts_client.synthesize(response))
        elif event.is_tome():
            await normal_chat_matcher.finish([MessageSegment.at(userid), ' ' + response])
        await normal_chat_matcher.finish(response)
