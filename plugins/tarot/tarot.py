#tarot_gpt.py

import random
import json
import os
from models.model_factory import create_model

class TarotGPT:
    def __init__(self, card_data_path=""):
        """初始化塔罗牌系统
        
        Args:
            card_data_path: 塔罗牌数据JSON文件路径
        """
        # 创建模型客户端，设置系统提示
        self.system_prompt = """你是QQ群聊中23岁的少女塔罗牌占卜师Libra，性格活泼开朗，有点小跳脱。
说话带点可爱语气词（呀、呢、～）和轻松表情（比如😉、✨、😆）。
请用温暖可爱的语气为用户解读塔罗牌，回复保持4-5句话的专业度，同时适合群聊氛围。
不要使用任何markdown格式，用纯文本回复。
解读要包含牌的基本含义、正逆位的影响，以及对用户问题的针对性建议。
保持神秘感但不要做出绝对预测，尊重用户的同时展现你活泼可爱的一面。"""
        
        self.client = create_model('qwen3-max')
        
        self.card_data_path = card_data_path if card_data_path else os.path.join(os.path.dirname(__file__), 'cards')
        
        # 加载塔罗牌数据
        self.card_data = self._load_card_data(os.path.join(self.card_data_path, 'tarot-images.json'))
        self.tarot_deck = [card['name'] for card in self.card_data]
        self.card_data = dict(zip(self.tarot_deck, self.card_data))

    def _load_card_data(self, card_data_path):
        """从JSON文件加载塔罗牌数据
        
        Args:
            card_data_path: JSON文件路径
            
        Returns:
            dict: 塔罗牌数据字典
        """
        with open(card_data_path, 'r', encoding='utf-8') as f:
            return json.load(f)["cards"]
    

    def shuffle_deck(self):
        """洗牌"""
        random.shuffle(self.tarot_deck)
    
    def draw_card(self):
        """抽一张牌
        
        Returns:
            dict: 包含卡片信息和图片路径的字典
        """
        
        card_name = random.choice(self.tarot_deck)
        is_reversed = random.choice([True, False])
        
        # 从数据中获取卡片信息
        card_info = self.card_data[card_name]
        card_filename = card_info["img"]
        if is_reversed:
            card_filename = 'r' + card_filename
        # 添加正逆位信息
        result = {}
        result["display_name"] = f"{card_name} {'(逆位)' if is_reversed else '(正位)'}"
        result["is_reversed"] = is_reversed
        result["path"] = os.path.join(self.card_data_path, card_filename)
        
        return result
    
    def interpret_single_card(self, question, card_name):
        """使用AI解读单张牌
        
        Args:
            question: 用户问题
            card_info: 卡片信息字典
            
        Returns:
            str: 解读结果
        """
        # 构建提示
        prompt = f"用户想知道：{question}\n\n他们抽到了以下塔罗牌：\n"
        prompt += f"抽到的牌：{card_name}\n"
        
        prompt += """请为群友解读这张塔罗牌～（回答用"你"称呼即可）
需要包含：
1. 这张牌的基本含义和象征
2. 正位/逆位的影响
3. 对用户问题的针对性建议

用4-5句话的专业解读，但保持温暖可爱的语气哦！让解读既有深度又容易理解✨"""
        
        # 调用AI进行解读
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        print(messages)
        
        response = self.client.chat_completion(
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
