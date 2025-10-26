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
        发送MCP请求 - 使用标准HTTP POST而不是SSE

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

            print(f"发送MCP请求: {method}")
            print(f"请求参数: {params}")
            print(f"请求URL: {self.base_url}")

            async with self.session.post(
                self.base_url,
                json=mcp_request,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:

                print(f"MCP响应状态码: {response.status}")

                if response.status != 200:
                    # 尝试读取错误响应体
                    try:
                        error_text = await response.text()
                        print(f"MCP错误响应: {error_text}")
                    except:
                        pass

                    return {
                        "error": f"MCP服务返回错误状态码: {response.status}",
                        "status_code": response.status
                    }

                # 处理JSON响应
                try:
                    result_data = await response.json()
                    print(f"MCP响应: {result_data}")

                    if "error" in result_data:
                        return {
                            "error": f"MCP服务错误: {result_data['error']}",
                            "mcp_error": result_data["error"]
                        }

                    return result_data.get("result", {})

                except Exception as e:
                    print(f"解析MCP响应失败: {e}")
                    # 尝试读取原始文本
                    raw_text = await response.text()
                    print(f"原始响应: {raw_text}")
                    return {"error": f"无法解析MCP响应: {str(e)}"}

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

    async def list_available_tools(self) -> List[Dict[str, Any]]:
        """列出可用的百度地图MCP工具"""
        return await self.list_tools()

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

        # 构建网页版百度地图URL - 使用更直接的导航URL
        # 百度地图网页版直接导航URL格式 - 使用更直接的URL
        url_params = {
            "origin": origin,
            "destination": destination,
            "mode": transport_mode,
            "region": "全国",
            "output": "html",
            "src": "AI导航助手",
            "coord_type": "bd09ll"
        }

        query_string = urllib.parse.urlencode(url_params, encoding='utf-8')
        baidu_url = f"https://api.map.baidu.com/direction?{query_string}"

        # 同时提供备用URL格式
        # 使用百度地图网页版直接路径规划URL
        backup_url_params = {
            "origin": origin,
            "destination": destination,
            "mode": transport_mode
        }
        backup_query_string = urllib.parse.urlencode(backup_url_params, encoding='utf-8')
        backup_baidu_url = f"https://map.baidu.com/direction?{backup_query_string}"

        print(f"生成百度地图导航URL: {baidu_url}")
        print(f"备用百度地图URL: {backup_baidu_url}")

        # 首先尝试主要URL，如果失败则尝试备用URL
        result = await self._open_navigation_url(baidu_url, "baidu_map", origin, destination)
        if not result.get("success"):
            print("主要URL失败，尝试备用URL")
            result = await self._open_navigation_url(backup_baidu_url, "baidu_map", origin, destination)

        return result

    async def _open_navigation_url(self, url: str, map_service: str, origin: str, destination: str) -> Dict[str, Any]:
        """打开导航URL"""
        try:
            print(f"打开{map_service}导航: {url}")

            # 首先验证URL是否有效（长度检查）
            if len(url) > 2000:
                print(f"警告：URL过长 ({len(url)} 字符)，可能无法正常打开")

            # 尝试在浏览器中打开网页版地图
            # 使用webbrowser.open()自动打开默认浏览器
            success = webbrowser.open(url)

            if success:
                print(f"webbrowser.open() 返回成功")
                # 添加延迟以确保浏览器有时间启动
                import asyncio
                await asyncio.sleep(1)

                return {
                    "success": True,
                    "message": f"已在浏览器中打开{map_service}导航页面: {origin} -> {destination}",
                    "map_service": map_service,
                    "origin": origin,
                    "destination": destination,
                    "url": url,
                    "action": "browser_opened"
                }
            else:
                print(f"webbrowser.open() 返回失败，尝试备用方法")
                # 如果webbrowser.open失败，尝试使用备用方法
                import subprocess
                import platform

                system = platform.system()
                try:
                    if system == "Darwin":  # macOS
                        print("使用macOS备用方法: open")
                        subprocess.run(["open", url], check=True, timeout=10)
                        success = True
                    elif system == "Windows":
                        print("使用Windows备用方法: start")
                        subprocess.run(["start", url], shell=True, check=True, timeout=10)
                        success = True
                    elif system == "Linux":
                        print("使用Linux备用方法: xdg-open")
                        subprocess.run(["xdg-open", url], check=True, timeout=10)
                        success = True
                    else:
                        print(f"未知系统: {system}")
                        success = False
                except subprocess.TimeoutExpired:
                    print("备用方法超时")
                    success = False
                except Exception as e:
                    print(f"备用方法异常: {e}")
                    success = False

                if success:
                    print("备用方法成功")
                    # 添加延迟以确保浏览器有时间启动
                    await asyncio.sleep(1)
                    return {
                        "success": True,
                        "message": f"已在浏览器中打开{map_service}导航页面: {origin} -> {destination}",
                        "map_service": map_service,
                        "origin": origin,
                        "destination": destination,
                        "url": url,
                        "action": "browser_opened"
                    }
                else:
                    print("所有方法都失败")
                    return {
                        "success": False,
                        "message": f"无法自动打开{map_service}导航页面，请手动复制URL",
                        "map_service": map_service,
                        "origin": origin,
                        "destination": destination,
                        "url": url,
                        "action": "manual_required"
                    }

        except Exception as e:
            print(f"打开导航URL异常: {e}")
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

    async def list_available_tools(self) -> List[Dict[str, Any]]:
        """列出可用的高德地图MCP工具"""
        return await self.list_tools()

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
            # 首先尝试调用MCP服务 - 使用更通用的工具名称
            result = await self.call_tool("maps_navigation", {
                "origin": origin,
                "destination": destination,
                "mode": mode,
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
            "bus": "bus",  # 公交
            "car": "car",  # 驾车
            "walk": "walk"  # 步行
        }
        transport_mode = mode_mapping.get(mode, "bus")

        # 构建网页版高德地图URL - 使用简化的URL格式，让高德地图自动选择第一个匹配地点
        # 移除固定的行政区划代码，让系统自动选择最匹配的地点
        url_params = {
            "dateTime": "now",
            "from[name]": origin,
            "to[name]": destination,
            "policy": "0",  # 默认策略
            "type": transport_mode
        }

        query_string = urllib.parse.urlencode(url_params, encoding='utf-8', quote_via=urllib.parse.quote)
        amap_url = f"https://ditu.amap.com/dir?{query_string}"

        print(f"生成高德地图导航URL: {amap_url}")
        return await self._open_navigation_url(amap_url, "amap", origin, destination)

    async def _open_navigation_url(self, url: str, map_service: str, origin: str, destination: str) -> Dict[str, Any]:
        """打开导航URL"""
        try:
            print(f"打开{map_service}导航: {url}")

            # 首先验证URL是否有效（长度检查）
            if len(url) > 2000:
                print(f"警告：URL过长 ({len(url)} 字符)，可能无法正常打开")

            # 尝试在浏览器中打开网页版地图
            # 使用webbrowser.open()自动打开默认浏览器
            success = webbrowser.open(url)

            if success:
                print(f"webbrowser.open() 返回成功")
                # 添加延迟以确保浏览器有时间启动
                import asyncio
                await asyncio.sleep(1)

                return {
                    "success": True,
                    "message": f"已在浏览器中打开{map_service}导航页面: {origin} -> {destination}",
                    "map_service": map_service,
                    "origin": origin,
                    "destination": destination,
                    "url": url,
                    "action": "browser_opened"
                }
            else:
                print(f"webbrowser.open() 返回失败，尝试备用方法")
                # 如果webbrowser.open失败，尝试使用备用方法
                import subprocess
                import platform

                system = platform.system()
                try:
                    if system == "Darwin":  # macOS
                        print("使用macOS备用方法: open")
                        subprocess.run(["open", url], check=True, timeout=10)
                        success = True
                    elif system == "Windows":
                        print("使用Windows备用方法: start")
                        subprocess.run(["start", url], shell=True, check=True, timeout=10)
                        success = True
                    elif system == "Linux":
                        print("使用Linux备用方法: xdg-open")
                        subprocess.run(["xdg-open", url], check=True, timeout=10)
                        success = True
                    else:
                        print(f"未知系统: {system}")
                        success = False
                except subprocess.TimeoutExpired:
                    print("备用方法超时")
                    success = False
                except Exception as e:
                    print(f"备用方法异常: {e}")
                    success = False

                if success:
                    print("备用方法成功")
                    # 添加延迟以确保浏览器有时间启动
                    await asyncio.sleep(1)
                    return {
                        "success": True,
                        "message": f"已在浏览器中打开{map_service}导航页面: {origin} -> {destination}",
                        "map_service": map_service,
                        "origin": origin,
                        "destination": destination,
                        "url": url,
                        "action": "browser_opened"
                    }
                else:
                    print("所有方法都失败")
                    return {
                        "success": False,
                        "message": f"无法自动打开{map_service}导航页面，请手动复制URL",
                        "map_service": map_service,
                        "origin": origin,
                        "destination": destination,
                        "url": url,
                        "action": "manual_required"
                    }

        except Exception as e:
            print(f"打开导航URL异常: {e}")
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