#!/usr/bin/env python3
"""
NavPilot - 智能网页地图导航助手
基于 mcp_agent_client 的正确导入方式
"""

import asyncio
import webbrowser
import urllib.parse
import re
import sys
from typing import Dict, Any, List

# 正确导入 mcp_agent_client（注意：包名中的连字符在导入时要改为下划线）
try:
    from mcp_agent_client import MCPSession, MCPClient

    MCP_AVAILABLE = True
    print("✅ mcp_agent_client 导入成功")
except ImportError as e:
    print(f"❌ mcp_agent_client 导入失败: {e}")
    MCP_AVAILABLE = False
    print("💡 请确保已安装: pip install mcp-agent-client")


class NavPilot:
    """基于 mcp_agent_client 的导航助手"""

    def __init__(self):
        self.mcp_available = MCP_AVAILABLE
        self.setup_map_providers()

        if self.mcp_available:
            print("🚀 MCP 客户端已启用")
        else:
            print("⚠️  使用简化模式（无 MCP）")

    def setup_map_providers(self):
        """设置地图提供商配置"""
        self.map_providers = {
            "baidu": {
                "name": "百度地图",
                "base_url": "https://map.baidu.com/dir/",
                "params_template": {
                    "from": "{origin}",
                    "to": "{destination}",
                    "mode": "driving"
                }
            },
            "gaode": {
                "name": "高德地图",
                "base_url": "https://ditu.amap.com/dir/",
                "params_template": {
                    "from": "{origin}",
                    "to": "{destination}",
                    "type": "drive"
                }
            }
        }

    async def initialize_mcp_session(self):
        """初始化 MCP 会话"""
        if not self.mcp_available:
            return None

        try:
            print("🔄 初始化 MCP 会话...")
            # 创建 MCP 客户端 - 这里需要根据 mcp_agent_client 的实际 API 调整
            client = MCPClient(
                command="python",
                args=["-c", "print('MCP Server')"]  # 简化示例，实际需要真正的 MCP 服务器
            )
            session = await client.start_session()
            print("✅ MCP 会话初始化成功")
            return session
        except Exception as e:
            print(f"❌ MCP 会话初始化失败: {e}")
            return None

    async def navigate(self, user_input: str, map_provider: str = "baidu") -> Dict[str, Any]:
        """执行导航"""
        session = None
        try:
            # 解析输入
            locations = self.parse_input(user_input)
            origin, destination = locations["origin"], locations["destination"]

            print(f"📍 路线规划: 从 {origin} 到 {destination}")

            # 生成URL
            url = self.generate_url(origin, destination, map_provider)
            provider_name = self.map_providers[map_provider]["name"]
            print(f"🗺️  使用 {provider_name}")

            # 打开导航
            if self.mcp_available:
                session = await self.initialize_mcp_session()
                if session:
                    success = await self.open_with_mcp(session, url)
                else:
                    success = self.open_directly(url)
            else:
                success = self.open_directly(url)

            return {
                "success": success,
                "origin": origin,
                "destination": destination,
                "map_provider": map_provider,
                "provider_name": provider_name,
                "navigation_url": url,
                "message": f"✅ {provider_name}导航已启动：从 {origin} 到 {destination}" if success else "❌ 导航启动失败"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ 导航失败: {e}"
            }
        finally:
            if session:
                await session.close()
                print("🔒 MCP 会话已关闭")

    def parse_input(self, text: str) -> Dict[str, str]:
        """解析用户输入"""
        text = text.strip()

        patterns = [
            r"从\s*(.+?)\s*到\s*(.+)",
            r"(.+?)\s*到\s*(.+)",
            r"导航\s*从\s*(.+?)\s*到\s*(.+)",
            r"去\s*(.+?)\s*从\s*(.+)",
            r"从\s*(.+?)\s*去\s*(.+)",
            r"(.+?)\s*至\s*(.+)",
            r"从\s*(.+?)\s*至\s*(.+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return {
                    "origin": match.group(1).strip(),
                    "destination": match.group(2).strip()
                }

        # 如果模式匹配失败，尝试简单分割
        separators = ["到", "至", "->", "→"]
        for sep in separators:
            if sep in text:
                parts = text.split(sep, 1)
                if len(parts) == 2:
                    return {
                        "origin": parts[0].strip(),
                        "destination": parts[1].strip()
                    }

        # 如果只有两个词，假设第一个是起点，第二个是终点
        words = text.split()
        if len(words) == 2:
            return {
                "origin": words[0].strip(),
                "destination": words[1].strip()
            }

        raise ValueError(f"无法解析输入: '{text}'。请使用格式：'从A到B' 或 'A到B'")

    def generate_url(self, origin: str, destination: str, provider: str) -> str:
        """生成导航URL"""
        if provider not in self.map_providers:
            raise ValueError(f"不支持的地图提供商: {provider}")

        config = self.map_providers[provider]
        params = config["params_template"].copy()

        formatted_params = {}
        for key, template in params.items():
            formatted_params[key] = template.format(
                origin=urllib.parse.quote(origin),
                destination=urllib.parse.quote(destination)
            )

        query = urllib.parse.urlencode(formatted_params)
        return f"{config['base_url']}?{query}"

    def open_directly(self, url: str) -> bool:
        """直接打开浏览器"""
        try:
            print(f"🌐 正在打开浏览器...")
            success = webbrowser.open(url)
            if success:
                print(f"✅ 已成功打开导航页面")
            else:
                print(f"⚠️  浏览器打开状态未知")
            return success
        except Exception as e:
            print(f"❌ 打开浏览器失败: {e}")
            return False

    async def open_with_mcp(self, session, url: str) -> bool:
        """使用 MCP 打开浏览器"""
        try:
            print(f"🔗 通过 MCP 打开导航页面...")

            # 根据 mcp_agent_client 的实际 API 调用工具
            # 这里需要根据具体的 API 文档调整
            result = await session.call_tool(
                "open_browser",
                {"url": url}
            )

            print(f"✅ MCP 调用成功")
            return True

        except Exception as e:
            print(f"❌ MCP 调用失败: {e}")
            # 失败时回退到直接打开
            return self.open_directly(url)

    async def get_available_tools(self, session):
        """获取可用的 MCP 工具"""
        if not session:
            return []
        try:
            tools = await session.list_tools()
            return tools
        except Exception as e:
            print(f"获取工具列表失败: {e}")
            return []


