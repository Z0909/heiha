# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an AI导航助手 (AI Navigation Assistant) project built with Python and FastAPI. The system uses DeepSeek AI for intent recognition and integrates with Baidu Map and Amap MCP services for navigation.

## Project Structure

```
├── main.py                 # FastAPI主应用
├── config.py              # 配置管理
├── run.py                 # 运行和测试脚本
├── start.sh               # 启动脚本
├── requirements.txt       # Python依赖
├── .env                   # 环境变量配置
├── services/              # 服务层
│   ├── deepseek_service.py    # DeepSeek AI服务
│   ├── map_mcp_service.py     # 地图MCP服务
│   └── navigation_service.py  # 导航业务逻辑
├── templates/             # 前端模板
│   └── index.html        # Web界面
└── static/               # 静态资源
    └── style.css         # 样式文件
```

## Development Setup

### Dependencies
Install required packages:
```bash
pip install -r requirements.txt
```

### Configuration
Configure API keys in `.env` file:
- `DEEPSEEK_API_KEY`: DeepSeek API key
- `BAIDU_MAP_AK`: Baidu Map AK
- `AMAP_KEY`: Amap API key

### Running the Application
```bash
# Using the run script
python run.py

# Using the shell script
./start.sh

# Direct execution
python main.py
```

## Key Features

- **AI Intent Recognition**: Uses DeepSeek AI to analyze navigation requests
- **Multi-Map Support**: Integrates with Baidu Map and Amap MCP services
- **Text Input**: Web interface for text-based navigation requests
- **MCP Architecture**: Built on Model Context Protocol

## API Endpoints

- `POST /api/navigate`: Process navigation requests
- `GET /api/status`: Check system status
- `GET /`: Web interface

## Testing

Run tests with:
```bash
python run.py --test      # Run functional tests
python run.py --check     # Check environment and config
```

## Git Status

- **Current Branch**: `testbranch`
- **Status**: Active development with complete navigation system