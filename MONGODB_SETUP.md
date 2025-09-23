# MongoDB 安装和配置指南

## 🍃 MongoDB 安装

### Windows 系统

1. **下载MongoDB Community Server**
   - 访问 [MongoDB官网](https://www.mongodb.com/try/download/community)
   - 选择 Windows 版本下载

2. **安装MongoDB**
   - 运行下载的安装程序
   - 选择 "Complete" 安装类型
   - 勾选 "Install MongoDB as a Service"
   - 勾选 "Install MongoDB Compass" (可选，图形界面工具)

3. **启动MongoDB服务**
   ```bash
   # 方法1: 通过服务管理器
   # 打开"服务"应用，找到"MongoDB"服务并启动
   
   # 方法2: 通过命令行
   net start MongoDB
   ```

### macOS 系统

1. **使用Homebrew安装**
   ```bash
   # 安装Homebrew (如果还没有)
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # 安装MongoDB
   brew tap mongodb/brew
   brew install mongodb-community
   
   # 启动MongoDB服务
   brew services start mongodb/brew/mongodb-community
   ```

2. **手动安装**
   - 下载macOS版本的MongoDB Community Server
   - 解压并移动到 `/usr/local/mongodb`
   - 创建数据目录: `sudo mkdir -p /usr/local/var/mongodb`
   - 创建日志目录: `sudo mkdir -p /usr/local/var/log/mongodb`
   - 启动服务: `mongod --dbpath /usr/local/var/mongodb --logpath /usr/local/var/log/mongodb/mongo.log --fork`

### Linux 系统

1. **Ubuntu/Debian**
   ```bash
   # 导入MongoDB公钥
   wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
   
   # 添加MongoDB仓库
   echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
   
   # 更新包列表并安装
   sudo apt-get update
   sudo apt-get install -y mongodb-org
   
   # 启动MongoDB服务
   sudo systemctl start mongod
   sudo systemctl enable mongod
   ```

2. **CentOS/RHEL**
   ```bash
   # 创建MongoDB仓库文件
   sudo vi /etc/yum.repos.d/mongodb-org-6.0.repo
   
   # 添加以下内容:
   [mongodb-org-6.0]
   name=MongoDB Repository
   baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/6.0/x86_64/
   gpgcheck=1
   enabled=1
   gpgkey=https://www.mongodb.org/static/pgp/server-6.0.asc
   
   # 安装MongoDB
   sudo yum install -y mongodb-org
   
   # 启动服务
   sudo systemctl start mongod
   sudo systemctl enable mongod
   ```

## 🔧 配置验证

### 1. 检查MongoDB服务状态

**Windows:**
```bash
# 检查服务状态
sc query MongoDB

# 或者通过服务管理器查看
```

**macOS/Linux:**
```bash
# 检查服务状态
sudo systemctl status mongod

# 或者
brew services list | grep mongodb
```

### 2. 测试连接

```bash
# 连接到MongoDB
mongosh

# 或者使用旧版本命令
mongo
```

如果连接成功，你会看到类似这样的输出：
```
Current Mongosh Log ID: 64f1a2b3c4d5e6f7g8h9i0j1
Connecting to:          mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.10.6
Using MongoDB:          6.0.9
Using Mongosh:          1.10.6
```

### 3. 创建数据库和用户（可选）

```javascript
// 切换到admin数据库
use admin

// 创建管理员用户
db.createUser({
  user: "admin",
  pwd: "password",
  roles: ["userAdminAnyDatabase", "dbAdminAnyDatabase", "readWriteAnyDatabase"]
})

// 切换到项目数据库
use ai_chat_system

// 创建应用用户
db.createUser({
  user: "chat_app",
  pwd: "chat_password",
  roles: ["readWrite"]
})
```

## ⚙️ 项目配置

### 1. 更新config.env文件

```env
# MongoDB数据库配置
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=ai_chat_system

# 如果启用了认证，使用以下格式:
# MONGODB_URI=mongodb://chat_app:chat_password@localhost:27017/ai_chat_system
```

### 2. 安装Python依赖

```bash
# 安装依赖
python install_dependencies.py

# 或者手动安装
pip install -r requirements.txt
```

### 3. 启动应用

```bash
python app.py
```

## 🔍 故障排除

### 常见问题

1. **连接被拒绝**
   - 确保MongoDB服务正在运行
   - 检查端口27017是否被占用
   - 验证防火墙设置

2. **认证失败**
   - 检查用户名和密码
   - 确认用户有正确的权限
   - 验证数据库名称

3. **权限错误**
   - 确保MongoDB数据目录有正确的权限
   - 检查日志文件权限

### 日志查看

**Windows:**
```bash
# 查看MongoDB日志
type "C:\Program Files\MongoDB\Server\6.0\log\mongod.log"
```

**macOS/Linux:**
```bash
# 查看MongoDB日志
sudo tail -f /var/log/mongodb/mongod.log

# 或者
tail -f /usr/local/var/log/mongodb/mongo.log
```

## 📊 数据库管理工具

### MongoDB Compass
- 官方图形界面工具
- 下载地址: https://www.mongodb.com/products/compass

### Studio 3T
- 第三方MongoDB管理工具
- 下载地址: https://studio3t.com/

### 命令行工具
```bash
# 查看所有数据库
show dbs

# 切换到数据库
use ai_chat_system

# 查看集合
show collections

# 查看文档
db.conversations.find().limit(5)
```

## 🚀 性能优化

### 1. 索引优化
项目会自动创建以下索引：
- `user_id + created_at` - 用户对话查询
- `character_name + created_at` - 角色对话查询
- `conversation_id` - 对话ID查询

### 2. 数据清理
```bash
# 清理30天前的对话记录
curl -X POST http://localhost:5000/api/database/cleanup \
  -H "Content-Type: application/json" \
  -d '{"days": 30}'
```

### 3. 监控
```bash
# 查看数据库统计信息
curl http://localhost:5000/api/database/stats
```

## 📝 注意事项

1. **数据备份**: 定期备份MongoDB数据
2. **安全设置**: 生产环境请启用认证和SSL
3. **资源监控**: 监控MongoDB的内存和磁盘使用
4. **版本兼容**: 确保MongoDB版本与pymongo驱动兼容

## 🆘 获取帮助

如果遇到问题，可以：
1. 查看MongoDB官方文档: https://docs.mongodb.com/
2. 检查项目日志输出
3. 使用MongoDB社区论坛: https://community.mongodb.com/
