# AI角色扮演平台 - TTS语音合成功能

## 功能概述

现在AI角色扮演平台已经支持完整的语音对话功能：

1. **语音输入** - 用户可以通过麦克风录音，系统自动转换为文本
2. **AI文本回复** - AI角色根据用户输入生成文本回复
3. **语音输出** - AI的文本回复自动转换为语音播放

## 新增功能

### 后端TTS API

- **端点**: `POST /api/voice/synthesize`
- **功能**: 将文本转换为语音
- **参数**:
  - `text`: 要转换的文本内容
  - `voice`: 语音类型 (alloy, echo, fable, onyx, nova, shimmer)
  - `model`: TTS模型 (tts-1, tts-1-hd)

### 前端语音控制

- **TTS开关按钮**: 用户可以控制是否播放AI的语音回复
- **自动播放**: AI回复后自动播放语音
- **静默模式**: 关闭TTS后只显示文本，不播放语音

## 使用方法

### 1. 启动后端服务

```bash
# 安装依赖
pip install -r requirements.txt

# 配置API密钥
cp config.env.example config.env
# 编辑 config.env 文件，填入你的OpenAI API密钥

# 启动服务
python app.py
```

### 2. 打开前端页面

在浏览器中打开 `0.1版本.html` 文件

### 3. 语音对话流程

1. **选择角色**: 在角色库中选择一个AI角色
2. **语音输入**: 点击麦克风按钮开始录音，说话后再次点击停止
3. **AI回复**: 系统自动将语音转为文本，发送给AI角色
4. **语音播放**: AI的文本回复自动转换为语音播放
5. **控制播放**: 使用音量按钮控制是否播放AI语音

## 技术实现

### 后端技术栈

- **Flask**: Web框架
- **OpenAI TTS API**: 文本转语音服务
- **OpenAI Whisper API**: 语音转文本服务
- **OpenAI GPT API**: AI对话服务

### 前端技术栈

- **原生JavaScript**: 处理音频播放和用户交互
- **Web Audio API**: 音频录制和处理
- **Fetch API**: 与后端API通信

## API端点列表

```
POST /api/chat - 与AI角色对话
POST /api/voice/transcribe - 语音转文本
POST /api/voice/synthesize - 文本转语音 (新增)
GET  /api/characters - 获取角色列表
GET  /api/characters/<id> - 获取特定角色
GET  /api/characters/search - 搜索角色
GET  /api/conversations - 获取对话列表
DELETE /api/conversations/<id> - 删除对话
GET  /api/health - 健康检查
```

## 测试方法

运行测试脚本验证TTS功能：

```bash
python test_tts.py
```

## 注意事项

1. **API密钥**: 确保在 `config.env` 中正确配置OpenAI API密钥
2. **网络连接**: 需要稳定的网络连接访问OpenAI API
3. **浏览器权限**: 首次使用需要允许浏览器访问麦克风
4. **音频格式**: TTS生成的音频格式为MP3
5. **文本长度**: 建议AI回复文本不要过长，以确保良好的语音合成效果

## 故障排除

### 常见问题

1. **TTS不播放**: 检查TTS开关是否开启，查看浏览器控制台错误信息
2. **录音失败**: 检查浏览器麦克风权限设置
3. **API调用失败**: 检查网络连接和API密钥配置
4. **音频播放失败**: 检查浏览器音频权限和音频格式支持

### 调试方法

1. 打开浏览器开发者工具查看控制台日志
2. 检查后端服务日志输出
3. 使用测试脚本验证API功能
4. 检查网络请求和响应状态

## 未来改进

- [ ] 支持更多语音类型和语言
- [ ] 添加语音速度控制
- [ ] 实现语音情感表达
- [ ] 支持自定义角色语音
- [ ] 添加语音历史记录功能
