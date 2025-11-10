import nonebot
from nonebot.adapters.onebot import V11Adapter as OnebotAdapter  # 避免重复命名
nonebot.init()

from pathlib import Path

driver = nonebot.get_driver()
driver.register_adapter(OnebotAdapter)

# 在这里加载插件
nonebot.load_plugin(Path("plugins/woshi.py"))  # “我是奶龙”复读功能
nonebot.load_plugin(Path("plugins/poke.py"))  # 戳一戳回复功能
nonebot.load_plugin(Path("plugins/group_chat"))  # 戳一戳回复功能
nonebot.load_plugin(Path("plugins/tarot"))  # 戳一戳回复功能
# nonebot.load_plugin(Path("plugins/song"))  # 本地插件
if __name__ == "__main__":
    nonebot.run()