from nonebot import on_message
from nonebot.adapters.onebot.v11 import Message, Event, MessageSegment
from nonebot.matcher import Matcher

from .tarot_intent import intent_recognizer, llm_intent_recognizer
from .tarot import TarotGPT

import base64
from pathlib import Path

tarot_client = TarotGPT()

async def tarot_check(event: Event) -> bool:
    user_message = event.get_plaintext()
    return intent_recognizer.rule_based_check(user_message)

tarot_matcher = on_message(priority=11, block=False)

state = {}

@tarot_matcher.handle()
async def handle_tarot(event: Event, matcher: Matcher):
    message = event.get_plaintext()
    user_id = event.get_user_id()
    # 初始化用户状态
    if user_id not in state:
        state[user_id] = {"stage": "initial"}
    
    user_state = state[user_id]
    
    # 初始阶段：识别占卜意图
    if user_state["stage"] == "initial":
        # 先进行规则判断
        if event.to_me and intent_recognizer.rule_based_check(message):
            # 规则判断通过，再进行模型判断
            result = llm_intent_recognizer.model_based_recognize(message)
            print(f"意图识别结果: {result}")
            
            if result['result'] == 'yes':
                # 抽取塔罗牌
                card_result = tarot_client.draw_card()
                card_name = card_result['display_name']
                user_state.update({
                    "stage": "waiting_interpretation",
                    "question": result['question'],
                    "card": card_name
                })
                img_path = Path(card_result['path'])
                
                # 读取图片并转换为 Base64
                with open(img_path, "rb") as f:
                    img_data = f.read()
                base64_str = base64.b64encode(img_data).decode("utf-8")
                
                await tarot_matcher.send(Message([
                    f"🔮 你抽到了：{card_name}\n",
                    MessageSegment.image(f"base64://{base64_str}"), 
                    f"需要我帮你解读这张牌吗？"]))
                matcher.stop_propagation()
            else:
                # 模型判断没有占卜意图，重置状态
                user_state["stage"] = "initial"
        else:
            # 规则判断没有占卜意图，重置状态
            user_state["stage"] = "initial"
    
    # 等待解读确认阶段
    elif user_state["stage"] == "waiting_interpretation":
        # 检查用户是否确认解读
        if message.lower() in ["是", "需要", "要", "解读", "yes", "y", "好", "ok", "1", "帮我解读", "好呀", "好啊"]:
            # 进行牌面解读
            interpretation = tarot_client.interpret_single_card(user_state["question"], user_state["card"])
            await matcher.send(interpretation)
            user_state["stage"] = "initial"
            matcher.stop_propagation()
        else:
            user_state["stage"] = "initial"
            matcher.stop_propagation()