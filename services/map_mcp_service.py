import json
import requests
from config import Config

class MapMCPClient:
    """地图MCP客户端基类"""

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def call_tool(self, tool_name: str, parameters: dict) -> dict:
        """调用MCP工具"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": parameters
                },
                "id": 1
            }

            response = requests.post(
                self.base_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(f"MCP调用失败: {response.status_code}")

            result = response.json()
            if "error" in result:
                raise Exception(f"MCP工具错误: {result['error']}")

            return result.get("result", {})

        except Exception as e:
            print(f"MCP调用异常: {e}")
            raise

class BaiduMapMCPClient(MapMCPClient):
    """百度地图MCP客户端"""

    def __init__(self):
        super().__init__(Config.BAIDU_MCP_URL)

    async def open_navigation(self, origin: str, destination: str, mode: str = "transit") -> dict:
        """
        打开百度地图导航

        Args:
            origin: 起点地址
            destination: 终点地址
            mode: 交通模式 (driving, transit, walking, riding)

        Returns:
            dict: 导航结果
        """
        parameters = {
            "origin": origin,
            "destination": destination,
            "mode": mode
        }

        return await self.call_tool("open_navigation", parameters)

    async def search_place(self, query: str, region: str = None) -> dict:
        """搜索地点"""
        parameters = {"query": query}
        if region:
            parameters["region"] = region

        return await self.call_tool("search_place", parameters)

class AmapMCPClient(MapMCPClient):
    """高德地图MCP客户端"""

    def __init__(self):
        super().__init__(Config.AMAP_MCP_URL)

    async def open_navigation(self, origin: str, destination: str, mode: str = "bus") -> dict:
        """
        打开高德地图导航

        Args:
            origin: 起点地址
            destination: 终点地址
            mode: 交通模式 (car, bus, walk, ride)

        Returns:
            dict: 导航结果
        """
        parameters = {
            "origin": origin,
            "destination": destination,
            "mode": mode
        }

        return await self.call_tool("open_navigation", parameters)

    async def search_place(self, keywords: str, city: str = None) -> dict:
        """搜索地点"""
        parameters = {"keywords": keywords}
        if city:
            parameters["city"] = city

        return await self.call_tool("search_place", parameters)

class MapMCPService:
    """地图MCP服务层"""

    def __init__(self):
        self.baidu_client = BaiduMapMCPClient()
        self.amap_client = AmapMCPClient()

    async def execute_navigation(self, map_service: str, origin: str, destination: str, transport_mode: str) -> dict:
        """
        执行导航操作

        Args:
            map_service: 地图服务 (baidu_map 或 amap)
            origin: 起点地址
            destination: 终点地址
            transport_mode: 交通模式

        Returns:
            dict: 导航结果
        """
        try:
            # 转换交通模式
            mode_mapping = {
                "transit": {
                    "baidu_map": "transit",
                    "amap": "bus"
                },
                "driving": {
                    "baidu_map": "driving",
                    "amap": "car"
                },
                "walking": {
                    "baidu_map": "walking",
                    "amap": "walk"
                }
            }

            # 获取对应的交通模式
            mode = mode_mapping.get(transport_mode, {}).get(map_service, "transit")

            if map_service == "baidu_map":
                result = await self.baidu_client.open_navigation(origin, destination, mode)
            elif map_service == "amap":
                result = await self.amap_client.open_navigation(origin, destination, mode)
            else:
                raise ValueError(f"不支持的地图服务: {map_service}")

            return {
                "success": True,
                "map_service": map_service,
                "origin": origin,
                "destination": destination,
                "transport_mode": transport_mode,
                "result": result
            }

        except Exception as e:
            print(f"导航执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "map_service": map_service,
                "origin": origin,
                "destination": destination
            }

    async def validate_address_with_map(self, address: str, map_service: str = "baidu_map") -> dict:
        """使用地图服务验证地址"""
        try:
            if map_service == "baidu_map":
                result = await self.baidu_client.search_place(address)
            elif map_service == "amap":
                result = await self.amap_client.search_place(address)
            else:
                raise ValueError(f"不支持的地图服务: {map_service}")

            # 解析搜索结果
            if result and "pois" in result and len(result["pois"]) > 0:
                return {
                    "is_valid": True,
                    "standardized_address": result["pois"][0].get("name", address),
                    "confidence": 0.9
                }
            else:
                return {
                    "is_valid": False,
                    "standardized_address": address,
                    "confidence": 0.0
                }

        except Exception as e:
            return {
                "is_valid": False,
                "standardized_address": address,
                "confidence": 0.0,
                "error": str(e)
            }