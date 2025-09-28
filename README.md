# AI角色扮演平台

一个功能丰富的AI角色扮演对话系统，支持多种角色、语音交互、对话历史管理等功能。基于Flask后端和现代化前端界面构建。

## 功能特性

- 🎭 **丰富的角色库**: 内置30+预设角色，涵盖游戏、电影、历史等各个领域
- 🎤 **语音交互**: 支持语音转文本（Whisper API）和文本转语音（TTS API）
- 💬 **智能对话**: 基于OpenAI GPT模型的智能对话系统
- 🎨 **现代化界面**: 响应式设计，美观易用的用户界面
- 🔧 **自定义角色**: 支持创建、编辑、删除自定义角色
- 📝 **对话历史**: 持久化存储对话记录，支持历史查看和管理
- 🖼️ **头像管理**: 支持角色头像上传和管理
- 🔍 **角色搜索**: 支持按名称、描述、标签搜索角色
- 📊 **数据管理**: 文件存储系统，支持数据备份和恢复

## 项目结构

```
├── app.py                    # Flask后端主服务
├── requirements.txt          # Python依赖包
├── config.env               # 环境变量配置
├── 0.1版本.html             # 前端HTML文件
├── data/                    # 数据存储目录
│   ├── data_manager.py      # 数据管理模块
│   ├── conversations.json   # 对话记录存储
│   ├── custom_roles.json    # 自定义角色存储
│   ├── backup/              # 数据备份目录
│   └── pic/                 # 角色头像存储
└── README.md                # 项目说明文档
```

## 安装和配置

### 1. 环境要求

- Python 3.7+
- 现代浏览器（支持Web Audio API）

### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

编辑 `config.env` 文件，配置OpenAI API：

```env
# OpenAI API配置
OPENAI_API_KEY=your-openai-api-key
OPENAI_API_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo

# 服务器配置
FLASK_ENV=development
FLASK_DEBUG=True
```

**重要说明**：
- 需要有效的OpenAI API Key
- 支持自定义API URL（如使用代理服务）
- 语音功能需要Whisper和TTS API权限

### 4. 启动后端服务

```bash
python app.py
```

后端服务将在 `http://localhost:5000` 启动。

### 5. 打开前端页面

在浏览器中打开 `0.1版本.html` 文件，即可开始使用。

## 使用说明

### 基本对话

1. **选择角色**: 在侧边栏选择预设角色或自定义角色
2. **发送消息**: 在输入框中输入文字消息
3. **语音输入**: 点击麦克风按钮进行语音输入
4. **查看回复**: AI角色会根据设定性格回复消息

### 语音交互

1. **语音转文本**: 点击麦克风按钮开始录音，再次点击停止
2. **文本转语音**: 点击播放按钮听取AI回复的语音版本
3. **语音设置**: 不同角色使用不同的声音配置

### 角色管理

#### 预设角色
系统内置30+角色，包括：
- **游戏角色**: 星穹铁道、哈利·波特等
- **电影角色**: 漫威超级英雄系列
- **历史人物**: 苏格拉底等哲学家
- **其他角色**: 各种有趣的角色设定

#### 自定义角色
1. **创建角色**: 点击"创建角色"按钮
2. **设置信息**: 填写角色名称、描述、性格等
3. **上传头像**: 支持PNG、JPG等格式
4. **保存使用**: 创建后即可在对话中使用

### 对话历史

- **查看历史**: 侧边栏显示所有对话记录
- **继续对话**: 点击历史对话可继续之前的对话
- **删除对话**: 支持删除不需要的对话记录

## API接口

### 核心API端点

#### 对话相关
- `POST /api/chat` - 与AI角色进行对话
- `GET /api/conversations` - 获取所有对话列表
- `GET /api/conversations/<id>` - 获取指定对话详情
- `DELETE /api/conversations/<id>` - 删除对话

#### 角色管理
- `GET /api/characters` - 获取所有角色列表
- `GET /api/characters/<id>` - 获取特定角色信息
- `GET /api/characters/search` - 搜索角色
- `POST /api/characters/custom` - 创建自定义角色
- `PUT /api/characters/custom/<id>` - 更新自定义角色
- `DELETE /api/characters/custom/<id>` - 删除自定义角色

#### 语音功能
- `POST /api/voice/transcribe` - 语音转文本
- `POST /api/voice/synthesize` - 文本转语音

#### 系统功能
- `GET /api/health` - 健康检查
- `GET /api/avatar/<filename>` - 获取头像图片

