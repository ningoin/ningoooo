# Dify角色扮演器

一个基于Dify API的智能角色扮演对话系统，支持语音输入和多种角色选择。

## 功能特性

- 🎭 **多角色扮演**: 支持多种预设角色，每个角色都有独特的性格和对话风格
- 🎤 **语音输入**: 支持语音转文字功能，使用OpenAI Whisper API
- 💬 **智能对话**: 基于Dify API的智能对话系统
- 🎨 **现代UI**: 美观的用户界面，支持响应式设计
- 🔧 **易于配置**: 简单的配置流程，支持环境变量

## 项目结构

```
├── app.py                 # Python Flask后端服务
├── requirements.txt       # Python依赖包
├── config.env.example     # 环境变量配置示例
├── 0.1版本.html          # 前端HTML文件
└── README.md             # 使用说明
```

## 安装和配置

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `config.env.example` 为 `.env` 并填入您的配置：

```bash
cp config.env.example .env
```

编辑 `.env` 文件：

```env
# Dify API配置
DIFY_API_URL=https://your-dify-app-url.com/chat-messages
DIFY_API_KEY=your-dify-api-key

# 服务器配置
FLASK_ENV=development
FLASK_DEBUG=True
```

### 3. 启动后端服务

```bash
python app.py
```

后端服务将在 `http://localhost:5000` 启动。

### 4. 打开前端页面

在浏览器中打开 `0.1版本.html` 文件。

## 使用说明

### 基本对话

1. 在HTML页面中选择一个角色
2. 在输入框中输入消息或点击麦克风按钮进行语音输入
3. 系统会将您的消息发送给Dify API，获取AI回复

### 语音输入

1. 点击麦克风按钮开始录音
2. 说话后再次点击停止录音
3. 系统会自动将语音转换为文字并发送给AI

### 角色选择

系统预设了以下角色：
- 🤖 **小助手**: 友善、乐于助人的AI助手
- 👨‍🏫 **老师**: 经验丰富的老师，善于解释复杂概念
- 👫 **朋友**: 真诚的朋友，愿意倾听并提供建议
- 🎭 **喜剧演员**: 幽默风趣，总是能逗人开心

## API接口

### 后端API端点

- `POST /api/chat` - 发送消息给Dify角色扮演器
- `GET /api/characters` - 获取可用角色列表
- `GET /api/health` - 健康检查

### 请求示例

```javascript
// 发送消息
fetch('http://localhost:5000/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: '你好',
    character_name: '小助手',
    character_description: '你是一个友善的AI助手'
  })
});
```

## 配置说明

### Dify API配置

1. 在Dify平台创建您的应用
2. 获取API URL和API Key
3. 在 `.env` 文件中配置这些信息

### OpenAI API配置

语音转文字功能需要OpenAI API Key：
1. 在HTML页面的设置中输入您的OpenAI API Key
2. 确保您的API Key有Whisper API的访问权限

## 故障排除

### 常见问题

1. **后端服务无法启动**
   - 检查Python版本（需要3.7+）
   - 确认所有依赖包已正确安装
   - 检查端口5000是否被占用

2. **前端无法连接后端**
   - 确认后端服务正在运行
   - 检查防火墙设置
   - 确认URL配置正确

3. **Dify API调用失败**
   - 检查API URL和Key是否正确
   - 确认Dify应用配置正确
   - 查看后端日志获取详细错误信息

4. **语音转文字失败**
   - 检查OpenAI API Key是否正确
   - 确认网络连接正常
   - 检查麦克风权限

### 日志查看

后端服务会在控制台输出详细日志，包括：
- API调用状态
- 错误信息
- 请求详情

## 开发说明

### 添加新角色

1. 在 `app.py` 的 `get_characters()` 函数中添加新角色
2. 在HTML前端更新角色选择界面

### 自定义Dify集成

修改 `app.py` 中的 `call_dify_api()` 函数来适配您的Dify应用配置。

### 前端定制

HTML文件包含了完整的CSS和JavaScript，您可以根据需要修改样式和功能。

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。