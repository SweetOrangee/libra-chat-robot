# models/base_model.py
from openai import OpenAI
from typing import Optional, Dict, Any
from .model_config import model_config

class BaseModel:
    def __init__(self, model_name: str = None):
        """初始化基础模型"""
        self.model_config = model_config.get_model_config(model_name)
        self.client = self._create_client()
        self.model_name = self.model_config['model_name']
    
    def _create_client(self) -> OpenAI:
        """创建OpenAI客户端"""
        return OpenAI(
            api_key=self.model_config['api_key'],
            base_url=self.model_config['base_url']
        )
    
    def chat_completion(self, 
                       messages: list, 
                       max_tokens: Optional[int] = None,
                       temperature: Optional[float] = None,
                       **kwargs) -> Any:
        """通用的聊天补全方法"""
        
        completion_args = {
            'model': self.model_name,
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': temperature,
            **kwargs
        }
        
        # 移除None值参数
        completion_args = {k: v for k, v in completion_args.items() if v is not None}
        
        return self.client.chat.completions.create(**completion_args)