from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import os
import uuid
import logging
import json
import base64
import io
import tempfile
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from datetime import datetime
from database import get_database

# 加载环境变量
load_dotenv('config.env')

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-api-key')
OPENAI_API_URL = os.getenv('OPENAI_API_URL', 'https://api.openai.com/v1')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

# 初始化数据库连接
try:
    db = get_database()
    logger.info("MongoDB数据库连接成功")
except Exception as e:
    logger.error(f"MongoDB数据库连接失败: {str(e)}")
    db = None

# 内存中的对话缓存（用于快速访问）
conversations = {}

# 角色库数据（与前端保持一致）
ROLE_LIBRARY = [
    {
        'id': 'elf-mage',
        'name': '精灵魔法师',
        'description': '拥有古老魔法知识的神秘精灵，优雅而智慧，掌握着自然魔法的奥秘。',
        'image': 'https://modao.cc/ai/uploads/ai_pics/29/293721/aigp_1758521099.jpeg',
        'category': 'fantasy',
        'tags': ['魔法', '智慧', '优雅'],
        'personality': '神秘、优雅、智慧'
    },
    {
        'id': 'future-warrior',
        'name': '未来战士',
        'description': '来自未来的高科技战士，装备着先进的武器和装甲，拥有强大的战斗力。',
        'image': 'https://modao.cc/ai/uploads/ai_pics/29/293722/aigp_1758521101.jpeg',
        'category': 'sci-fi',
        'tags': ['科技', '战斗', '未来'],
        'personality': '直接、果断、勇敢'
    },
    {
        'id': 'ancient-emperor',
        'name': '古代帝王',
        'description': '威严的古代帝王，拥有至高无上的权力和智慧，统治着庞大的帝国。',
        'image': 'https://modao.cc/ai/uploads/ai_pics/29/293723/aigp_1758521103.jpeg',
        'category': 'historical',
        'tags': ['权力', '智慧', '威严'],
        'personality': '威严、睿智、庄重'
    },
    {
        'id': 'detective',
        'name': '名侦探',
        'description': '著名的推理大师，善于分析线索和破解谜题，拥有敏锐的观察力。',
        'image': 'https://modao.cc/ai/uploads/ai_pics/29/293724/aigp_1758521105.jpeg',
        'category': 'modern',
        'tags': ['推理', '观察', '逻辑'],
        'personality': '逻辑、敏锐、冷静'
    },
    {
        'id': 'robot',
        'name': '机器人',
        'description': '先进的智能机器人，拥有强大的人工智能，友好而乐于助人。',
        'image': 'https://modao.cc/ai/uploads/ai_pics/29/293724/aigp_1758521105.jpeg',
        'category': 'sci-fi',
        'tags': ['AI', '科技', '友好'],
        'personality': '机械、友好、理性'
    },
    {
        'id': 'witch',
        'name': '女巫',
        'description': '神秘的女巫，掌握着古老的魔法和预言术，拥有超自然的力量。',
        'image': 'https://modao.cc/ai/uploads/ai_pics/29/293724/aigp_1758521105.jpeg',
        'category': 'fantasy',
        'tags': ['魔法', '神秘', '预言'],
        'personality': '神秘、预言、智慧'
    },
    {
        'id': 'space-explorer',
        'name': '太空探险家',
        'description': '勇敢的太空探险家，探索宇宙的奥秘，发现新的星球和文明。',
        'image': 'https://modao.cc/ai/uploads/ai_pics/29/293724/aigp_1758521105.jpeg',
        'category': 'sci-fi',
        'tags': ['探索', '冒险', '太空'],
        'personality': '冒险、好奇、勇敢'
    },
    {
        'id': 'martial-artist',
        'name': '武侠大师',
        'description': '武林中的绝世高手，精通各种武学，拥有深厚的内功和武德。',
        'image': 'https://modao.cc/ai/uploads/ai_pics/29/293724/aigp_1758521105.jpeg',
        'category': 'historical',
        'tags': ['武功', '江湖', '侠义'],
        'personality': '豪爽、正义、侠义'
    },
    {
        'id': 'space-commander',
        'name': '星际指挥官',
        'description': '星际舰队的最高指挥官，负责指挥太空作战，保护银河系的安全。',
        'image': 'https://modao.cc/ai/uploads/ai_pics/29/293724/aigp_1758521105.jpeg',
        'category': 'sci-fi',
        'tags': ['指挥', '军事', '太空'],
        'personality': '权威、果断、战略'
    }
]

