from services.deepseek_service import DeepSeekService
from services.map_mcp_service import MapMCPService

class NavigationService:
    """导航业务逻辑服务"""

    def __init__(self):
        self.deepseek_service = DeepSeekService()
        self.map_mcp_service = MapMCPService()

    async def process_navigation_request(self, user_input: str) -> dict:
        """
        处理导航请求

        Args:
            user_input: 用户输入的文本

        Returns:
            dict: 处理结果
        """
        print(f"处理导航请求: {user_input}")

        # 1. 使用DeepSeek分析意图
        print("正在分析导航意图...")
        intent_result = await self.deepseek_service.analyze_navigation_intent(user_input)

        if intent_result.get("error"):
            return {
                "success": False,
                "error": f"意图分析失败: {intent_result['error']}",
                "step": "intent_analysis"
            }

        # 检查是否成功提取起点和终点
        origin = intent_result.get("origin")
        destination = intent_result.get("destination")

        if not origin or not destination:
            return {
                "success": False,
                "error": "无法识别起点或终点地址",
                "intent_result": intent_result,
                "step": "address_extraction"
            }

        # 2. 验证地址有效性
        print(f"验证地址: 起点={origin}, 终点={destination}")
        origin_validation = await self.deepseek_service.validate_address(origin)
        destination_validation = await self.deepseek_service.validate_address(destination)

        if not origin_validation.get("is_valid", False):
            return {
                "success": False,
                "error": f"起点地址无效: {origin}",
                "step": "address_validation"
            }

        if not destination_validation.get("is_valid", False):
            return {
                "success": False,
                "error": f"终点地址无效: {destination}",
                "step": "address_validation"
            }

        # 使用标准化地址
        standardized_origin = origin_validation.get("standardized_address", origin)
        standardized_destination = destination_validation.get("standardized_address", destination)

        # 3. 执行导航
        print(f"执行导航: {standardized_origin} -> {standardized_destination}")
        map_service = intent_result.get("map_service", "baidu_map")
        transport_mode = intent_result.get("transport_mode", "transit")

        navigation_result = await self.map_mcp_service.execute_navigation(
            map_service=map_service,
            origin=standardized_origin,
            destination=standardized_destination,
            transport_mode=transport_mode
        )

        # 4. 返回完整结果
        result = {
            "success": navigation_result.get("success", False),
            "user_input": user_input,
            "intent_analysis": intent_result,
            "address_validation": {
                "origin": origin_validation,
                "destination": destination_validation
            },
            "navigation_execution": navigation_result,
            "summary": {
                "origin": standardized_origin,
                "destination": standardized_destination,
                "map_service": map_service,
                "transport_mode": transport_mode
            }
        }

        if not navigation_result.get("success", False):
            result["error"] = navigation_result.get("error", "导航执行失败")

        return result

    async def get_system_status(self) -> dict:
        """获取系统状态"""
        from config import Config

        try:
            # 验证配置
            Config.validate_config()

            # 测试DeepSeek连接
            test_result = await self.deepseek_service.analyze_navigation_intent("测试连接")
            deepseek_status = "正常" if not test_result.get("error") else "异常"

            return {
                "status": "正常",
                "services": {
                    "deepseek": deepseek_status,
                    "baidu_map": "配置完成",
                    "amap": "配置完成"
                },
                "config": {
                    "deepseek_api_key": "已配置" if Config.DEEPSEEK_API_KEY else "未配置",
                    "baidu_map_ak": "已配置" if Config.BAIDU_MAP_AK else "未配置",
                    "amap_key": "已配置" if Config.AMAP_KEY else "未配置"
                }
            }

        except Exception as e:
            return {
                "status": "异常",
                "error": str(e),
                "services": {
                    "deepseek": "异常",
                    "baidu_map": "异常",
                    "amap": "异常"
                }
            }