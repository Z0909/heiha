from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
import uvicorn
import json
import asyncio

from config import Config
from services.navigation_service import NavigationService

# 创建FastAPI应用
app = FastAPI(title="AI导航助手", description="基于MCP的智能导航系统")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 模板引擎
templates = Jinja2Templates(directory="templates")

# 服务实例
navigation_service = NavigationService()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """主页面"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/navigate")
async def navigate(request_data: dict):
    """处理导航请求"""
    try:
        user_input = request_data.get("text", "")
        if not user_input:
            return {"success": False, "error": "请输入导航指令"}

        result = await navigation_service.process_navigation_request(user_input)
        return result

    except Exception as e:
        return {"success": False, "error": f"处理请求时发生错误: {str(e)}"}

@app.get("/api/status")
async def get_status():
    """获取系统状态"""
    try:
        status = await navigation_service.get_system_status()
        return status
    except Exception as e:
        return {"status": "异常", "error": str(e)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接，用于实时通信"""
    await websocket.accept()

    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "navigate":
                # 处理导航请求
                result = await navigation_service.process_navigation_request(message["text"])
                await websocket.send_text(json.dumps({
                    "type": "navigation_result",
                    "data": result
                }))

            elif message["type"] == "status":
                # 获取状态
                status = await navigation_service.get_system_status()
                await websocket.send_text(json.dumps({
                    "type": "status_result",
                    "data": status
                }))

    except WebSocketDisconnect:
        print("WebSocket连接断开")
    except Exception as e:
        print(f"WebSocket错误: {e}")

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print("AI导航助手启动中...")

    try:
        # 验证配置
        Config.validate_config()
        print("配置验证通过")

        # 测试服务状态
        status = await navigation_service.get_system_status()
        print(f"系统状态: {status['status']}")

    except Exception as e:
        print(f"启动失败: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    print("AI导航助手正在关闭...")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=Config.APP_HOST,
        port=Config.APP_PORT,
        reload=True
    )