"""
MongoDB数据库操作模块
用于存储用户对话记录、记忆和角色交互历史
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('config.env')

logger = logging.getLogger(__name__)

class ConversationDatabase:
    """对话数据库管理类"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.database_name = os.getenv('MONGODB_DATABASE', 'ai_chat_system')
        
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            # 测试连接
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            
            # 创建集合
            self.conversations = self.db.conversations
            self.user_memories = self.db.user_memories
            self.character_interactions = self.db.character_interactions
            
            # 创建索引
            self._create_indexes()
            
            logger.info(f"成功连接到MongoDB数据库: {self.database_name}")
            
        except ConnectionFailure as e:
            logger.error(f"MongoDB连接失败: {str(e)}")
            raise
    
    def _create_indexes(self):
        """创建数据库索引以提高查询性能"""
        try:
            # 对话集合索引
            self.conversations.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
            self.conversations.create_index([("character_name", ASCENDING), ("created_at", DESCENDING)])
            self.conversations.create_index("conversation_id", unique=True)
            
            # 用户记忆集合索引
            self.user_memories.create_index([("user_id", ASCENDING), ("character_name", ASCENDING)])
            self.user_memories.create_index("user_id")
            
            # 角色交互集合索引
            self.character_interactions.create_index([("user_id", ASCENDING), ("character_name", ASCENDING)])
            self.character_interactions.create_index("user_id")
            
            logger.info("数据库索引创建成功")
            
        except Exception as e:
            logger.error(f"创建索引失败: {str(e)}")
    
    def save_conversation(self, conversation_data: Dict[str, Any]) -> bool:
        """
        保存对话记录
        
        Args:
            conversation_data: 对话数据字典
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 添加时间戳
            conversation_data['updated_at'] = datetime.now()
            
            # 使用upsert操作，如果conversation_id存在则更新，否则插入
            result = self.conversations.update_one(
                {"conversation_id": conversation_data['conversation_id']},
                {"$set": conversation_data},
                upsert=True
            )
            
            logger.info(f"对话保存成功: {conversation_data['conversation_id']}")
            return True
            
        except Exception as e:
            logger.error(f"保存对话失败: {str(e)}")
            return False
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定对话记录
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            Dict: 对话数据，如果不存在返回None
        """
        try:
            conversation = self.conversations.find_one({"conversation_id": conversation_id})
            if conversation:
                # 移除MongoDB的_id字段
                conversation.pop('_id', None)
            return conversation
            
        except Exception as e:
            logger.error(f"获取对话失败: {str(e)}")
            return None
    
    def get_user_conversations(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取用户的所有对话记录
        
        Args:
            user_id: 用户ID
            limit: 返回记录数量限制
            
        Returns:
            List[Dict]: 对话记录列表
        """
        try:
            conversations = list(self.conversations.find(
                {"user_id": user_id}
            ).sort("created_at", DESCENDING).limit(limit))
            
            # 移除MongoDB的_id字段
            for conv in conversations:
                conv.pop('_id', None)
            
            return conversations
            
        except Exception as e:
            logger.error(f"获取用户对话失败: {str(e)}")
            return []
    
    def get_character_conversations(self, character_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取特定角色的所有对话记录
        
        Args:
            character_name: 角色名称
            limit: 返回记录数量限制
            
        Returns:
            List[Dict]: 对话记录列表
        """
        try:
            conversations = list(self.conversations.find(
                {"character_name": character_name}
            ).sort("created_at", DESCENDING).limit(limit))
            
            # 移除MongoDB的_id字段
            for conv in conversations:
                conv.pop('_id', None)
            
            return conversations
            
        except Exception as e:
            logger.error(f"获取角色对话失败: {str(e)}")
            return []
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        删除指定对话记录
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            result = self.conversations.delete_one({"conversation_id": conversation_id})
            success = result.deleted_count > 0
            
            if success:
                logger.info(f"对话删除成功: {conversation_id}")
            else:
                logger.warning(f"对话不存在: {conversation_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"删除对话失败: {str(e)}")
            return False
    
    def save_user_memory(self, user_id: str, character_name: str, memory_data: Dict[str, Any]) -> bool:
        """
        保存用户记忆
        
        Args:
            user_id: 用户ID
            character_name: 角色名称
            memory_data: 记忆数据
            
        Returns:
            bool: 保存是否成功
        """
        try:
            memory_doc = {
                "user_id": user_id,
                "character_name": character_name,
                "memory_data": memory_data,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # 使用upsert操作
            result = self.user_memories.update_one(
                {"user_id": user_id, "character_name": character_name},
                {"$set": memory_doc},
                upsert=True
            )
            
            logger.info(f"用户记忆保存成功: {user_id} - {character_name}")
            return True
            
        except Exception as e:
            logger.error(f"保存用户记忆失败: {str(e)}")
            return False
    
    def get_user_memory(self, user_id: str, character_name: str) -> Optional[Dict[str, Any]]:
        """
        获取用户记忆
        
        Args:
            user_id: 用户ID
            character_name: 角色名称
            
        Returns:
            Dict: 记忆数据，如果不存在返回None
        """
        try:
            memory = self.user_memories.find_one({
                "user_id": user_id,
                "character_name": character_name
            })
            
            if memory:
                memory.pop('_id', None)
                return memory.get('memory_data', {})
            
            return None
            
        except Exception as e:
            logger.error(f"获取用户记忆失败: {str(e)}")
            return None
    
    def get_user_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户的所有记忆
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Dict]: 记忆列表
        """
        try:
            memories = list(self.user_memories.find({"user_id": user_id}))
            
            # 移除MongoDB的_id字段并格式化
            formatted_memories = []
            for memory in memories:
                memory.pop('_id', None)
                formatted_memories.append({
                    "character_name": memory.get("character_name"),
                    "memory_data": memory.get("memory_data", {}),
                    "created_at": memory.get("created_at"),
                    "updated_at": memory.get("updated_at")
                })
            
            return formatted_memories
            
        except Exception as e:
            logger.error(f"获取用户所有记忆失败: {str(e)}")
            return []
    
    def save_character_interaction(self, user_id: str, character_name: str, interaction_data: Dict[str, Any]) -> bool:
        """
        保存角色交互记录
        
        Args:
            user_id: 用户ID
            character_name: 角色名称
            interaction_data: 交互数据
            
        Returns:
            bool: 保存是否成功
        """
        try:
            interaction_doc = {
                "user_id": user_id,
                "character_name": character_name,
                "interaction_data": interaction_data,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # 使用upsert操作
            result = self.character_interactions.update_one(
                {"user_id": user_id, "character_name": character_name},
                {"$set": interaction_doc},
                upsert=True
            )
            
            logger.info(f"角色交互记录保存成功: {user_id} - {character_name}")
            return True
            
        except Exception as e:
            logger.error(f"保存角色交互记录失败: {str(e)}")
            return False
    
    def get_character_interaction(self, user_id: str, character_name: str) -> Optional[Dict[str, Any]]:
        """
        获取角色交互记录
        
        Args:
            user_id: 用户ID
            character_name: 角色名称
            
        Returns:
            Dict: 交互数据，如果不存在返回None
        """
        try:
            interaction = self.character_interactions.find_one({
                "user_id": user_id,
                "character_name": character_name
            })
            
            if interaction:
                interaction.pop('_id', None)
                return interaction.get('interaction_data', {})
            
            return None
            
        except Exception as e:
            logger.error(f"获取角色交互记录失败: {str(e)}")
            return None
    
    def get_recent_conversations(self, user_id: str, character_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取用户与特定角色的最近对话记录
        
        Args:
            user_id: 用户ID
            character_name: 角色名称
            limit: 返回记录数量限制
            
        Returns:
            List[Dict]: 对话记录列表
        """
        try:
            conversations = list(self.conversations.find({
                "user_id": user_id,
                "character_name": character_name
            }).sort("created_at", DESCENDING).limit(limit))
            
            # 移除MongoDB的_id字段
            for conv in conversations:
                conv.pop('_id', None)
            
            return conversations
            
        except Exception as e:
            logger.error(f"获取最近对话失败: {str(e)}")
            return []
    
    def cleanup_old_conversations(self, days: int = 30) -> int:
        """
        清理旧的对话记录
        
        Args:
            days: 保留天数
            
        Returns:
            int: 删除的记录数量
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            result = self.conversations.delete_many({
                "created_at": {"$lt": cutoff_date}
            })
            
            deleted_count = result.deleted_count
            logger.info(f"清理了 {deleted_count} 条旧对话记录")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理旧对话记录失败: {str(e)}")
            return 0
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        获取数据库统计信息
        
        Returns:
            Dict: 统计信息
        """
        try:
            stats = {
                "conversations_count": self.conversations.count_documents({}),
                "user_memories_count": self.user_memories.count_documents({}),
                "character_interactions_count": self.character_interactions.count_documents({}),
                "database_name": self.database_name,
                "last_updated": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取数据库统计信息失败: {str(e)}")
            return {}
    
    def close_connection(self):
        """关闭数据库连接"""
        try:
            self.client.close()
            logger.info("MongoDB连接已关闭")
        except Exception as e:
            logger.error(f"关闭MongoDB连接失败: {str(e)}")


# 全局数据库实例
db_instance = None

def get_database() -> ConversationDatabase:
    """获取数据库实例（单例模式）"""
    global db_instance
    if db_instance is None:
        db_instance = ConversationDatabase()
    return db_instance
