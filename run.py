#!/usr/bin/env python3
"""
AI角色扮演聊天室启动脚本
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import flask
        import openai
        print("✅ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_api_key():
    """检查API密钥"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  未设置OPENAI_API_KEY环境变量")
        print("请在设置中配置API密钥或设置环境变量")
        print("设置方法: export OPENAI_API_KEY='your-api-key-here'")
        return False
    else:
        print("✅ API密钥已配置")
        return True

def start_server():
    """启动服务器"""
    print("🚀 启动AI角色扮演聊天室...")
    print("📱 访问地址: http://localhost:5000")
    print("🛑 按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        # 启动Flask应用
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    print("🎭 AI角色扮演聊天室")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查API密钥（可选）
    check_api_key()
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
