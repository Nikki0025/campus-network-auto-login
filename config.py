#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""配置文件"""

import os
import json
from dataclasses import dataclass, field

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@dataclass
class Config:
    """配置类"""
    auth_server: str = "172.16.4.14"
    username: str = ""
    password: str = ""
    # 运营商: 1=校园网, 2=中国移动, 3=中国联通, 4=中国电信
    isp: int = 2
    max_retries: int = 3
    retry_interval: int = 5
    network_timeout: int = 60

    config_file: str = field(default_factory=lambda: os.path.join(BASE_DIR, "config.json"))

    def __post_init__(self):
        self._load()

    def _load(self):
        """从 config.json 加载配置"""
        if not os.path.exists(self.config_file):
            self._first_run()
            return

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        except Exception as e:
            print(f"加载配置失败: {e}")

    def _first_run(self):
        """首次运行设置向导"""
        print("=" * 50)
        print("       校园网自动登录 - 首次设置向导")
        print("=" * 50)
        self.username = input("请输入校园网账号: ").strip()
        self.password = input("请输入校园网密码: ").strip()

        print("\n请选择运营商:")
        print("  1. 校园网  2. 中国移动  3. 中国联通  4. 中国电信")
        while True:
            try:
                choice = int(input("请输入编号 (1-4): ").strip())
                if choice in (1, 2, 3, 4):
                    self.isp = choice
                    break
            except ValueError:
                pass
            print("请输入有效编号")

        server = input(f"\n认证服务器地址 [{self.auth_server}]: ").strip()
        if server:
            self.auth_server = server

        # 保存配置
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump({
                'auth_server': self.auth_server,
                'username': self.username,
                'password': self.password,
                'isp': self.isp,
            }, f, indent=2, ensure_ascii=False)
        print(f"\n配置已保存到: {self.config_file}")
