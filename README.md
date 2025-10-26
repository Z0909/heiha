# AI导航助手

基于MCP的智能导航系统，支持文本输入，自动在浏览器中打开百度地图或高德地图网页版进行导航。

## 功能特性

- 🎯 **智能意图识别**: 使用DeepSeek AI分析用户导航意图
- 🗺️ **多地图支持**: 支持百度地图和高德地图网页版
- 🌐 **网页版地图**: 在浏览器中直接打开地图导航页面
- 📝 **文本输入**: 支持自然语言文本指令输入
- 📱 **Web界面**: 友好的用户交互界面
- 🔧 **MCP架构**: 基于Model Context Protocol实现
- ⚡ **实时响应**: 快速处理导航请求
- 🔄 **自动打开**: 自动在浏览器中打开导航页面
- 🎯 **智能地点选择**: 自动选择第一个匹配地点，避免多地点选择困扰

## 系统架构

```
用户界面 (Web) → FastAPI服务 → DeepSeek AI → 地图MCP → 网页版地图
```

### 核心组件

1. **用户交互层**: Web界面，支持文本输入
2. **服务层**: FastAPI后端，处理业务逻辑
3. **AI服务层**: DeepSeek API，意图识别和地址标准化
4. **执行层**: 地图MCP客户端，生成网页版地图URL
5. **浏览器层**: 自动在浏览器中打开网页版地图导航页面

## 快速开始

### 环境要求

- Python 3.8+
- 现代Web浏览器（Chrome、Firefox、Safari等）
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
- "用高德地图从北京西站到首都机场"
- "百度地图导航到天安门广场"

### 操作流程
1. 在输入框中输入导航指令
2. 点击"开始导航"按钮
3. 系统自动在浏览器中打开地图导航页面
4. 在地图页面中确认导航路线

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
- **地图服务**: 百度地图网页版API, 高德地图网页版API
- **MCP客户端**: SSE协议实现
- **浏览器自动化**: webbrowser模块
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
│   ├── mcp_client.py
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

1. **DeepSeek API超时**: 检查网络连接和API密钥配置
2. **地图URL生成失败**: 验证地图服务API密钥配置
3. **浏览器无法自动打开**: 检查默认浏览器设置
4. **网页版地图加载失败**: 检查网络连接和地图服务状态

### 日志查看
应用运行日志会显示在控制台，包含详细的处理过程。

## 工作原理

1. **意图分析**: 使用DeepSeek AI分析用户输入的导航意图
2. **地址标准化**: 将模糊地址转换为标准格式
3. **URL生成**: 生成百度地图或高德地图的网页版导航URL
4. **自动打开**: 在默认浏览器中打开网页版地图导航页面
5. **用户确认**: 用户在地图页面中确认导航路线

## 许可证

MIT License