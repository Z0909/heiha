"""
基于MCP协议的百度地图和高德地图客户端
遵循MCP (Model Context Protocol) 标准协议
使用SSE (Server-Sent Events) 协议
"""
import json
import aiohttp
import asyncio
import urllib.parse
import webbrowser
from typing import Dict, Any, List, Optional
from config import Config


class MCPClient:
    """MCP客户端基类 - 使用SSE协议"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _make_sse_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送SSE MCP请求

        Args:
            method: MCP方法名
            params: 请求参数

        Returns:
            MCP响应结果
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            # 构建MCP请求
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params
            }

            print(f"发送MCP SSE请求: {method}")
            print(f"请求参数: {params}")

            async with self.session.post(
                self.base_url,
                json=mcp_request,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:

                if response.status != 200:
                    return {
                        "error": f"MCP服务返回错误状态码: {response.status}",
                        "status_code": response.status
                    }

                # 处理SSE响应
                result_text = await response.text()
                print(f"MCP响应: {result_text}")

                # 解析SSE数据
                lines = result_text.strip().split('\n')
                for line in lines:
                    if line.startswith('data: '):
                        data = line[6:]  # 移除 'data: ' 前缀
                        if data:
                            try:
                                result = json.loads(data)
                                if "error" in result:
                                    return {
                                        "error": f"MCP服务错误: {result['error']}",
                                        "mcp_error": result["error"]
                                    }
                                return result.get("result", {})
                            except json.JSONDecodeError:
                                continue

                return {"error": "无法解析MCP响应"}

        except asyncio.TimeoutError:
            return {"error": "MCP请求超时"}
        except aiohttp.ClientError as e:
            return {"error": f"MCP连接错误: {str(e)}"}
        except Exception as e:
            print(f"MCP请求异常: {e}")
            return {"error": str(e)}

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        列出可用的MCP工具

        Returns:
            工具列表
        """
        try:
            result = await self._make_sse_request("tools/list", {})
            return result.get("tools", [])
        except Exception as e:
            print(f"获取工具列表失败: {e}")
            return []

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用MCP工具

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果
        """
        return await self._make_sse_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })


class BaiduMapMCPClient(MCPClient):
    """百度地图MCP客户端"""

    def __init__(self):
        super().__init__(Config.BAIDU_MCP_URL, Config.BAIDU_MAP_AK)

    async def open_navigation(self, origin: str, destination: str, mode: str = "transit") -> Dict[str, Any]:
        """
        打开百度地图导航

        Args:
            origin: 起点地址
            destination: 终点地址
            mode: 交通模式 (transit/driving/walking)

        Returns:
            导航结果
        """
        try:
            # 首先尝试调用MCP服务
            result = await self.call_tool("maps_navigation", {
                "origin": origin,
                "destination": destination,
                "mode": mode,
                "coord_type": "bd09ll"
            })

            # 如果MCP服务失败，使用本地生成的URL作为回退
            if "error" in result:
                print(f"MCP服务失败，使用本地URL回退: {result['error']}")
                return await self._generate_local_navigation_url(origin, destination, mode)

            # 处理MCP响应
            if result.get("success"):
                # 从MCP响应中提取导航URL
                navigation_url = result.get("url") or result.get("navigation_url")
                if navigation_url:
                    return await self._open_navigation_url(navigation_url, "baidu_map", origin, destination)

            # 如果MCP响应中没有URL，使用本地生成的URL
            return await self._generate_local_navigation_url(origin, destination, mode)

        except Exception as e:
            return {
                "success": False,
                "error": f"百度地图导航失败: {e}",
                "map_service": "baidu_map",
                "origin": origin,
                "destination": destination
            }

    async def _generate_local_navigation_url(self, origin: str, destination: str, mode: str) -> Dict[str, Any]:
        """生成本地百度地图导航URL"""
        # 转换交通模式
        mode_mapping = {
            "transit": "transit",  # 公交
            "driving": "driving",  # 驾车
            "walking": "walking"  # 步行
        }
        transport_mode = mode_mapping.get(mode, "transit")

        # 构建URL
        url_params = {
            "origin": origin,
            "destination": destination,
            "mode": transport_mode,
            "src": "AI导航助手"
        }

        query_string = urllib.parse.urlencode(url_params)
        baidu_url = f"baidumap://map/direction?{query_string}"

        return await self._open_navigation_url(baidu_url, "baidu_map", origin, destination)

    async def _open_navigation_url(self, url: str, map_service: str, origin: str, destination: str) -> Dict[str, Any]:
        """打开导航URL"""
        try:
            print(f"打开{map_service}导航: {url}")

            # 尝试自动打开地图应用
            success = webbrowser.open(url)

            if success:
                return {
                    "success": True,
                    "message": f"已打开{map_service}导航: {origin} -> {destination}",
                    "map_service": map_service,
                    "origin": origin,
                    "destination": destination,
                    "url": url,
                    "action": "app_opened"
                }
            else:
                return {
                    "success": False,
                    "message": f"无法自动打开{map_service}，请手动复制URL",
                    "map_service": map_service,
                    "origin": origin,
                    "destination": destination,
                    "url": url,
                    "action": "manual_required"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"打开{map_service}导航失败: {e}",
                "map_service": map_service,
                "origin": origin,
                "destination": destination,
                "url": url
            }


class AmapMCPClient(MCPClient):
    """高德地图MCP客户端"""

    def __init__(self):
        super().__init__(Config.AMAP_MCP_URL, Config.AMAP_KEY)

    async def open_navigation(self, origin: str, destination: str, mode: str = "bus") -> Dict[str, Any]:
        """
        打开高德地图导航

        Args:
            origin: 起点地址
            destination: 终点地址
            mode: 交通模式 (bus/car/walk)

        Returns:
            导航结果
        """
        try:
            # 首先尝试调用MCP服务
            result = await self.call_tool("maps_direction_transit_integrated", {
                "origin": origin,
                "destination": destination,
                "strategy": mode,
                "city": ""
            })

            # 如果MCP服务失败，使用本地生成的URL作为回退
            if "error" in result:
                print(f"MCP服务失败，使用本地URL回退: {result['error']}")
                return await self._generate_local_navigation_url(origin, destination, mode)

            # 处理MCP响应
            if result.get("success"):
                # 从MCP响应中提取导航URL
                navigation_url = result.get("url") or result.get("navigation_url")
                if navigation_url:
                    return await self._open_navigation_url(navigation_url, "amap", origin, destination)

            # 如果MCP响应中没有URL，使用本地生成的URL
            return await self._generate_local_navigation_url(origin, destination, mode)

        except Exception as e:
            return {
                "success": False,
                "error": f"高德地图导航失败: {e}",
                "map_service": "amap",
                "origin": origin,
                "destination": destination
            }

    async def _generate_local_navigation_url(self, origin: str, destination: str, mode: str) -> Dict[str, Any]:
        """生成本地高德地图导航URL"""
        # 转换交通模式
        mode_mapping = {
            "bus": "1",  # 公交
            "car": "0",  # 驾车
            "walk": "2"  # 步行
        }
        transport_mode = mode_mapping.get(mode, "1")

        # 构建URL
        url_params = {
            "from": origin,
            "to": destination,
            "mode": transport_mode,
            "src": "AI导航助手"
        }

        query_string = urllib.parse.urlencode(url_params)
        amap_url = f"amapuri://route/plan/?{query_string}"

        return await self._open_navigation_url(amap_url, "amap", origin, destination)

    async def _open_navigation_url(self, url: str, map_service: str, origin: str, destination: str) -> Dict[str, Any]:
        """打开导航URL"""
        try:
            print(f"打开{map_service}导航: {url}")

            # 尝试自动打开地图应用
            success = webbrowser.open(url)

            if success:
                return {
                    "success": True,
                    "message": f"已打开{map_service}导航: {origin} -> {destination}",
                    "map_service": map_service,
                    "origin": origin,
                    "destination": destination,
                    "url": url,
                    "action": "app_opened"
                }
            else:
                return {
                    "success": False,
                    "message": f"无法自动打开{map_service}，请手动复制URL",
                    "map_service": map_service,
                    "origin": origin,
                    "destination": destination,
                    "url": url,
                    "action": "manual_required"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"打开{map_service}导航失败: {e}",
                "map_service": map_service,
                "origin": origin,
                "destination": destination,
                "url": url
            }


class MapMCPService:
    """地图MCP服务层"""

    def __init__(self):
        self.baidu_client = BaiduMapMCPClient()
        self.amap_client = AmapMCPClient()

    async def execute_navigation(self, map_service: str, origin: str, destination: str, transport_mode: str = "transit") -> Dict[str, Any]:
        """
        执行导航操作

        Args:
            map_service: 地图服务 (baidu_map 或 amap)
            origin: 起点地址
            destination: 终点地址
            transport_mode: 交通模式

        Returns:
            导航结果
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
                async with self.baidu_client as client:
                    result = await client.open_navigation(origin, destination, mode)
            elif map_service == "amap":
                async with self.amap_client as client:
                    result = await client.open_navigation(origin, destination, mode)
            else:
                raise ValueError(f"不支持的地图服务: {map_service}")

            return result

        except Exception as e:
            print(f"导航执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "map_service": map_service,
                "origin": origin,
                "destination": destination
            }