@app.route('/api/voice/transcribe', methods=['POST'])
def transcribe_voice():
    """
    语音转文本API端点
    接收音频文件并转换为文本
    """
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传音频文件'
            }), 400
        
        audio_file = request.files['file']
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': '音频文件名为空'
            }), 400
        
        # 获取角色信息
        role_id = request.form.get('role_id', '')
        role_name = request.form.get('role_name', '')
        role_description = request.form.get('role_description', '')
        
        logger.info(f"收到语音转文本请求 - 角色: {role_name}, 文件: {audio_file.filename}")
        
        # 调用OpenAI Whisper API进行语音转文本
        transcription = call_whisper_api(audio_file)
        
        if transcription:
            return jsonify({
                'success': True,
                'transcription': transcription,
                'role_id': role_id,
                'role_name': role_name,
                'role_description': role_description
            })
        else:
            return jsonify({
                'success': False,
                'error': '语音转文本失败'
            }), 500
            
    except Exception as e:
        logger.error(f"语音转文本错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/voice/synthesize', methods=['POST'])
def synthesize_voice():
    """
    文本转语音API端点
    接收文本并转换为语音文件
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据格式错误'
            }), 400
        
        text = data.get('text', '')
        voice = data.get('voice', 'alloy')  # 默认使用alloy声音
        model = data.get('model', 'tts-1')  # 默认使用tts-1模型
        
        if not text:
            return jsonify({
                'success': False,
                'error': '文本内容不能为空'
            }), 400
        
        logger.info(f"收到文本转语音请求 - 文本: {text[:50]}..., 声音: {voice}")
        
        # 调用OpenAI TTS API进行文本转语音
        audio_data = call_tts_api(text, voice, model)
        
        if audio_data:
            # 创建临时文件保存音频数据
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(audio_data)
                temp_file.flush()
                
                return send_file(
                    temp_file.name,
                    as_attachment=True,
                    download_name='ai_response.mp3',
                    mimetype='audio/mpeg'
                )
        else:
            return jsonify({
                'success': False,
                'error': '文本转语音失败'
            }), 500
            
    except Exception as e:
        logger.error(f"文本转语音错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    """
    与AI角色进行对话
    接收参数：
    - message: 用户输入的文本
    - character_name: 角色名称
    - character_description: 角色描述
    - role_id: 角色ID（可选）
    - conversation_id: 对话ID（可选）
    - user_id: 用户ID（可选）
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        character_name = data.get('character_name', '小助手')
        character_description = data.get('character_description', '你是一个友善、乐于助人的AI助手')
        role_id = data.get('role_id', '')
        conversation_id = data.get('conversation_id', '')
        user_id = data.get('user_id', str(uuid.uuid4()))
        
        logger.info(f"收到请求 - 消息: {user_message[:50]}..., 角色: {character_name}, 角色ID: {role_id}")
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': '消息不能为空'
            }), 400
        
        # 如果提供了role_id，从角色库获取详细信息
        if role_id:
            role_info = get_role_by_id(role_id)
            if role_info:
                character_name = role_info['name']
                character_description = role_info['description']
                logger.info(f"使用角色库中的角色: {character_name}")
        
        # 如果没有提供conversation_id，创建新的对话
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            conversation_data = {
                'conversation_id': conversation_id,
                'user_id': user_id,
                'character_name': character_name,
                'character_description': character_description,
                'messages': [],
                'created_at': datetime.now().isoformat()
            }
            conversations[conversation_id] = conversation_data
            
            # 保存到数据库
            if db:
                db.save_conversation(conversation_data)
        else:
            # 尝试从数据库加载对话
            if db:
                conversation_data = db.get_conversation(conversation_id)
                if conversation_data:
                    conversations[conversation_id] = conversation_data
                else:
                    # 如果数据库中没有，创建新的
                    conversation_data = {
                        'conversation_id': conversation_id,
                        'user_id': user_id,
                        'character_name': character_name,
                        'character_description': character_description,
                        'messages': [],
                        'created_at': datetime.now().isoformat()
                    }
                    conversations[conversation_id] = conversation_data
                    db.save_conversation(conversation_data)
            else:
                # 如果数据库不可用，使用内存存储
                if conversation_id not in conversations:
                    conversations[conversation_id] = {
                        'conversation_id': conversation_id,
                        'user_id': user_id,
                        'character_name': character_name,
                        'character_description': character_description,
                        'messages': [],
                        'created_at': datetime.now().isoformat()
                    }
        
        logger.info(f"处理用户消息: {user_message[:50]}... (对话ID: {conversation_id})")
        
        # 调用OpenAI API
        ai_response = call_openai_api(
            user_message, 
            character_name, 
            character_description, 
            conversation_id
        )
        
        # 保存对话历史
        conversations[conversation_id]['messages'].append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        conversations[conversation_id]['messages'].append({
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # 保存到数据库
        if db:
            db.save_conversation(conversations[conversation_id])
            
            # 保存用户记忆（基于对话内容提取关键信息）
            save_user_memory_from_conversation(user_id, character_name, user_message, ai_response)
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'character_name': character_name,
            'character_description': character_description,
            'role_id': role_id,
            'conversation_id': conversation_id,
            'user_id': user_id
        })
        
    except Exception as e:
        logger.error(f"聊天处理错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def call_whisper_api(audio_file):
    """
    调用OpenAI Whisper API进行语音转文本
    """
    try:
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}'
        }
        
        # 准备文件数据
        files = {
            'file': (audio_file.filename, audio_file.stream, audio_file.content_type)
        }
        
        data = {
            'model': 'whisper-1',
            'language': 'zh'  # 设置为中文
        }
        
        logger.info(f"调用OpenAI Whisper API: {OPENAI_API_URL}/audio/transcriptions")
        
        response = requests.post(
            f'{OPENAI_API_URL}/audio/transcriptions',
            headers=headers,
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            transcription = result.get('text', '')
            logger.info(f"语音转文本成功: {transcription[:50]}...")
            return transcription
        else:
            error_msg = f'Whisper API调用失败: {response.status_code} - {response.text}'
            logger.error(error_msg)
            raise Exception(error_msg)
            
    except requests.exceptions.Timeout:
        error_msg = 'Whisper API请求超时'
        logger.error(error_msg)
        raise Exception(error_msg)
    except requests.exceptions.RequestException as e:
        error_msg = f'Whisper API网络请求失败: {str(e)}'
        logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f'Whisper API调用错误: {str(e)}'
        logger.error(error_msg)
        raise Exception(error_msg)

def call_tts_api(text, voice='alloy', model='tts-1'):
    """
    调用OpenAI TTS API进行文本转语音
    """
    try:
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'input': text,
            'voice': voice,
            'response_format': 'mp3'
        }
        
        logger.info(f"调用OpenAI TTS API: {OPENAI_API_URL}/audio/speech")
        
        response = requests.post(
            f'{OPENAI_API_URL}/audio/speech',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            audio_data = response.content
            logger.info(f"文本转语音成功，音频大小: {len(audio_data)} bytes")
            return audio_data
        else:
            error_msg = f'TTS API调用失败: {response.status_code} - {response.text}'
            logger.error(error_msg)
            raise Exception(error_msg)
            
    except requests.exceptions.Timeout:
        error_msg = 'TTS API请求超时'
        logger.error(error_msg)
        raise Exception(error_msg)
    except requests.exceptions.RequestException as e:
        error_msg = f'TTS API网络请求失败: {str(e)}'
        logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f'TTS API调用错误: {str(e)}'
        logger.error(error_msg)
        raise Exception(error_msg)

def get_role_by_id(role_id):
    """
    根据角色ID获取角色信息
    """
    for role in ROLE_LIBRARY:
        if role['id'] == role_id:
            return role
    return None

def get_role_by_name(role_name):
    """
    根据角色名称获取角色信息
    """
    for role in ROLE_LIBRARY:
        if role['name'] == role_name:
            return role
    return None

def save_user_memory_from_conversation(user_id, character_name, user_message, ai_response):
    """
    从对话中提取并保存用户记忆
    """
    try:
        if not db:
            return
            
        # 获取现有记忆
        existing_memory = db.get_user_memory(user_id, character_name) or {}
        
        # 简单的记忆提取逻辑（可以根据需要扩展）
        memory_updates = {
            'last_conversation_time': datetime.now().isoformat(),
            'total_messages': existing_memory.get('total_messages', 0) + 1,
            'user_preferences': existing_memory.get('user_preferences', {}),
            'conversation_topics': existing_memory.get('conversation_topics', [])
        }
        
        # 提取用户偏好（简单示例）
        if '喜欢' in user_message or '不喜欢' in user_message:
            if '喜欢' in user_message:
                memory_updates['user_preferences']['likes'] = memory_updates['user_preferences'].get('likes', [])
            if '不喜欢' in user_message:
                memory_updates['user_preferences']['dislikes'] = memory_updates['user_preferences'].get('dislikes', [])
        
        # 保存记忆
        db.save_user_memory(user_id, character_name, memory_updates)
        
    except Exception as e:
        logger.error(f"保存用户记忆失败: {str(e)}")

def load_user_memory_for_conversation(user_id, character_name):
    """
    为对话加载用户记忆
    """
    try:
        if not db:
            return {}
            
        # 获取用户记忆
        user_memory = db.get_user_memory(user_id, character_name) or {}
        
        # 获取最近的对话历史
        recent_conversations = db.get_recent_conversations(user_id, character_name, limit=5)
        
        return {
            'user_memory': user_memory,
            'recent_conversations': recent_conversations
        }
        
    except Exception as e:
        logger.error(f"加载用户记忆失败: {str(e)}")
        return {}

def call_openai_api(user_message, character_name, character_description, conversation_id):
    """
    调用OpenAI Chat Completions API获取AI回复
    """
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_API_KEY}'
        }
        
        # 获取用户ID
        user_id = conversations.get(conversation_id, {}).get('user_id', '')
        
        # 加载用户记忆和历史对话
        memory_data = load_user_memory_for_conversation(user_id, character_name) if user_id else {}
        user_memory = memory_data.get('user_memory', {})
        recent_conversations = memory_data.get('recent_conversations', [])
        
        # 构建增强的系统提示词
        system_prompt = f"""你是{character_name}，{character_description}

请严格按照以下要求进行角色扮演：
1. 完全沉浸在{character_name}的角色中，用第一人称说话
2. 保持角色的性格特点和说话风格
3. 回复要生动有趣，符合角色设定
4. 回复长度控制在100-300字之间
5. 使用中文回复"""

        # 添加用户记忆信息到系统提示词
        if user_memory:
            memory_info = []
            if user_memory.get('total_messages', 0) > 0:
                memory_info.append(f"你与这个用户已经进行了{user_memory['total_messages']}次对话")
            
            if user_memory.get('user_preferences', {}).get('likes'):
                memory_info.append(f"用户喜欢：{', '.join(user_memory['user_preferences']['likes'])}")
            
            if user_memory.get('user_preferences', {}).get('dislikes'):
                memory_info.append(f"用户不喜欢：{', '.join(user_memory['user_preferences']['dislikes'])}")
            
            if memory_info:
                system_prompt += f"\n\n关于这个用户的记忆：\n" + "\n".join(memory_info)
        
        system_prompt += "\n\n现在开始与用户对话："
        
        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加对话历史（如果有的话）
        if conversation_id in conversations and 'messages' in conversations[conversation_id]:
            # 只保留最近的10轮对话，避免token过多
            recent_messages = conversations[conversation_id]['messages'][-20:]  # 10轮对话 = 20条消息
            for msg in recent_messages:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        # 构建请求payload
        payload = {
            "model": OPENAI_MODEL,
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.8,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        }
        
        logger.info(f"调用OpenAI API: {OPENAI_API_URL}/chat/completions")
        logger.info(f"角色: {character_name}")
        logger.info(f"用户消息: {user_message[:50]}...")
        
        response = requests.post(
            f'{OPENAI_API_URL}/chat/completions',
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content'].strip()
            logger.info(f"OpenAI API调用成功，回复: {ai_response[:50]}...")
            return ai_response
        else:
            error_msg = f'OpenAI API调用失败: {response.status_code} - {response.text}'
            logger.error(error_msg)
            raise Exception(error_msg)
            
    except requests.exceptions.Timeout:
        error_msg = '请求超时，请稍后重试'
        logger.error(error_msg)
        raise Exception(error_msg)
    except requests.exceptions.RequestException as e:
        error_msg = f'网络请求失败: {str(e)}'
        logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f'OpenAI API调用错误: {str(e)}'
        logger.error(error_msg)
        raise Exception(error_msg)

@app.route('/api/characters', methods=['GET'])
def get_characters():
    """
    获取可用的角色列表
    """
    return jsonify({
        'success': True,
        'characters': ROLE_LIBRARY
    })

@app.route('/api/characters/<role_id>', methods=['GET'])
def get_character_by_id(role_id):
    """
    根据ID获取特定角色信息
    """
    try:
        role = get_role_by_id(role_id)
        if role:
            return jsonify({
                'success': True,
                'character': role
            })
        else:
            return jsonify({
                'success': False,
                'error': '角色不存在'
            }), 404
    except Exception as e:
        logger.error(f"获取角色信息错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/characters/search', methods=['GET'])
def search_characters():
    """
    搜索角色
    支持按名称、描述、标签搜索
    """
    try:
        query = request.args.get('q', '').lower()
        category = request.args.get('category', '')
        
        filtered_roles = ROLE_LIBRARY
        
        # 按分类筛选
        if category and category != 'all':
            filtered_roles = [role for role in filtered_roles if role['category'] == category]
        
        # 按关键词搜索
        if query:
            filtered_roles = [
                role for role in filtered_roles
                if (query in role['name'].lower() or
                    query in role['description'].lower() or
                    query in role['personality'].lower() or
                    any(query in tag.lower() for tag in role['tags']))
            ]
        
        return jsonify({
            'success': True,
            'characters': filtered_roles,
            'total': len(filtered_roles)
        })
    except Exception as e:
        logger.error(f"搜索角色错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """
    获取所有对话列表
    """
    try:
        user_id = request.args.get('user_id')
        
        if user_id and db:
            # 从数据库获取用户的对话列表
            user_conversations = db.get_user_conversations(user_id)
            return jsonify({
                'success': True,
                'conversations': user_conversations,
                'total': len(user_conversations)
            })
        else:
            # 返回内存中的对话列表
            return jsonify({
                'success': True,
                'conversations': list(conversations.keys()),
                'total': len(conversations)
            })
    except Exception as e:
        logger.error(f"获取对话列表错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """
    删除指定对话
    """
    try:
        success = False
        
        # 从内存中删除
        if conversation_id in conversations:
            del conversations[conversation_id]
            success = True
        
        # 从数据库中删除
        if db:
            db_success = db.delete_conversation(conversation_id)
            success = success or db_success
        
        if success:
            return jsonify({
                'success': True,
                'message': f'对话 {conversation_id} 已删除'
            })
        else:
            return jsonify({
                'success': False,
                'error': '对话不存在'
            }), 404
    except Exception as e:
        logger.error(f"删除对话错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/conversations/character/<character_name>', methods=['GET'])
def get_character_conversations(character_name):
    """
    获取特定角色的对话历史
    """
    try:
        # 查找该角色的所有对话
        character_conversations = []
        for conv_id, conv_data in conversations.items():
            if conv_data.get('character_name') == character_name:
                character_conversations.append({
                    'id': conv_id,
                    'character_name': conv_data.get('character_name'),
                    'character_description': conv_data.get('character_description'),
                    'messages': conv_data.get('messages', []),
                    'created_at': conv_data.get('created_at'),
                    'last_message_time': conv_data.get('messages', [])[-1].get('timestamp') if conv_data.get('messages') else conv_data.get('created_at')
                })
        
        # 按最后消息时间排序，最新的在前
        character_conversations.sort(key=lambda x: x['last_message_time'], reverse=True)
        
        return jsonify({
            'success': True,
            'character_name': character_name,
            'conversations': character_conversations,
            'total': len(character_conversations)
        })
    except Exception as e:
        logger.error(f"获取角色对话历史错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/memory/<user_id>', methods=['GET'])
def get_user_memories(user_id):
    """
    获取用户的所有记忆
    """
    try:
        if not db:
            return jsonify({
                'success': False,
                'error': '数据库不可用'
            }), 500
        
        memories = db.get_user_all_memories(user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'memories': memories,
            'total': len(memories)
        })
    except Exception as e:
        logger.error(f"获取用户记忆错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/memory/<user_id>/<character_name>', methods=['GET'])
def get_user_character_memory(user_id, character_name):
    """
    获取用户与特定角色的记忆
    """
    try:
        if not db:
            return jsonify({
                'success': False,
                'error': '数据库不可用'
            }), 500
        
        memory = db.get_user_memory(user_id, character_name)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'character_name': character_name,
            'memory': memory
        })
    except Exception as e:
        logger.error(f"获取用户角色记忆错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/memory/<user_id>/<character_name>', methods=['POST'])
def save_user_memory(user_id, character_name):
    """
    手动保存用户记忆
    """
    try:
        if not db:
            return jsonify({
                'success': False,
                'error': '数据库不可用'
            }), 500
        
        data = request.get_json()
        memory_data = data.get('memory_data', {})
        
        success = db.save_user_memory(user_id, character_name, memory_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': '记忆保存成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '记忆保存失败'
            }), 500
    except Exception as e:
        logger.error(f"保存用户记忆错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/database/stats', methods=['GET'])
def get_database_stats():
    """
    获取数据库统计信息
    """
    try:
        if not db:
            return jsonify({
                'success': False,
                'error': '数据库不可用'
            }), 500
        
        stats = db.get_database_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"获取数据库统计信息错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/database/cleanup', methods=['POST'])
def cleanup_old_conversations():
    """
    清理旧的对话记录
    """
    try:
        if not db:
            return jsonify({
                'success': False,
                'error': '数据库不可用'
            }), 500
        
        data = request.get_json()
        days = data.get('days', 30)
        
        deleted_count = db.cleanup_old_conversations(days)
        
        return jsonify({
            'success': True,
            'message': f'清理完成，删除了 {deleted_count} 条旧对话记录',
            'deleted_count': deleted_count
        })
    except Exception as e:
        logger.error(f"清理旧对话记录错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    健康检查端点
    """
    db_status = "connected" if db else "disconnected"
    db_stats = db.get_database_stats() if db else {}
    
    return jsonify({
        'status': 'healthy',
        'message': 'AI角色扮演平台后端服务运行正常',
        'openai_api_url': OPENAI_API_URL,
        'openai_model': OPENAI_MODEL,
        'openai_api_key_configured': bool(OPENAI_API_KEY and OPENAI_API_KEY != 'your-openai-api-key'),
        'active_conversations': len(conversations),
        'total_roles': len(ROLE_LIBRARY),
        'database_status': db_status,
        'database_stats': db_stats,
        'features': {
            'voice_transcription': True,
            'role_management': True,
            'character_chat': True,
            'conversation_history': True,
            'direct_openai_integration': True,
            'persistent_storage': bool(db),
            'user_memory': bool(db)
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 启动AI角色扮演平台后端服务...")
    print("=" * 60)
    print(f"🤖 OpenAI API URL: {OPENAI_API_URL}")
    print(f"🧠 OpenAI Model: {OPENAI_MODEL}")
    print(f"🔑 OpenAI API Key 已配置: {'✅' if OPENAI_API_KEY and OPENAI_API_KEY != 'your-openai-api-key' else '❌'}")
    print(f"👥 角色库数量: {len(ROLE_LIBRARY)}")
    print("=" * 60)
    print("📋 可用的API端点:")
    print("  • POST /api/chat - 与AI角色对话")
    print("  • POST /api/voice/transcribe - 语音转文本")
    print("  • POST /api/voice/synthesize - 文本转语音")
    print("  • GET  /api/characters - 获取角色列表")
    print("  • GET  /api/characters/<id> - 获取特定角色")
    print("  • GET  /api/characters/search - 搜索角色")
    print("  • GET  /api/conversations - 获取对话列表")
    print("  • GET  /api/conversations/character/<name> - 获取特定角色对话历史")
    print("  • DELETE /api/conversations/<id> - 删除对话")
    print("  • GET  /api/memory/<user_id> - 获取用户所有记忆")
    print("  • GET  /api/memory/<user_id>/<character_name> - 获取用户角色记忆")
    print("  • POST /api/memory/<user_id>/<character_name> - 保存用户记忆")
    print("  • GET  /api/database/stats - 获取数据库统计信息")
    print("  • POST /api/database/cleanup - 清理旧对话记录")
    print("  • GET  /api/health - 健康检查")
    print("=" * 60)
    print(f"🗄️  MongoDB状态: {'✅ 已连接' if db else '❌ 未连接'}")
    if db:
        try:
            stats = db.get_database_stats()
            print(f"📊 数据库统计: {stats.get('conversations_count', 0)} 对话, {stats.get('user_memories_count', 0)} 记忆")
        except:
            pass
    print("=" * 60)
    print("🌐 请在浏览器中访问 http://localhost:5000/api/health 检查服务状态")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
