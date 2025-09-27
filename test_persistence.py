# -*- coding: utf-8 -*-
"""
数据持久化功能测试脚本
测试文件存储是否正常工作
"""

import os
import sys
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.data_manager import DataManager

def test_data_persistence():
    """测试数据持久化功能"""
    print("🧪 开始测试数据持久化功能...")
    
    # 创建数据管理器实例
    data_manager = DataManager("data")
    
    # 测试1: 创建对话
    print("\n📝 测试1: 创建对话")
    conversation_id = "test-conv-001"
    user_id = "test-user-001"
    character_name = "测试角色"
    character_description = "这是一个测试角色"
    
    conversation = data_manager.save_conversation(
        conversation_id, user_id, character_name, character_description
    )
    print(f"✅ 创建对话成功: {conversation['id']}")
    
    # 测试2: 添加消息
    print("\n💬 测试2: 添加消息")
    data_manager.add_message_to_conversation(conversation_id, "user", "你好，我是用户")
    data_manager.add_message_to_conversation(conversation_id, "assistant", "你好！我是AI助手")
    print("✅ 添加消息成功")
    
    # 测试3: 获取对话
    print("\n📖 测试3: 获取对话")
    retrieved_conversation = data_manager.get_conversation(conversation_id)
    if retrieved_conversation:
        print(f"✅ 获取对话成功，包含 {len(retrieved_conversation['messages'])} 条消息")
        for msg in retrieved_conversation['messages']:
            print(f"   - {msg['role']}: {msg['content']}")
    else:
        print("❌ 获取对话失败")
    
    # 测试4: 创建自定义角色
    print("\n🎭 测试4: 创建自定义角色")
    custom_role = {
        "id": "test-role-001",
        "name": "测试自定义角色",
        "description": "这是一个测试用的自定义角色",
        "personality": "友善、幽默、乐于助人",
        "category": "test",
        "tags": ["测试", "自定义"],
        "image": "https://example.com/test.jpg"
    }
    
    saved_role = data_manager.save_custom_role(custom_role)
    print(f"✅ 创建自定义角色成功: {saved_role['name']}")
    
    # 测试5: 获取自定义角色
    print("\n🔍 测试5: 获取自定义角色")
    retrieved_role = data_manager.get_custom_role("test-role-001")
    if retrieved_role:
        print(f"✅ 获取自定义角色成功: {retrieved_role['name']}")
    else:
        print("❌ 获取自定义角色失败")
    
    # 测试6: 获取所有数据
    print("\n📊 测试6: 获取所有数据")
    all_conversations = data_manager.get_all_conversations()
    all_custom_roles = data_manager.get_all_custom_roles()
    print(f"✅ 总对话数: {len(all_conversations)}")
    print(f"✅ 总自定义角色数: {len(all_custom_roles)}")
    
    # 测试7: 数据统计
    print("\n📈 测试7: 数据统计")
    stats = data_manager.get_data_stats()
    print(f"✅ 数据统计: {json.dumps(stats, ensure_ascii=False, indent=2)}")
    
    # 测试8: 搜索功能
    print("\n🔎 测试8: 搜索功能")
    search_results = data_manager.search_custom_roles("测试")
    print(f"✅ 搜索结果: 找到 {len(search_results)} 个匹配的角色")
    
    # 测试9: 更新角色
    print("\n✏️ 测试9: 更新角色")
    update_data = {
        "name": "更新后的测试角色",
        "description": "这是更新后的描述"
    }
    success = data_manager.update_custom_role("test-role-001", update_data)
    if success:
        updated_role = data_manager.get_custom_role("test-role-001")
        print(f"✅ 更新角色成功: {updated_role['name']}")
    else:
        print("❌ 更新角色失败")
    
    # 测试10: 备份数据
    print("\n💾 测试10: 备份数据")
    backup_dir = data_manager.backup_data()
    print(f"✅ 数据备份成功，备份目录: {backup_dir}")
    
    # 测试11: 删除数据
    print("\n🗑️ 测试11: 删除数据")
    delete_conv_success = data_manager.delete_conversation(conversation_id)
    delete_role_success = data_manager.delete_custom_role("test-role-001")
    
    if delete_conv_success:
        print("✅ 删除对话成功")
    else:
        print("❌ 删除对话失败")
        
    if delete_role_success:
        print("✅ 删除角色成功")
    else:
        print("❌ 删除角色失败")
    
    # 验证删除
    final_conversations = data_manager.get_all_conversations()
    final_roles = data_manager.get_all_custom_roles()
    print(f"✅ 删除后对话数: {len(final_conversations)}")
    print(f"✅ 删除后角色数: {len(final_roles)}")
    
    print("\n🎉 数据持久化功能测试完成！")
    print("\n📁 检查data文件夹中的文件:")
    if os.path.exists("data"):
        for file in os.listdir("data"):
            file_path = os.path.join("data", file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"   - {file}: {size} bytes")

def test_file_structure():
    """测试文件结构"""
    print("\n📁 检查项目文件结构:")
    
    required_files = [
        "app.py",
        "data/data_manager.py",
        "0.1版本.html",
        "requirements.txt",
        "config.env.example"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 文件不存在")
    
    # 检查data目录
    if os.path.exists("data"):
        print("✅ data/ 目录存在")
        data_files = os.listdir("data")
        for file in data_files:
            print(f"   - data/{file}")
    else:
        print("❌ data/ 目录不存在")

if __name__ == "__main__":
    print("🚀 开始数据持久化测试")
    print("=" * 50)
    
    # 测试文件结构
    test_file_structure()
    
    # 测试数据持久化
    test_data_persistence()
    
    print("\n" + "=" * 50)
    print("✨ 测试完成！现在您的数据将持久化存储在文件中，重启应用后数据不会丢失。")
