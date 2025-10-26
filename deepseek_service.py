import json
import requests
from config import Config

class DeepSeekService:
    """DeepSeek AI服务层"""

    def __init__(self):
        self.api_key = Config.DEEPSEEK_API_KEY
        self.base_url = Config.DEEPSEEK_BASE_URL

    async def analyze_navigation_intent(self, user_input: str) -> dict:
        """
        分析用户导航意图

        Args:
            user_input: 用户输入的文本

        Returns:
            dict: 解析结果，包含起点、终点、地图选择等信息
        """
        prompt = f"""
        请分析以下用户输入的导航请求，提取关键信息并返回JSON格式结果：

        用户输入：{user_input}

        请提取以下信息：
        1. 起点位置（origin）
        2. 终点位置（destination）
        3. 推荐使用的地图服务（baidu_map 或 amap）
        4. 导航模式（默认使用公共交通）

        返回JSON格式：
        {{
            "origin": "起点地址",
            "destination": "终点地址",
            "map_service": "baidu_map 或 amap",
            "transport_mode": "transit",
            "confidence": 0.95
        }}

        如果无法确定起点或终点，请返回null值。
        """

        try:
            response = await self._call_deepseek_api(prompt)
            result = self._parse_response(response)
            return result
        except Exception as e:
            print(f"DeepSeek API调用失败: {e}")
            return {
                "origin": None,
                "destination": None,
                "map_service": "baidu_map",
                "transport_mode": "transit",
                "confidence": 0.0,
                "error": str(e)
            }

    async def _call_deepseek_api(self, prompt: str) -> str:
        """调用DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 1000
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"API调用失败: {response.status_code} - {response.text}")

        result = response.json()
        return result["choices"][0]["message"]["content"]

    def _parse_response(self, response_text: str) -> dict:
        """解析DeepSeek的响应"""
        try:
            # 尝试从响应中提取JSON
            lines = response_text.strip().split('\n')
            json_start = None
            json_end = None

            for i, line in enumerate(lines):
                if line.strip().startswith('{'):
                    json_start = i
                if line.strip().endswith('}'):
                    json_end = i
                    break

            if json_start is not None and json_end is not None:
                json_str = '\n'.join(lines[json_start:json_end+1])
                result = json.loads(json_str)

                # 验证必要字段
                required_fields = ["origin", "destination", "map_service"]
                for field in required_fields:
                    if field not in result:
                        result[field] = None

                if "transport_mode" not in result:
                    result["transport_mode"] = "transit"
                if "confidence" not in result:
                    result["confidence"] = 0.8

                return result
            else:
                raise ValueError("未找到有效的JSON响应")

        except (json.JSONDecodeError, ValueError) as e:
            print(f"解析响应失败: {e}")
            return {
                "origin": None,
                "destination": None,
                "map_service": "baidu_map",
                "transport_mode": "transit",
                "confidence": 0.0,
                "error": f"解析失败: {str(e)}"
            }

    async def validate_address(self, address: str) -> dict:
        """验证地址有效性"""
        prompt = f"""
        请验证以下地址是否是一个有效的地理位置：
        地址：{address}

        返回JSON格式：
        {{
            "is_valid": true/false,
            "standardized_address": "标准化后的地址",
            "confidence": 0.95
        }}
        """

        try:
            response = await self._call_deepseek_api(prompt)
            result = self._parse_response(response)
            return result
        except Exception as e:
            return {
                "is_valid": False,
                "standardized_address": address,
                "confidence": 0.0,
                "error": str(e)
            }