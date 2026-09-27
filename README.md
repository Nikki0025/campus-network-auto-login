# 校园网自动登录程序

自动连接校园网（Dr.COM 认证），支持开机自动登录。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行（首次会引导设置账号）
python main.py
```

## 开机自动登录

程序通过 Windows 启动文件夹实现自启，无需管理员权限：

1. 运行一次 `python main.py` 完成设置
2. 将 `start_login_silent.vbs` 的快捷方式放入启动文件夹：
   ```
   %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\
   ```

取消自启：删除启动文件夹中的 `CampusNetworkAutoLogin.vbs` 即可。

## 配置文件

`config.json`（首次运行自动生成）：

```json
{
  "auth_server": "172.16.4.14",
  "username": "你的学号",
  "password": "你的密码",
  "isp": 2
}
```

| ISP 代码 | 运营商 |
|----------|--------|
| 1 | 校园网 |
| 2 | 中国移动 |
| 3 | 中国联通 |
| 4 | 中国电信 |

## 文件说明

```
├── main.py              # 主程序
├── config.py            # 配置管理
├── login.py             # Dr.COM 登录模块
├── config.json          # 账号配置（不提交）
├── start_login_silent.vbs  # 静默启动脚本
├── campus_network.log   # 运行日志（不提交）
└── requirements.txt     # 依赖
```