# 测试函数
async def run_tests():
    """运行测试用例"""
    pilot = NavPilot()

    print("🧪 开始测试 NavPilot...")

    # 测试解析功能
    test_cases = [
        "从北京到上海",
        "北京到上海",
        "导航从天安门到故宫",
        "去上海从北京",
        "北京 上海",
        "北京至上海",
    ]

    print("\n📝 输入解析测试:")
    for test_case in test_cases:
        try:
            result = pilot.parse_input(test_case)
            print(f"  ✅ '{test_case}' -> 从 {result['origin']} 到 {result['destination']}")
        except Exception as e:
            print(f"  ❌ '{test_case}' -> 失败: {e}")

    # 测试URL生成
    print("\n🔗 URL生成测试:")
    url_test_cases = [
        ("北京", "上海", "baidu"),
        ("天安门", "故宫", "gaode"),
        ("杭州东站", "西湖", "baidu"),
    ]

    for origin, destination, provider in url_test_cases:
        try:
            url = pilot.generate_url(origin, destination, provider)
            provider_name = pilot.map_providers[provider]['name']
            print(f"  ✅ {provider_name}: {origin} → {destination}")
            print(f"     链接: {url}")
        except Exception as e:
            print(f"  ❌ {provider}: {origin} → {destination} -> 失败: {e}")


# 主程序
async def main():
    """NavPilot 主程序"""
    pilot = NavPilot()

    print("=" * 60)
    print("🚀 NavPilot 智能导航助手")
    print("=" * 60)
    print("💡 使用说明:")
    print("  格式: '从A到B' 或 'A到B' 或 'A B'")
    print("  地图: 百度地图(默认), 高德地图(g)")
    print("  示例:")
    print("    '从北京到上海'")
    print("    'g:上海到北京' (使用高德地图)")
    print("    'b:天安门到故宫' (使用百度地图)")
    print("    '北京 上海' (空格分隔)")
    print("  命令:")
    print("    'test' - 运行测试")
    print("    'help' - 显示帮助")
    print("    'quit' - 退出程序")
    print("-" * 60)

    while True:
        try:
            user_input = input("\n🎯 请输入导航指令: ").strip()

            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("👋 感谢使用 NavPilot，再见！")
                break

            if user_input.lower() in ['help', '帮助', '?']:
                print("\n📖 帮助信息:")
                print("  基本格式:")
                print("    '从起点到终点'")
                print("    '起点 到 终点'")
                print("    '起点 终点'")
                print("  地图选择:")
                print("    默认: 百度地图")
                print("    g:起点到终点 - 高德地图")
                print("    b:起点到终点 - 百度地图")
                continue

            if user_input.lower() == 'test':
                await run_tests()
                continue

            if not user_input:
                continue

            # 解析地图提供商
            map_provider = "baidu"  # 默认百度地图
            if user_input.startswith('g:'):
                map_provider = "gaode"
                user_input = user_input[2:]
            elif user_input.startswith('b:'):
                map_provider = "baidu"
                user_input = user_input[2:]

            # 执行导航
            print("🔄 处理导航请求...")
            result = await pilot.navigate(user_input, map_provider)

            # 显示结果
            print(f"\n{result['message']}")
            if result["success"]:
                print(f"🔗 导航链接: {result['navigation_url']}")

        except KeyboardInterrupt:
            print("\n🛑 程序被用户中断")
            break
        except Exception as e:
            print(f"❌ 系统错误: {e}")


if __name__ == "__main__":
    # 运行主程序
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        asyncio.run(run_tests())
    else:
        asyncio.run(main())