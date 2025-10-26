# AI导航助手

基于MCP的智能导航系统，支持语音和文本输入，自动打开百度地图或高德地图进行导航。

## 功能特性

- 🎯 **智能意图识别**: 使用DeepSeek AI分析用户导航意图
- 🗺️ **多地图支持**: 支持百度地图和高德地图
- 📝 **文本输入**: 支持文本指令输入
- 📱 **Web界面**: 友好的用户交互界面
- 🔧 **MCP架构**: 基于Model Context Protocol实现
- ⚡ **实时响应**: 快速处理导航请求

## 系统架构

```
用户界面 (Web) → FastAPI服务 → DeepSeek AI → 地图MCP → 地图应用
```

### 核心组件

1. **用户交互层**: Web界面，支持文本和语音输入
2. **服务层**: FastAPI后端，处理业务逻辑
3. **AI服务层**: DeepSeek API，意图识别和地址标准化
4. **执行层**: 地图MCP客户端，调用地图服务

## 快速开始

### 环境要求

- Python 3.8+
- 麦克风（用于语音输入）
- 网络连接

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置API密钥

1. 复制 `.env.example` 为 `.env`
2. 配置以下API密钥：

```env
# DeepSeek API配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 百度地图MCP配置
BAIDU_MAP_AK=your_baidu_map_ak_here

# 高德地图MCP配置
AMAP_KEY=your_amap_key_here
```

### 获取API密钥

1. **DeepSeek API**: 访问 https://platform.deepseek.com/
2. **百度地图AK**: 访问 https://lbsyun.baidu.com/
3. **高德地图Key**: 访问 https://lbs.amap.com/

### 运行应用

```bash
python main.py
```

访问 http://127.0.0.1:8000 使用导航助手

## 使用示例

### 文本输入
- "从北京天安门到上海东方明珠"
- "帮我导航到最近的星巴克"
- "从公司到家，坐公交"

## API文档

### 导航请求
```http
POST /api/navigate
Content-Type: application/json

{
    "text": "从北京天安门到上海东方明珠"
}
```

### 系统状态
```http
GET /api/status
```


## 技术栈

- **后端**: FastAPI, Uvicorn
- **前端**: HTML, CSS, JavaScript
- **AI服务**: DeepSeek API
- **地图服务**: 百度地图MCP, 高德地图MCP
- **语音识别**: SpeechRecognition, PyAudio
- **配置管理**: python-dotenv

## 开发说明

### 项目结构
```
├── main.py              # 主应用入口
├── config.py            # 配置管理
├── requirements.txt     # 依赖列表
├── .env                 # 环境变量
├── services/            # 服务层
│   ├── deepseek_service.py
│   ├── map_mcp_service.py
│   ├── voice_service.py
│   └── navigation_service.py
├── templates/           # 前端模板
│   └── index.html
└── static/              # 静态资源
    └── style.css
```

### MCP配置参考

- **百度地图MCP**: https://lbs.baidu.com/faq/api?title=mcpserver/quickstart
- **高德地图MCP**: https://lbs.amap.com/api/mcp-server/gettingstarted
- **DeepSeek API**: https://api-docs.deepseek.com/zh-cn/

## 故障排除

### 常见问题

1. **语音识别失败**: 检查麦克风权限和网络连接
2. **API调用失败**: 验证API密钥配置
3. **地图无法打开**: 检查地图应用是否安装

### 日志查看
应用运行日志会显示在控制台，包含详细的处理过程。

## 许可证

MIT License