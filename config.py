#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
"""

import os
import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """配置类"""
    # 校园网认证服务器地址
    auth_server: str = "172.16.4.14"

    # 账号 (运行时从 config.json 加载)
    username: str = ""

    # 密码 (运行时从 config.json 加载)
    password: str = ""

    # 运营商选择 (中国移动)
    # 常见运营商代码: 中国移动=2, 中国联通=3, 中国电信=4, 校园网=1
    isp: int = 2

    # 运营商名称
    isp_name: str = "中国移动"

    # 登录URL
    login_url: str = "http://172.16.4.14"

    # 登录请求路径
    login_path: str = "/login"

    # 配置文件路径
    config_file: str = "config.json"

    # 日志文件路径
    log_file: str = "campus_network.log"

    # 最大重试次数
    max_retries: int = 3

    # 重试间隔(秒)
    retry_interval: int = 5

    # 网络连接超时(秒)
    network_timeout: int = 60

    def __post_init__(self):
        """初始化后加载配置文件"""
        self.load_config()

    def load_config(self):
        """从配置文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                # 更新配置
                for key, value in config_data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)

                print(f"已加载配置文件: {self.config_file}")
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                print("使用默认配置")
        else:
            print("配置文件不存在，首次运行请设置账号信息")
            self.first_run_setup()

    def save_config(self):
        """保存配置到文件"""
        try:
            config_data = {
                'auth_server': self.auth_server,
                'username': self.username,
                'password': self.password,
                'isp': self.isp,
                'isp_name': self.isp_name,
                'login_url': self.login_url,
                'login_path': self.login_path,
                'max_retries': self.max_retries,
                'retry_interval': self.retry_interval,
                'network_timeout': self.network_timeout
            }

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            print(f"配置已保存到: {self.config_file}")
        except Exception as e:
            print(f"保存配置文件失败: {e}")

    def first_run_setup(self):
        """首次运行设置向导"""
        print("=" * 50)
        print("       校园网自动登录 - 首次设置向导")
        print("=" * 50)
        print()

        self.username = input("请输入校园网账号: ").strip()
        self.password = input("请输入校园网密码: ").strip()

        print()
        print("请选择运营商:")
        print("  1. 校园网")
        print("  2. 中国移动")
        print("  3. 中国联通")
        print("  4. 中国电信")

        while True:
            try:
                choice = int(input("请输入运营商编号 (1-4): ").strip())
                if choice in [1, 2, 3, 4]:
                    self.isp = choice
                    isp_names = {1: "校园网", 2: "中国移动", 3: "中国联通", 4: "中国电信"}
                    self.isp_name = isp_names[choice]
                    break
                else:
                    print("请输入有效的编号 (1-4)")
            except ValueError:
                print("请输入数字")

        print()
        server = input(f"认证服务器地址 [{self.auth_server}]: ").strip()
        if server:
            self.auth_server = server
            self.login_url = f"http://{server}"

        print()
        print("设置完成！正在保存配置...")
        self.save_config()
        print()

    def get_auth_headers(self):
        """获取认证请求头"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': self.login_url
        }


# 默认配置实例
default_config = Config()
