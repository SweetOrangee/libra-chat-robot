# services/llm_intent_recognizer.py
from models.model_factory import create_model
import json
import re

# services/intent_recognizer.py
import re

class IntentRecognizer:
    def __init__(self):
        """初始化意图识别器"""
        # 占卜相关关键词
        self.divination_keywords = [
            "占卜", "塔罗", "运势", "运气", "预测", 
            "未来", "命运", "缘分", "桃花", "事业", "财运", "健康",
            "感情", "爱情", "婚姻", "工作", "学业", "考试"
        ]
        
        # 请求词
        self.request_words = ["帮我", "给我", "想要", "请", "占卜", "算命", "算卦", "测一下", "看一下"]
    
    def rule_based_check(self, user_input: str) -> bool:
        """基于规则的意图判断
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            bool: 是否有占卜意图
        """
        # 检查是否包含占卜关键词
        has_keyword = any(keyword in user_input for keyword in self.divination_keywords)
        
        # 检查是否有请求词
        has_request = any(word in user_input for word in self.request_words)
        
        # 如果有占卜关键词且有请求词，判断为有占卜意图
        return has_keyword and has_request
    
    def extract_question_by_rule(self, user_input: str) -> str:
        """基于规则提取占卜问题
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            str: 提取的占卜问题
        """
        # 去除请求词，保留核心问题
        question = user_input
        for word in self.request_words:
            question = question.replace(word, "")
        
        question = question.strip()
        
        # 如果问题为空，返回默认问题
        if not question:
            return "近期的运势如何"
        
        return question

# 全局意图识别器实例

class LLMIntentRecognizer:
    def __init__(self):
        """初始化LLM意图识别器"""
        self.model = create_model('spark-lite')
    
    def model_based_recognize(self, user_input: str) -> dict:
        """使用LLM识别占卜意图并提取问题
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            dict: 识别结果，包含result和question字段
        """
        prompt = f"""
请分析以下用户输入，判断用户是否有发起塔罗牌占卜的意图。

用户输入："{user_input}"

分析要求：
1. 如果用户明确要求占卜、算命、预测，或者询问运势等，判断为有占卜意图
2. 如果用户只是讨论之前的占卜结果、表达感谢等，判断为无占卜意图
3. 如果有占卜意图，请从用户输入中提取出具体的占卜问题
4. 输出格式必须为JSON：{{"result": "yes"或"no", "question": "提取的问题"}}

示例：
输入：我最近成绩不好，帮我占卜下原因
输出：{{"result": "yes", "question": "我最近成绩不好，原因是什么"}}

输入：你的占卜结果真准啊
输出：{{"result": "no"}}

现在请分析上面的用户输入：
"""
        
        messages = [
            {
                "role": "system", 
                "content": "你是一个专业的意图识别助手，能够准确判断用户是否有占卜意图，并严格按照JSON格式输出结果。"
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]
        
        try:
            response = self.model.chat_completion(
                messages=messages,
                max_tokens=500,
                temperature=0.1  # 低温度确保输出稳定
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 尝试解析JSON
            try:
                result = json.loads(result_text)
                # 验证结果格式
                if "result" not in result:
                    return {"result": "no"}
                if result["result"] == "yes" and "question" not in result:
                    # 如果模型没有提取问题，使用规则方法提取
                    result["question"] = intent_recognizer.extract_question_by_rule(user_input)
                return result
            except json.JSONDecodeError:
                # 如果JSON解析失败，使用正则表达式提取
                return self._fallback_parse(result_text, user_input)
                
        except Exception as e:
            # 如果API调用失败，使用基于规则的方法
            if intent_recognizer.rule_based_check(user_input):
                return {
                    "result": "yes",
                    "question": intent_recognizer.extract_question_by_rule(user_input)
                }
            else:
                return {"result": "no"}
    
    def _fallback_parse(self, text: str, user_input: str) -> dict:
        """回退解析方法，用于处理非标准JSON输出"""
        # 查找result字段
        result_match = re.search(r'"result":\s*"(\w+)"', text)
        if not result_match:
            return {"result": "no"}
        
        result = result_match.group(1).lower()
        if result != "yes":
            return {"result": "no"}
        
        # 查找question字段
        question_match = re.search(r'"question":\s*"([^"]*)"', text)
        if question_match:
            return {
                "result": "yes",
                "question": question_match.group(1)
            }
        else:
            # 如果模型没有提取问题，使用规则方法提取
            return {
                "result": "yes",
                "question": intent_recognizer.extract_question_by_rule(user_input)
            }

intent_recognizer = IntentRecognizer()
# 全局LLM意图识别器实例
llm_intent_recognizer = LLMIntentRecognizer()


