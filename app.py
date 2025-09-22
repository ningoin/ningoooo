from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import json
import os
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 配置OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY', '')

# 角色配置
CHARACTERS = {
    'harry-potter': {
        'name': '哈利·波特',
        'description': '来自魔法世界的勇敢巫师，霍格沃茨的学生',
        'system_prompt': '''你是哈利·波特，来自J.K.罗琳的魔法世界。你是一个勇敢、善良的年轻巫师，在霍格沃茨魔法学校学习。你总是愿意帮助朋友，对魔法世界充满好奇，并且有强烈的正义感。

请用友好、勇敢的语气与用户对话，分享你的魔法经历和冒险故事。你可以：
1. 知识问答：回答关于魔法世界、咒语、魔法生物等问题
2. 情感支持：给予勇气和鼓励，分享友谊的重要性
3. 创意写作：帮助创作魔法故事，提供创意灵感
4. 冒险指导：分享冒险经验，给出勇敢的建议

请保持角色的真实性和一致性，用第一人称说话。'''
    },
    'sherlock-holmes': {
        'name': '夏洛克·福尔摩斯',
        'description': '世界著名的侦探，拥有敏锐的观察力和推理能力',
        'system_prompt': '''你是夏洛克·福尔摩斯，世界上最著名的侦探。你拥有敏锐的观察力、强大的推理能力和对细节的极致关注。

请用冷静、理性的语气与用户对话，帮助他们分析问题并找到解决方案。你可以：
1. 推理分析：帮助分析复杂问题，提供逻辑推理
2. 观察技巧：教授观察和分析的方法
3. 逻辑思维：引导用户进行逻辑思考
4. 案件解决：协助解决各种"案件"和问题

请保持角色的专业性和逻辑性，用第一人称说话。'''
    },
    'socrates': {
        'name': '苏格拉底',
        'description': '古希腊哲学家，以苏格拉底式问答法闻名',
        'system_prompt': '''你是苏格拉底，古希腊最著名的哲学家之一。你以苏格拉底式问答法闻名，通过不断提问来引导人们思考真理。

请用智慧、好奇的语气与用户对话，通过提问来引导他们深入思考。你可以：
1. 哲学思辨：进行深度的哲学讨论和思考
2. 苏格拉底式问答：通过提问引导用户思考
3. 智慧引导：分享人生智慧和哲学见解
4. 真理探索：帮助用户探索真理和知识

请保持角色的智慧性和引导性，用第一人称说话。'''
    },
    'confucius': {
        'name': '孔子',
        'description': '中国古代思想家、教育家，儒家学派创始人',
        'system_prompt': '''你是孔子，中国古代最伟大的思想家和教育家，儒家学派的创始人。你强调仁爱、礼仪、智慧和道德修养。

请用温和、智慧的语气与用户对话，分享你的人生哲学和教育理念。你可以：
1. 道德教育：教授道德修养和人生道理
2. 人生智慧：分享人生经验和智慧
3. 礼仪指导：指导正确的行为举止
4. 学习建议：提供学习和教育的方法

请保持角色的温和性和智慧性，用第一人称说话。'''
    },
    'ai-assistant': {
        'name': 'AI助手',
        'description': '智能AI助手，具备多种技能',
        'system_prompt': '''你是一个友好的AI助手，具备广泛的知识和多种技能。你乐于帮助用户解决问题，提供信息，进行创意写作，并给予情感支持。

你可以：
1. 知识问答：回答各种知识问题
2. 创意写作：协助创作故事、诗歌、文章等
3. 情感支持：提供情感安慰和建议
4. 学习辅导：帮助学习和理解各种知识

请用友好、专业的语气与用户对话，根据他们的需求提供最合适的帮助。'''
    }
}

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/voice-test')
def voice_test():
    """语音功能测试页面"""
    return render_template('voice_test.html')

@app.route('/api/characters', methods=['GET'])
def get_characters():
    """获取所有角色列表"""
    return jsonify({
        'success': True,
        'characters': CHARACTERS
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        data = request.get_json()
        character_id = data.get('character_id')
        message = data.get('message')
        chat_history = data.get('chat_history', [])
        
        if not character_id or not message:
            return jsonify({
                'success': False,
                'error': '缺少必要参数'
            }), 400
        
        if character_id not in CHARACTERS:
            return jsonify({
                'success': False,
                'error': '角色不存在'
            }), 400
        
        # 获取角色信息
        character = CHARACTERS[character_id]
        
        # 构建对话历史
        messages = [{"role": "system", "content": character['system_prompt']}]
        
        # 添加历史对话
        for msg in chat_history[-10:]:  # 只保留最近10条对话
            if msg['sender'] == 'user':
                messages.append({"role": "user", "content": msg['content']})
            else:
                messages.append({"role": "assistant", "content": msg['content']})
        
        # 添加当前消息
        messages.append({"role": "user", "content": message})
        
        # 调用OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
            temperature=0.8,
            stream=False
        )
        
        ai_response = response.choices[0].message.content
        
        # 记录日志
        logger.info(f"Character: {character_id}, Message: {message[:50]}...")
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'character': character['name']
        })
        
    except openai.error.AuthenticationError:
        return jsonify({
            'success': False,
            'error': 'API密钥无效，请在设置中配置正确的OpenAI API密钥'
        }), 401
    except openai.error.RateLimitError:
        return jsonify({
            'success': False,
            'error': 'API请求频率过高，请稍后重试'
        }), 429
    except openai.error.APIError as e:
        return jsonify({
            'success': False,
            'error': f'OpenAI API错误: {str(e)}'
        }), 500
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500

@app.route('/api/character-skills', methods=['POST'])
def get_character_skills():
    """获取角色技能演示"""
    try:
        data = request.get_json()
        character_id = data.get('character_id')
        skill_type = data.get('skill_type')  # knowledge, emotion, creative
        
        if not character_id or not skill_type:
            return jsonify({
                'success': False,
                'error': '缺少必要参数'
            }), 400
        
        if character_id not in CHARACTERS:
            return jsonify({
                'success': False,
                'error': '角色不存在'
            }), 400
        
        character = CHARACTERS[character_id]
        
        # 根据技能类型生成不同的演示
        skill_prompts = {
            'knowledge': f"作为{character['name']}，请展示你的知识问答技能，回答一个关于你专业领域的问题。",
            'emotion': f"作为{character['name']}，请展示你的情感支持技能，给用户一些鼓励和建议。",
            'creative': f"作为{character['name']}，请展示你的创意写作技能，创作一个简短的故事或诗歌。"
        }
        
        messages = [
            {"role": "system", "content": character['system_prompt']},
            {"role": "user", "content": skill_prompts[skill_type]}
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=300,
            temperature=0.9
        )
        
        skill_demo = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'skill_demo': skill_demo,
            'skill_type': skill_type
        })
        
    except Exception as e:
        logger.error(f"Skill demo error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # 检查API密钥
    if not openai.api_key:
        print("警告: 未设置OPENAI_API_KEY环境变量")
        print("请在设置中配置API密钥或设置环境变量")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
