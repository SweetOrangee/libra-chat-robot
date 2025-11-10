import os
import dashscope
from dashscope.audio.qwen_tts import SpeechSynthesizer
from models.model_config import model_config

class TTSService:
    """阿里云百炼TTS语音合成服务类"""
    
    def __init__(self, model="qwen3-tts-flash"):
        tts_config = model_config.get_model_config(model)
        self.api_key = tts_config['api_key']
        self.model = tts_config['model_name']
        self.voice = tts_config['voice']
        self.language_type = tts_config['language']

    def synthesize(self, text):
        """
        文本转语音接口
        
        参数:
            text (str): 需要转换的文本内容
            
        返回:
            dashscope.Response: 语音合成结果，包含音频数据等信息
        """
        if not isinstance(text, str) or not text.strip():
            raise ValueError("输入文本不能为空且必须为字符串类型")
            
        try:
            # 调用TTS接口
            response = SpeechSynthesizer.call(
                model=self.model,
                api_key=self.api_key,
                text=text,
                voice=self.voice,
                language_type=self.language_type
            )
            
            # 检查返回状态
            if response.status_code != 200:
                raise RuntimeError(f"语音合成失败: {response.message} (状态码: {response.status_code})")
                
            return response['output']['audio']['url']
            
        except Exception as e:
            raise RuntimeError(f"语音合成过程发生错误: {str(e)}")


# 使用示例
if __name__ == "__main__":
    try:
        # 初始化TTS服务（默认从环境变量获取API密钥）
        tts_service = TTSService(
            model="qwen_tts"
        )
        # 待合成文本
        text = "我是奶龙，我才是奶龙"
        # 调用合成接口
        result = tts_service.synthesize(text)
        print(result)
        # 处理结果（示例：保存音频到文件）
        if hasattr(result, 'audio_data'):
            with open("tts_result.wav", "wb") as f:
                f.write(result.audio_data)
            print("语音合成成功，已保存为tts_result.wav")
        else:
            print("语音合成结果:", result)
           
    except Exception as e:
        print(f"发生错误: {e}")