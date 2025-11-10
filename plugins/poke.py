from nonebot import on_notice
from nonebot.adapters.onebot.v11 import PokeNotifyEvent, NoticeEvent, MessageSegment
import random

group_poke = on_notice()

@group_poke.handle()
async def _(event: NoticeEvent):
    if isinstance(event, PokeNotifyEvent):
        if event.target_id == event.self_id: 
            group_id = event.group_id
            user_id = event.user_id
            at_back = MessageSegment.at(user_id)
            poke_responses = [
                "诶嘿！",
                at_back + " 在的哦！",
                "owo",
                at_back + " 怎么戳我！",
                "呜呜",
                "在！",
                at_back + " 干嘛……",
                "哼",
                "awa",
                "干嘛。。。",
                "呀！",
                "呼呼！",
                "哼哼！",
                "不要乱戳哦！",
                "好哦！",
                "戳我干嘛o>_<o",
                "再戳我就咬你啦",
                "不要再戳了……",
                "请……请你不要再戳了(>_<)",
                "啊啊啊，不要戳了",
                "不要戳啦",
                "嗷呜～",
                "哎呀"
            ]
            await group_poke.finish(random.choice(poke_responses))