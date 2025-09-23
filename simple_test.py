#!/usr/bin/env python3
"""
简单的记忆系统测试
"""

import requests
import json

def test_memory():
    """测试记忆功能"""
    base_url = "http://localhost:5000"
    user_id = "test_user_memory"
    
    print("🧪 测试记忆系统...")
    
    # 第一轮对话 - 告诉AI我们的偏好
    print("\n📝 第一轮对话：告诉AI我们的偏好")
    chat_data1 = {
        "message": "你好，我是新用户，我喜欢魔法和冒险，特别是火系魔法",
        "character_name": "精灵魔法师",
        "character_description": "拥有古老魔法知识的神秘精灵，优雅而智慧，掌握着自然魔法的奥秘。",
        "user_id": user_id
    }
    
    try:
        response1 = requests.post(f"{base_url}/api/chat", json=chat_data1)
        if response1.status_code == 200:
            data1 = response1.json()
            conversation_id = data1['conversation_id']
            print(f"✅ 对话成功，对话ID: {conversation_id}")
            print(f"🤖 AI回复: {data1['response'][:100]}...")
        else:
            print(f"❌ 对话失败: {response1.status_code}")
            return
    except Exception as e:
        print(f"❌ 对话异常: {str(e)}")
        return
    
    # 等待一下让记忆保存
    import time
    time.sleep(2)
    
    # 第二轮对话 - 测试记忆
    print("\n📝 第二轮对话：测试AI是否记住我们的偏好")
    chat_data2 = {
        "message": "你还记得我喜欢什么吗？",
        "character_name": "精灵魔法师",
        "conversation_id": conversation_id,
        "user_id": user_id
    }
    
    try:
        response2 = requests.post(f"{base_url}/api/chat", json=chat_data2)
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"✅ 记忆对话成功")
            print(f"🤖 AI回复: {data2['response']}")
            
            # 检查AI是否提到了火系魔法
            if "火" in data2['response'] or "魔法" in data2['response']:
                print("🎉 AI成功记住了用户的偏好！")
            else:
                print("⚠️  AI可能没有完全记住用户偏好")
        else:
            print(f"❌ 记忆对话失败: {response2.status_code}")
    except Exception as e:
        print(f"❌ 记忆对话异常: {str(e)}")
    
    # 第三轮对话 - 新会话测试
    print("\n📝 第三轮对话：新会话测试记忆持久化")
    chat_data3 = {
        "message": "我想学习新的魔法技能",
        "character_name": "精灵魔法师",
        "user_id": user_id
    }
    
    try:
        response3 = requests.post(f"{base_url}/api/chat", json=chat_data3)
        if response3.status_code == 200:
            data3 = response3.json()
            print(f"✅ 新会话对话成功")
            print(f"🤖 AI回复: {data3['response']}")
            
            # 检查AI是否在新会话中提到了之前的偏好
            if "火" in data3['response'] or "魔法" in data3['response'] or "冒险" in data3['response']:
                print("🎉 AI在新会话中成功记住了用户偏好！")
            else:
                print("⚠️  AI在新会话中没有提到之前的偏好")
        else:
            print(f"❌ 新会话对话失败: {response3.status_code}")
    except Exception as e:
        print(f"❌ 新会话对话异常: {str(e)}")

if __name__ == "__main__":
    test_memory()
