# 校园网自动登录程序

一个用于自动连接校园网的Python程序，支持开机自动登录。

## 功能特性

- ✅ 支持多种校园网认证方式（锐捷、Dr.COM、深澜等）
- ✅ 开机自动登录（通过Windows任务计划程序）
- ✅ 网络连接检测和等待
- ✅ 登录失败自动重试
- ✅ 详细的日志记录
- ✅ 配置文件支持

## 系统要求

- Windows 10/11
- Python 3.7+
- 管理员权限（用于创建任务计划程序）

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/your-username/campus-network-auto-login.git
cd campus-network-auto-login
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置账号信息

首次运行程序时会自动进入设置向导，引导你填写账号信息。

或者手动复制 `config.py.example` 为 `config.py`，修改以下配置：

```python
# 校园网认证服务器地址
auth_server: str = "172.16.4.14"

# 账号 (请替换为你的校园网账号)
username: str = "YOUR_USERNAME"

# 密码 (请替换为你的校园网密码)
password: str = "YOUR_PASSWORD"

# 运营商选择 (中国移动)
isp: int = 2

# 运营商名称
isp_name: str = "中国移动"
```

配置完成后运行程序会自动生成 `config.json` 配置文件。

### 4. 测试登录

```bash
python main.py
```

### 5. 设置开机自动登录

```bash
python scheduler.py
```

**注意：** 需要以管理员身份运行，程序会自动请求提升权限。

## 使用方法

### 手动登录

```bash
python main.py
```

### 设置开机自动登录

```bash
python scheduler.py
```

### 管理任务计划程序

```bash
# 查看任务状态
schtasks /query /tn CampusNetworkAutoLogin

# 手动运行任务
schtasks /run /tn CampusNetworkAutoLogin

# 删除任务
schtasks /delete /tn CampusNetworkAutoLogin /f
```

## 配置文件说明

程序会自动生成 `config.json` 配置文件：

```json
{
  "auth_server": "172.16.4.14",
  "username": "YOUR_USERNAME",
  "password": "YOUR_PASSWORD",
  "isp": 2,
  "isp_name": "中国移动",
  "login_url": "http://172.16.4.14",
  "login_path": "/login",
  "max_retries": 3,
  "retry_interval": 5,
  "network_timeout": 60
}
```

### 运营商代码对照表

| 运营商 | 代码 |
|--------|------|
| 校园网 | 1 |
| 中国移动 | 2 |
| 中国联通 | 3 |
| 中国电信 | 4 |

## 文件说明

```
campus-network-auto-login/
├── main.py              # 主程序
├── config.py            # 配置文件
├── login.py             # 登录模块
├── scheduler.py         # 任务计划程序配置
├── requirements.txt     # 依赖列表
├── config.json          # 运行时生成的配置文件
├── campus_network.log   # 日志文件
├── start_login.bat      # 启动批处理（自动生成）
└── start_login_silent.vbs  # 静默启动脚本（自动生成）
```

## 故障排除

### 1. 登录失败

- 检查账号密码是否正确
- 确认运营商选择是否正确
- 查看日志文件 `campus_network.log`

### 2. 无法创建任务计划程序

- 确保以管理员身份运行
- 检查Windows任务计划程序服务是否正常

### 3. 网络连接超时

- 检查网线是否连接
- 确认IP地址设置是否正确
- 尝试手动访问 `http://172.16.4.14`

### 4. 日志文件位置

日志文件保存在程序运行目录：`campus_network.log`

## 注意事项

1. **密码安全**：配置文件中包含明文密码，请妥善保管
2. **网络环境**：确保在校园网环境中使用
3. **管理员权限**：设置开机自启需要管理员权限
4. **防火墙**：确保Python程序可以访问网络

## 开发说明

### 支持的认证系统

- 锐捷认证系统
- Dr.COM认证系统
- 深澜认证系统
- 通用Web认证系统

### 扩展认证方式

如需支持其他认证系统，请在 `login.py` 中添加新的认证方法：

```python
def try_custom_auth(self):
    """自定义认证方式"""
    # 实现认证逻辑
    pass
```

然后在 `login()` 方法中调用。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题，请提交Issue。
