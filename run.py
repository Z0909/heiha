#!/usr/bin/env python3
"""
AI导航助手 - 运行脚本

这个脚本提供了完整的运行和验证功能
"""

import os
import sys
import asyncio
import requests
from config import Config

async def check_dependencies():
    """检查依赖是否安装"""
    print("🔍 检查依赖包...")

    required_packages = [
        'fastapi', 'uvicorn', 'python-dotenv', 'requests',
        'speechrecognition', 'pyaudio', 'websockets', 'jinja2'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False

    print("✅ 所有依赖包已安装")
    return True

def check_config():
    """检查配置是否完整"""
    print("\n🔍 检查配置文件...")

    try:
        Config.validate_config()
        print("✅ 配置文件验证通过")
        return True
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("请编辑 .env 文件，配置以下API密钥:")
        print("- DEEPSEEK_API_KEY: DeepSeek API密钥")
        print("- BAIDU_MAP_AK: 百度地图AK")
        print("- AMAP_KEY: 高德地图Key")
        return False

async def test_services():
    """测试各服务连接"""
    print("\n🔍 测试服务连接...")

    # 测试DeepSeek连接
    print("测试DeepSeek API连接...")
    try:
        from services.deepseek_service import DeepSeekService
        service = DeepSeekService()
        test_result = await service.analyze_navigation_intent("测试连接")
        if test_result.get("error"):
            print(f"❌ DeepSeek连接失败: {test_result['error']}")
            return False
        else:
            print("✅ DeepSeek连接正常")
    except Exception as e:
        print(f"❌ DeepSeek连接异常: {e}")
        return False

    # 测试地图MCP连接
    print("测试地图MCP连接...")
    try:
        from services.map_mcp_service import MapMCPService
        service = MapMCPService()

        # 测试百度地图
        try:
            await service.baidu_client.search_place("测试")
            print("✅ 百度地图MCP连接正常")
        except Exception as e:
            print(f"⚠️ 百度地图MCP连接异常: {e}")

        # 测试高德地图
        try:
            await service.amap_client.search_place("测试")
            print("✅ 高德地图MCP连接正常")
        except Exception as e:
            print(f"⚠️ 高德地图MCP连接异常: {e}")

    except Exception as e:
        print(f"❌ 地图MCP连接异常: {e}")
        return False

    return True

def start_application():
    """启动应用程序"""
    print("\n🚀 启动AI导航助手...")
    print(f"访问地址: http://{Config.APP_HOST}:{Config.APP_PORT}")
    print("按 Ctrl+C 停止服务")

    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host=Config.APP_HOST,
            port=Config.APP_PORT,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

async def run_test_navigation():
    """运行测试导航"""
    print("\n🧪 运行测试导航...")

    from services.navigation_service import NavigationService
    service = NavigationService()

    test_cases = [
        "从北京天安门到上海东方明珠",
        "帮我导航到最近的星巴克",
        "从公司到家，坐公交"
    ]

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_input}")
        try:
            result = await service.process_navigation_request(test_input)
            if result.get("success"):
                print("✅ 测试成功")
                summary = result.get("summary", {})
                print(f"   起点: {summary.get('origin')}")
                print(f"   终点: {summary.get('destination')}")
                print(f"   地图: {summary.get('map_service')}")
            else:
                print(f"❌ 测试失败: {result.get('error')}")
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def show_help():
    """显示帮助信息"""
    print("""
AI导航助手 - 使用说明

命令:
  python run.py             启动完整服务
  python run.py --test      运行测试
  python run.py --check     检查环境和配置
  python run.py --help      显示此帮助

功能:
  • 智能导航: 基于AI的意图识别和地址标准化
  • 多地图支持: 百度地图和高德地图
  • 语音输入: 支持语音指令
  • Web界面: 友好的用户交互界面

配置说明:
  1. 编辑 .env 文件配置API密钥
  2. 确保已安装 requirements.txt 中的依赖
  3. 需要网络连接和麦克风(语音功能)

API密钥获取:
  • DeepSeek: https://platform.deepseek.com/
  • 百度地图: https://lbsyun.baidu.com/
  • 高德地图: https://lbs.amap.com/
""")

async def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            await run_test_navigation()
        elif sys.argv[1] == "--check":
            await check_dependencies()
            check_config()
            await test_services()
        elif sys.argv[1] == "--help":
            show_help()
        else:
            print("❌ 未知参数，使用 --help 查看帮助")
        return

    # 完整启动流程
    print("=" * 50)
    print("🤖 AI导航助手 - 启动检查")
    print("=" * 50)

    # 检查依赖
    if not await check_dependencies():
        return

    # 检查配置
    if not check_config():
        return

    # 测试服务
    if not await test_services():
        print("\n⚠️ 部分服务连接异常，但应用仍可启动")

    # 启动应用
    start_application()

if __name__ == "__main__":
    asyncio.run(main())