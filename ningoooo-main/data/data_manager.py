# -*- coding: utf-8 -*-
"""
数据管理模块 - 文件存储替代内存存储
支持对话记录和自定义角色的持久化存储
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

class DataManager:
    """数据管理器 - 使用JSON文件存储数据"""
    
    def __init__(self, data_dir: str = "data"):
        """
        初始化数据管理器
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = data_dir
        self.conversations_file = os.path.join(data_dir, "conversations.json")
        self.custom_roles_file = os.path.join(data_dir, "custom_roles.json")
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 初始化数据文件
        self._init_data_files()
    
    def _init_data_files(self):
        """初始化数据文件"""
        # 初始化对话文件
        if not os.path.exists(self.conversations_file):
            self._save_json(self.conversations_file, {})
        
        # 初始化自定义角色文件
        if not os.path.exists(self.custom_roles_file):
            self._save_json(self.custom_roles_file, {})
    
    def _load_json(self, file_path: str) -> Dict:
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json(self, file_path: str, data: Dict):
        """保存JSON文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ==================== 对话管理 ====================
    
    def save_conversation(self, conversation_id: str, user_id: str, 
                         character_name: str, character_description: str) -> Dict:
        """
        保存对话信息
        
        Args:
            conversation_id: 对话ID
            user_id: 用户ID
            character_name: 角色名称
            character_description: 角色描述
            
        Returns:
            对话信息字典
        """
        conversations = self._load_json(self.conversations_file)
        
        conversation_data = {
            "id": conversation_id,
            "user_id": user_id,
            "character_name": character_name,
            "character_description": character_description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }
        
        conversations[conversation_id] = conversation_data
        self._save_json(self.conversations_file, conversations)
        
        return conversation_data
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        获取对话信息
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            对话信息字典或None
        """
        conversations = self._load_json(self.conversations_file)
        return conversations.get(conversation_id)
    
    def get_all_conversations(self) -> List[Dict]:
        """
        获取所有对话列表
        
        Returns:
            对话列表
        """
        conversations = self._load_json(self.conversations_file)
        return list(conversations.values())
    
    def add_message_to_conversation(self, conversation_id: str, role: str, content: str) -> bool:
        """
        向对话添加消息
        
        Args:
            conversation_id: 对话ID
            role: 角色 ('user' 或 'assistant')
            content: 消息内容
            
        Returns:
            是否成功添加
        """
        conversations = self._load_json(self.conversations_file)
        
        if conversation_id not in conversations:
            return False
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        conversations[conversation_id]["messages"].append(message)
        conversations[conversation_id]["updated_at"] = datetime.now().isoformat()
        
        self._save_json(self.conversations_file, conversations)
        return True
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        删除对话
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            是否成功删除
        """
        conversations = self._load_json(self.conversations_file)
        
        if conversation_id in conversations:
            del conversations[conversation_id]
            self._save_json(self.conversations_file, conversations)
            return True
        
        return False
    
    # ==================== 自定义角色管理 ====================
    
    def save_custom_role(self, role_data: Dict) -> Dict:
        """
        保存自定义角色
        
        Args:
            role_data: 角色数据字典
            
        Returns:
            保存的角色数据
        """
        custom_roles = self._load_json(self.custom_roles_file)
        
        # 确保有ID
        if "id" not in role_data:
            role_data["id"] = str(uuid.uuid4())
        
        # 添加时间戳
        role_data["created_at"] = datetime.now().isoformat()
        role_data["updated_at"] = datetime.now().isoformat()
        role_data["is_custom"] = True
        
        custom_roles[role_data["id"]] = role_data
        self._save_json(self.custom_roles_file, custom_roles)
        
        return role_data
    
    def get_custom_role(self, role_id: str) -> Optional[Dict]:
        """
        获取自定义角色
        
        Args:
            role_id: 角色ID
            
        Returns:
            角色数据字典或None
        """
        custom_roles = self._load_json(self.custom_roles_file)
        return custom_roles.get(role_id)
    
    def get_all_custom_roles(self) -> List[Dict]:
        """
        获取所有自定义角色
        
        Returns:
            角色列表
        """
        custom_roles = self._load_json(self.custom_roles_file)
        return list(custom_roles.values())
    
    def update_custom_role(self, role_id: str, role_data: Dict) -> bool:
        """
        更新自定义角色
        
        Args:
            role_id: 角色ID
            role_data: 更新的角色数据
            
        Returns:
            是否成功更新
        """
        custom_roles = self._load_json(self.custom_roles_file)
        
        if role_id not in custom_roles:
            return False
        
        # 保留原有数据，只更新提供的字段
        existing_role = custom_roles[role_id]
        for key, value in role_data.items():
            if key != "id":  # 不允许修改ID
                existing_role[key] = value
        
        existing_role["updated_at"] = datetime.now().isoformat()
        
        self._save_json(self.custom_roles_file, custom_roles)
        return True
    
    def delete_custom_role(self, role_id: str) -> bool:
        """
        删除自定义角色
        
        Args:
            role_id: 角色ID
            
        Returns:
            是否成功删除
        """
        custom_roles = self._load_json(self.custom_roles_file)
        
        if role_id in custom_roles:
            del custom_roles[role_id]
            self._save_json(self.custom_roles_file, custom_roles)
            return True
        
        return False
    
    def search_custom_roles(self, keyword: str) -> List[Dict]:
        """
        搜索自定义角色
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的角色列表
        """
        custom_roles = self._load_json(self.custom_roles_file)
        keyword_lower = keyword.lower()
        
        results = []
        for role in custom_roles.values():
            if (keyword_lower in role.get("name", "").lower() or 
                keyword_lower in role.get("description", "").lower() or
                keyword_lower in role.get("personality", "").lower()):
                results.append(role)
        
        return results
    
    # ==================== 数据统计 ====================
    
    def get_data_stats(self) -> Dict:
        """
        获取数据统计信息
        
        Returns:
            统计信息字典
        """
        conversations = self._load_json(self.conversations_file)
        custom_roles = self._load_json(self.custom_roles_file)
        
        total_messages = 0
        for conv in conversations.values():
            total_messages += len(conv.get("messages", []))
        
        return {
            "total_conversations": len(conversations),
            "total_custom_roles": len(custom_roles),
            "total_messages": total_messages,
            "data_dir": self.data_dir,
            "last_updated": datetime.now().isoformat()
        }
    
    def backup_data(self, backup_dir: str = "data/backup") -> str:
        """
        备份数据
        
        Args:
            backup_dir: 备份目录
            
        Returns:
            备份文件路径
        """
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 备份对话数据
        conversations = self._load_json(self.conversations_file)
        backup_file = os.path.join(backup_dir, f"conversations_backup_{timestamp}.json")
        self._save_json(backup_file, conversations)
        
        # 备份自定义角色数据
        custom_roles = self._load_json(self.custom_roles_file)
        backup_file = os.path.join(backup_dir, f"custom_roles_backup_{timestamp}.json")
        self._save_json(backup_file, custom_roles)
        
        return backup_dir
    
    def restore_data(self, backup_file: str, data_type: str) -> bool:
        """
        恢复数据
        
        Args:
            backup_file: 备份文件路径
            data_type: 数据类型 ('conversations' 或 'custom_roles')
            
        Returns:
            是否成功恢复
        """
        try:
            backup_data = self._load_json(backup_file)
            
            if data_type == "conversations":
                self._save_json(self.conversations_file, backup_data)
            elif data_type == "custom_roles":
                self._save_json(self.custom_roles_file, backup_data)
            else:
                return False
            
            return True
        except Exception as e:
            print(f"恢复数据失败: {e}")
            return False


# 全局数据管理器实例
data_manager = DataManager()
