#!/bin/bash

# AI导航助手 - 启动脚本

echo "🤖 AI导航助手启动中..."

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📚 安装依赖包..."
pip install -r requirements.txt

# 运行应用
echo "🚀 启动AI导航助手..."
python run.py

# 如果run.py不存在，直接启动main.py
if [ $? -ne 0 ]; then
    echo "⚠️ 使用备用启动方式..."
    python main.py
fi