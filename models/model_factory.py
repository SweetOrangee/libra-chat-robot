# models/model_factory.py
from models.base_model import BaseModel

class ModelFactory:
    """模型工厂类"""
    
    @staticmethod
    def create_model(model_name: str = None) -> BaseModel:
        """创建指定模型的实例"""
        return BaseModel(model_name)

# 便捷函数
def create_model(model_name: str = None) -> BaseModel:
    """便捷函数：创建模型实例"""
    return ModelFactory.create_model(model_name)