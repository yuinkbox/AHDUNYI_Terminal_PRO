#!/bin/bash
echo "🚀 启动 AHDUNYI 真实前端服务"
echo "========================================"
echo "📡 前端地址: http://localhost:5173"
echo "🔗 后端地址: http://127.0.0.1:8000"
echo "🔐 测试账号: admin / 123456"
echo "💡 请确保后端服务已启动！"
echo "========================================"

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
  echo "📦 安装前端依赖..."
  npm install
fi

# 启动开发服务器
echo "🖥️  启动开发服务器..."
npm run dev