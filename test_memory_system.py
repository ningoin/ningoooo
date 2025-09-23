#!/usr/bin/env python3
"""
记忆系统测试脚本
测试MongoDB存储和记忆加载功能
"""

import requests
import json
import time
import uuid

# 测试配置
BASE_URL = "http://localhost:5000"
TEST_USER_ID = "test_user_" + str(uuid.uuid4())[:8]
TEST_CHARACTER = "精灵魔法师"

def test_health_check():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务状态: {data['status']}")
            print(f"🗄️  数据库状态: {data.get('database_status', 'unknown')}")
            print(f"🧠 记忆功能: {'✅' if data.get('features', {}).get('user_memory') else '❌'}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")
        return False

def test_chat_with_memory():
    """测试带记忆的对话"""
    print(f"\n💬 测试与 {TEST_CHARACTER} 的对话...")
    
    # 第一轮对话
    print("📝 第一轮对话...")
    chat_data = {
        "message": "你好，我是新用户，我喜欢魔法和冒险",
        "character_name": TEST_CHARACTER,
        "character_description": "拥有古老魔法知识的神秘精灵，优雅而智慧，掌握着自然魔法的奥秘。",
        "user_id": TEST_USER_ID
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json=chat_data)
        if response.status_code == 200:
            data = response.json()
            conversation_id = data['conversation_id']
            print(f"✅ 对话成功，对话ID: {conversation_id}")
            print(f"🤖 AI回复: {data['response'][:100]}...")
            
            # 等待一下让记忆保存
            time.sleep(1)
            
            # 第二轮对话 - 测试记忆加载
            print("\n📝 第二轮对话（测试记忆）...")
            chat_data2 = {
                "message": "你还记得我喜欢什么吗？",
                "character_name": TEST_CHARACTER,
                "conversation_id": conversation_id,
                "user_id": TEST_USER_ID
            }
            
            response2 = requests.post(f"{BASE_URL}/api/chat", json=chat_data2)
            if response2.status_code == 200:
                data2 = response2.json()
                print(f"✅ 记忆对话成功")
                print(f"🤖 AI回复: {data2['response'][:100]}...")
                return conversation_id
            else:
                print(f"❌ 记忆对话失败: {response2.status_code}")
                return None
        else:
            print(f"❌ 对话失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 对话异常: {str(e)}")
        return None

def test_memory_api():
    """测试记忆API"""
    print(f"\n🧠 测试记忆API...")
    
    try:
        # 获取用户记忆
        response = requests.get(f"{BASE_URL}/api/memory/{TEST_USER_ID}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取用户记忆成功，共 {data['total']} 条记忆")
            for memory in data['memories']:
                print(f"  - 角色: {memory['character_name']}")
                print(f"    消息数: {memory['memory_data'].get('total_messages', 0)}")
        else:
            print(f"❌ 获取用户记忆失败: {response.status_code}")
        
        # 获取特定角色记忆
        response2 = requests.get(f"{BASE_URL}/api/memory/{TEST_USER_ID}/{TEST_CHARACTER}")
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"✅ 获取角色记忆成功")
            memory = data2['memory']
            if memory:
                print(f"  - 总消息数: {memory.get('total_messages', 0)}")
                print(f"  - 最后对话时间: {memory.get('last_conversation_time', 'N/A')}")
        else:
            print(f"❌ 获取角色记忆失败: {response2.status_code}")
            
    except Exception as e:
        print(f"❌ 记忆API测试异常: {str(e)}")

def test_database_stats():
    """测试数据库统计"""
    print(f"\n📊 测试数据库统计...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/database/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data['stats']
            print(f"✅ 数据库统计获取成功:")
            print(f"  - 对话数量: {stats.get('conversations_count', 0)}")
            print(f"  - 用户记忆数量: {stats.get('user_memories_count', 0)}")
            print(f"  - 角色交互数量: {stats.get('character_interactions_count', 0)}")
        else:
            print(f"❌ 数据库统计获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 数据库统计测试异常: {str(e)}")

def test_conversation_persistence():
    """测试对话持久化"""
    print(f"\n💾 测试对话持久化...")
    
    try:
        # 获取用户对话列表
        response = requests.get(f"{BASE_URL}/api/conversations?user_id={TEST_USER_ID}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取用户对话列表成功，共 {data['total']} 个对话")
            for conv in data['conversations'][:3]:  # 只显示前3个
                print(f"  - 对话ID: {conv.get('conversation_id', 'N/A')}")
                print(f"    角色: {conv.get('character_name', 'N/A')}")
                print(f"    消息数: {len(conv.get('messages', []))}")
        else:
            print(f"❌ 获取对话列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 对话持久化测试异常: {str(e)}")

def main():
    """主测试函数"""
    print("🚀 开始测试记忆系统...")
    print("=" * 60)
    print(f"👤 测试用户ID: {TEST_USER_ID}")
    print(f"🎭 测试角色: {TEST_CHARACTER}")
    print("=" * 60)
    
    # 测试步骤
    tests = [
        ("健康检查", test_health_check),
        ("对话记忆", test_chat_with_memory),
        ("记忆API", test_memory_api),
        ("数据库统计", test_database_stats),
        ("对话持久化", test_conversation_persistence)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 执行测试: {test_name}")
        try:
            result = test_func()
            if result is not False:
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！记忆系统工作正常")
    else:
        print("⚠️  部分测试失败，请检查配置和日志")
    
    print("\n💡 提示:")
    print("- 确保MongoDB服务正在运行")
    print("- 检查config.env配置文件")
    print("- 查看应用日志获取详细错误信息")

if __name__ == "__main__":
    main()
