import time
import random
import json
from typing import List, Optional, Dict
from models.model_factory import create_model

class OpenAIChatBot:
    def __init__(self, model: str = "spark-lite", prompt_path='prompts/libra_chat.md'):
        # 初始化API客户端
        self.client = create_model(model)
        self.model = model
        
        with open(prompt_path, 'r') as f:
            self.system_prompt = f.read()
    
    def chat(self, recent_messages: List[str]) -> str:
        """根据最近群聊消息生成回复"""
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        for msg in recent_messages[-10:]:
            if msg.startswith("robot: "):
                content = msg[len("robot: "):].strip()
                messages.append({"role": "assistant", "content": content})
            else:
                messages.append({"role": "user", "content": msg})
        
        try:
            completion = self.client.chat_completion(
                model=self.model,
                messages=messages,
                temperature=0.6,  # 降低随机性，减少违规
                max_tokens=100  # 缩短最大长度，避免加前缀
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(e)
            return ""

class GroupChatbot:
    def __init__(self):
        self.chatbot = OpenAIChatBot(model='qwen3-max')
        self.bot_name = "Libra"  # 统一角色名，与OpenAIChatBot的名字一致
        
        # 状态管理变量
        self.recent_messages: List[str] = []
        self.in_dialogue: bool = False
        self.dialogue_start_time: Optional[float] = None
        self.last_replied: bool = False
        
        # 概率参数
        self.base_prob = 0.2
        self.current_prob = self.base_prob
        self.dialogue_boost = 2.0
        self.decay_rate = 0.95
        self.dialogue_decay_count = 0
        
        # 对话退出参数
        self.max_dialogue_duration = 300
        self.exit_keywords = {"不聊这个了", "换个话题", "算了吧", "打住"}
        with open('config/nickname.json', 'r') as f:
            self.user_nickname_dict = json.load(f)

    def _exit_dialogue(self) -> None:
        """退出对话状态，重置相关参数"""
        self.in_dialogue = False
        self.current_prob = self.base_prob
        self.dialogue_start_time = None
        self.dialogue_decay_count = 0

    def _update_recent_messages(self, message: str, userid=None) -> None:
        """更新最近消息列表（保留原逻辑）"""
        if userid in self.user_nickname_dict:
            username = self.user_nickname_dict[userid]
        else:
            username = '用户' + userid[:4]
        dump_message = username + ': ' + message
        self.recent_messages.append(dump_message)
        if len(self.recent_messages) > 30:
            self.recent_messages.pop(0)

    def _filter_username_prefix(self, reply: str) -> str:
        """过滤回复中的用户名前缀（最后一道防线）"""
        if not reply:
            return ""
        # 1. 提取所有已知用户名（包括robot和Libra）
        all_usernames = list(self.user_nickname_dict.values()) + [self.bot_name]
        # 2. 检查回复是否以“用户名+冒号”开头，若是则剔除
        for name in all_usernames:
            if reply.startswith(f"{name}：") or reply.startswith(f"{name}:"):
                # 去掉前缀，保留后面的内容
                return reply[len(f"{name}："):].strip() if reply.startswith(f"{name}：") else reply[len(f"{name}:"):].strip()
        # 3. 无前缀则直接返回
        return reply

    def dealMessage(self, message: str, userid: str = "", is_mentioned: bool = False) -> str:
        """处理群消息，返回机器人回复（空字符串表示不回复）"""
        if not message:
            return ""
        # 1. 更新最近消息列表
        self._update_recent_messages(message, userid=userid)
        now = time.time()

        # 2. 检查是否需要退出对话
        if self.in_dialogue:
            if now - self.dialogue_start_time > self.max_dialogue_duration:
                self._exit_dialogue()
            elif any(keyword in message for keyword in self.exit_keywords):
                self._exit_dialogue()

        # 3. 计算当前回复概率
        if is_mentioned:
            current_prob = 1.0
        else:
            current_prob = self.current_prob if self.in_dialogue else self.base_prob
        # 4. 避免连续回复
        if self.last_replied and not is_mentioned:
            self.last_replied = False
            return ""


        # 5. 随机判断是否回复
        reply_prob = random.random()
        print(current_prob, reply_prob)
        if reply_prob < current_prob:
            # 生成回复 + 过滤前缀
            raw_reply = self.chatbot.chat(self.recent_messages)
            filtered_reply = self._filter_username_prefix(raw_reply)  # 关键：加过滤
            
            # 更新对话状态
            self.last_replied = True
            if not self.in_dialogue:
                self.in_dialogue = True
                self.dialogue_start_time = now
                self.dialogue_decay_count = 0
                self.current_prob = self.base_prob * self.dialogue_boost
            else:
                self.dialogue_decay_count += 1
                new_prob = self.base_prob * self.dialogue_boost * (self.decay_rate ** self.dialogue_decay_count)
                self.current_prob = max(new_prob, self.base_prob)
            self._update_recent_messages(filtered_reply, 'robot')
            return filtered_reply
        else:
            self.last_replied = False
            return ""



if __name__ == "__main__":
    
    bot = GroupChatbot()
    
    # 模拟群聊消息
    test_messages = [
        "今天天气好热啊，快35度了",
        "@群友小助手 你那热不热？",
        "听说下周要降温，可能有雨",
        "降温好啊，终于能凉快几天了",
        "你们周末打算干嘛？",
        "不聊天气了，说说明天吃啥"
    ]
    
    for msg in test_messages:
        print(f"群友: {msg}")
        reply = bot.dealMessage(msg)
        if reply:
            print(f"{bot.bot_name}: {reply}\n")
        else:
            print(f"{bot.bot_name}: （不回复）\n")
        