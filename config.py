import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置类"""

    # DeepSeek配置
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')

    # 百度地图配置
    BAIDU_MAP_AK = os.getenv('BAIDU_MAP_AK')
    BAIDU_MCP_URL = f"https://mcp.map.baidu.com/api/v1/mcp?ak={BAIDU_MAP_AK}"

    # 高德地图配置
    AMAP_KEY = os.getenv('AMAP_KEY')
    AMAP_MCP_URL = f"https://mcp.amap.com/api/v1/mcp?key={AMAP_KEY}"

    # 应用配置
    APP_HOST = os.getenv('APP_HOST', '127.0.0.1')
    APP_PORT = int(os.getenv('APP_PORT', 8000))

    @classmethod
    def validate_config(cls):
        """验证配置是否完整"""
        missing = []
        if not cls.DEEPSEEK_API_KEY:
            missing.append('DEEPSEEK_API_KEY')
        if not cls.BAIDU_MAP_AK:
            missing.append('BAIDU_MAP_AK')
        if not cls.AMAP_KEY:
            missing.append('AMAP_KEY')

        if missing:
            raise ValueError(f"缺少必要的环境变量: {', '.join(missing)}")

        print("配置验证通过")