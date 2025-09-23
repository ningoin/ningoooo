#!/usr/bin/env python3
"""
依赖安装脚本
自动安装项目所需的Python包
"""

import subprocess
import sys
import os

def install_package(package):
    """安装Python包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} 安装失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始安装项目依赖...")
    print("=" * 50)
    
    # 读取requirements.txt
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    else:
        # 如果没有requirements.txt，手动指定包
        packages = [
            "Flask==2.3.3",
            "Flask-CORS==4.0.0", 
            "requests==2.31.0",
            "python-dotenv==1.0.0",
            "Werkzeug==2.3.7",
            "pymongo==4.6.0"
        ]
    
    success_count = 0
    total_count = len(packages)
    
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print("=" * 50)
    print(f"📊 安装完成: {success_count}/{total_count} 个包安装成功")
    
    if success_count == total_count:
        print("🎉 所有依赖安装成功！")
        print("\n📋 接下来请确保:")
        print("1. 安装并启动MongoDB服务")
        print("2. 检查config.env配置文件")
        print("3. 运行 python app.py 启动服务")
    else:
        print("⚠️  部分依赖安装失败，请手动安装失败的包")
        print("可以使用: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
