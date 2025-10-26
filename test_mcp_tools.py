#!/usr/bin/env python3
"""
测试MCP服务可用的工具列表
"""
import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.mcp_client import BaiduMapMCPClient, AmapMCPClient
from config import Config

async def test_mcp_tools():
    """测试MCP工具列表"""
    print("=== 测试MCP服务工具列表 ===\n")

    # 测试百度地图MCP
    print("1. 百度地图MCP工具列表:")
    try:
        async with BaiduMapMCPClient() as client:
            tools = await client.list_available_tools()
            if tools:
                for tool in tools:
                    print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            else:
                print("   没有找到可用工具")
    except Exception as e:
        print(f"   错误: {e}")

    print("\n2. 高德地图MCP工具列表:")
    try:
        async with AmapMCPClient() as client:
            tools = await client.list_available_tools()
            if tools:
                for tool in tools:
                    print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            else:
                print("   没有找到可用工具")
    except Exception as e:
        print(f"   错误: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())