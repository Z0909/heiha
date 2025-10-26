import json
import requests
import urllib.parse
import webbrowser
from config import Config

class MapMCPClient:
    """地图MCP客户端基类"""

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def call_tool(self, tool_name: str, parameters: dict) -> dict:
        """调用MCP工具"""
        try:
            # 对于地图导航，通常是通过URL scheme打开本地地图应用
            # 而不是通过HTTP API调用

            if tool_name == "open_navigation":
                # 构建地图导航URL
                origin = parameters.get("origin", "")
                destination = parameters.get("destination", "")
                mode = parameters.get("mode", "transit")

                # 调用具体的导航实现
                return await self._open_navigation(origin, destination, mode)
            elif tool_name == "search_place":
                # 搜索地点
                query = parameters.get("query") or parameters.get("keywords", "")
                return await self._search_place(query)
            else:
                raise Exception(f"不支持的MCP工具: {tool_name}")

        except Exception as e:
            print(f"MCP调用异常: {e}")
            raise

    async def _open_navigation(self, origin: str, destination: str, mode: str) -> dict:
        """打开导航 - 由子类实现"""
        raise NotImplementedError("子类必须实现此方法")

    async def _search_place(self, query: str) -> dict:
        """搜索地点 - 由子类实现"""
        raise NotImplementedError("子类必须实现此方法")

class BaiduMapMCPClient(MapMCPClient):
    """百度地图MCP客户端"""

    def __init__(self):
        super().__init__(Config.BAIDU_MCP_URL)

    async def open_navigation(self, origin: str, destination: str, mode: str) -> dict:
        """打开导航 - 公共方法"""
        return await self._open_navigation(origin, destination, mode)

    async def search_place(self, query: str) -> dict:
        """搜索地点 - 公共方法"""
        return await self._search_place(query)

    async def _open_navigation(self, origin: str, destination: str, mode: str) -> dict:
        """打开百度地图导航"""
        try:
            # 百度地图URL scheme
            # baidumap://map/direction?origin=起点&destination=终点&mode=交通方式

            # 转换交通模式
            mode_mapping = {
                "driving": "driving",
                "transit": "transit",
                "walking": "walking",
                "riding": "riding"
            }

            baidu_mode = mode_mapping.get(mode, "transit")

            # 构建URL
            url_params = {
                "origin": origin,
                "destination": destination,
                "mode": baidu_mode,
                "src": "AI导航助手"
            }

            query_string = urllib.parse.urlencode(url_params)
            baidu_url = f"baidumap://map/direction?{query_string}"

            print(f"打开百度地图导航: {baidu_url}")

            # 尝试打开百度地图应用
            try:
                webbrowser.open(baidu_url)
                return {
                    "success": True,
                    "message": f"已打开百度地图导航: {origin} -> {destination}",
                    "url": baidu_url
                }
            except Exception as e:
                # 如果无法直接打开，返回URL让用户手动打开
                return {
                    "success": False,
                    "message": f"无法自动打开百度地图，请手动复制URL: {baidu_url}",
                    "url": baidu_url,
                    "error": str(e)
                }

        except Exception as e:
            raise Exception(f"百度地图导航失败: {e}")

    async def _search_place(self, query: str) -> dict:
        """搜索百度地图地点"""
        try:
            # 百度地图搜索URL
            url_params = {
                "query": query,
                "src": "AI导航助手"
            }

            query_string = urllib.parse.urlencode(url_params)
            baidu_url = f"baidumap://map/search?{query_string}"

            print(f"百度地图搜索: {baidu_url}")

            return {
                "success": True,
                "message": f"已打开百度地图搜索: {query}",
                "url": baidu_url
            }

        except Exception as e:
            raise Exception(f"百度地图搜索失败: {e}")

class AmapMCPClient(MapMCPClient):
    """高德地图MCP客户端"""

    def __init__(self):
        super().__init__(Config.AMAP_MCP_URL)

    async def open_navigation(self, origin: str, destination: str, mode: str) -> dict:
        """打开导航 - 公共方法"""
        return await self._open_navigation(origin, destination, mode)

    async def search_place(self, query: str) -> dict:
        """搜索地点 - 公共方法"""
        return await self._search_place(query)

    async def _open_navigation(self, origin: str, destination: str, mode: str) -> dict:
        """打开高德地图导航"""
        try:
            # 高德地图URL scheme
            # amapuri://route/plan/?from=起点&to=终点&mode=交通方式

            # 转换交通模式
            mode_mapping = {
                "driving": "0",  # 驾车
                "transit": "1",  # 公交
                "bus": "1",      # 公交
                "walking": "2",  # 步行
                "walk": "2",     # 步行
                "ride": "3"      # 骑行
            }

            amap_mode = mode_mapping.get(mode, "1")  # 默认公交

            # 构建URL
            url_params = {
                "from": origin,
                "to": destination,
                "mode": amap_mode,
                "src": "AI导航助手"
            }

            query_string = urllib.parse.urlencode(url_params)
            amap_url = f"amapuri://route/plan/?{query_string}"

            print(f"打开高德地图导航: {amap_url}")

            # 尝试打开高德地图应用
            try:
                webbrowser.open(amap_url)
                return {
                    "success": True,
                    "message": f"已打开高德地图导航: {origin} -> {destination}",
                    "url": amap_url
                }
            except Exception as e:
                # 如果无法直接打开，返回URL让用户手动打开
                return {
                    "success": False,
                    "message": f"无法自动打开高德地图，请手动复制URL: {amap_url}",
                    "url": amap_url,
                    "error": str(e)
                }

        except Exception as e:
            raise Exception(f"高德地图导航失败: {e}")

    async def _search_place(self, query: str) -> dict:
        """搜索高德地图地点"""
        try:
            # 高德地图搜索URL
            url_params = {
                "keywords": query,
                "src": "AI导航助手"
            }

            query_string = urllib.parse.urlencode(url_params)
            amap_url = f"amapuri://poi?{query_string}"

            print(f"高德地图搜索: {amap_url}")

            return {
                "success": True,
                "message": f"已打开高德地图搜索: {query}",
                "url": amap_url
            }

        except Exception as e:
            raise Exception(f"高德地图搜索失败: {e}")

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