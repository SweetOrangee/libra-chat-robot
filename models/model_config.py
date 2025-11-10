import json
import os
from typing import Dict, Any

class ModelConfig:
    def __init__(self, config_path: str = "config/model_config.json"):
        self.config_path = config_path
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return config
    
    def get_model_config(self, model_name: str = None) -> Dict[str, Any]:
        """获取指定模型的配置"""
        if model_name is None:
            model_name = self._config.get('default_model')
        
        if model_name not in self._config['models']:
            raise ValueError(f"未知的模型: {model_name}")
        
        return self._config['models'][model_name].copy()
    
    def get_all_models(self) -> list:
        """获取所有可用的模型名称"""
        return list(self._config['models'].keys())

# 全局配置实例
model_config = ModelConfig()