### 请求示例

```javascript
// 发送对话消息
fetch('http://localhost:5000/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: '你好，哈利！',
    character_name: '哈利·波特',
    character_description: '霍格沃茨魔法学校的学生',
    role_id: 'harry-potter',
    conversation_id: 'optional-conversation-id'
  })
});

// 创建自定义角色
const formData = new FormData();
formData.append('name', '我的角色');
formData.append('description', '角色描述');
formData.append('personality', '角色性格');
formData.append('avatar', avatarFile);

fetch('http://localhost:5000/api/characters/custom', {
  method: 'POST',
  body: formData
});

// 语音转文本
const audioFormData = new FormData();
audioFormData.append('file', audioFile);
audioFormData.append('role_id', 'harry-potter');

fetch('http://localhost:5000/api/voice/transcribe', {
  method: 'POST',
  body: audioFormData
});
```

## 配置说明

### OpenAI API配置

1. **获取API Key**: 在OpenAI官网注册并获取API Key
2. **配置权限**: 确保API Key具有以下权限：
   - Chat Completions API
   - Whisper API（语音转文本）
   - TTS API（文本转语音）
3. **设置配额**: 根据使用量设置合适的API配额

### 自定义API URL

支持使用代理服务或自部署的OpenAI兼容API：
```env
OPENAI_API_URL=https://your-proxy-url.com/v1
```

### 数据存储

- **对话记录**: 存储在 `data/conversations.json`
- **自定义角色**: 存储在 `data/custom_roles.json`
- **角色头像**: 存储在 `data/pic/` 目录
- **数据备份**: 自动备份到 `data/backup/` 目录

## 故障排除

### 常见问题

1. **后端服务无法启动**
   - 检查Python版本（需要3.7+）
   - 确认所有依赖包已正确安装：`pip install -r requirements.txt`
   - 检查端口5000是否被占用
   - 确认 `config.env` 文件存在且配置正确

2. **前端无法连接后端**
   - 确认后端服务正在运行（访问 `http://localhost:5000/api/health`）
   - 检查浏览器控制台是否有CORS错误
   - 确认防火墙设置允许本地连接

3. **OpenAI API调用失败**
   - 检查API Key是否正确且有效
   - 确认API URL配置正确
   - 检查网络连接和代理设置
   - 查看后端日志获取详细错误信息

4. **语音功能异常**
   - 检查浏览器是否支持Web Audio API
   - 确认麦克风权限已授予
   - 检查OpenAI API Key是否有Whisper和TTS权限
   - 确认音频文件格式正确

5. **角色头像显示异常**
   - 检查图片文件是否存在
   - 确认图片格式支持（PNG、JPG、JPEG、GIF、WEBP）
   - 检查文件权限设置

### 日志查看

后端服务会在控制台输出详细日志，包括：
- API调用状态和响应
- 错误信息和堆栈跟踪
- 请求详情和参数
- 数据操作记录

### 数据恢复

如果数据文件损坏，可以从备份恢复：
```bash
# 查看备份文件
ls data/backup/

# 手动恢复（需要修改data_manager.py）
```

## 开发说明

### 添加新预设角色

1. 在 `app.py` 的 `ROLE_LIBRARY` 列表中添加新角色
2. 添加对应的头像图片到 `data/pic/` 目录
3. 在 `call_openai_api()` 函数中添加角色的系统提示词

### 自定义前端界面

- 修改 `0.1版本.html` 中的CSS样式
- 调整JavaScript逻辑以适配新的API端点
- 添加新的UI组件和交互功能

### 扩展API功能

- 在 `app.py` 中添加新的路由和端点
- 在 `data_manager.py` 中添加新的数据操作方法
- 更新前端JavaScript以调用新的API

### 部署到生产环境

1. **环境配置**:
   ```env
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

2. **使用生产级WSGI服务器**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **配置反向代理**（如Nginx）:
   ```nginx
   location / {
       proxy_pass http://localhost:5000;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

## 技术栈

- **后端**: Flask + Python
- **前端**: HTML5 + CSS3 + JavaScript
- **AI服务**: OpenAI GPT + Whisper + TTS
- **数据存储**: JSON文件存储
- **语音处理**: Web Audio API

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

### 贡献指南

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 提交Pull Request

## 更新日志

### v0.1.0
- 初始版本发布
- 支持多角色对话
- 集成语音交互功能
- 实现自定义角色管理
- 添加对话历史功能