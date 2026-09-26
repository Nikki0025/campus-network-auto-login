#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校园网登录模块
支持多种校园网认证方式
"""

import re
import time
import json
import hashlib
import logging
import requests
from urllib.parse import urljoin, urlencode
from config import Config

logger = logging.getLogger(__name__)


class CampusNetworkLogin:
    """校园网登录类"""

    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(config.get_auth_headers())
        self.session.verify = False  # 禁用SSL验证

        # 禁用SSL警告
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def login(self):
        """
        登录校园网
        根据不同的认证系统尝试不同的登录方式
        """
        try:
            # 首先检查是否已经登录
            if self.check_already_logged():
                logger.info("已经登录，无需重复登录")
                return True

            # 尝试不同的认证方式
            auth_methods = [
                self.try_ruijie_auth,
                self.try_drcom_auth,
                self.try_shenlan_auth,
                self.try_web_auth
            ]

            for method in auth_methods:
                try:
                    logger.info(f"尝试 {method.__name__} 认证方式...")
                    if method():
                        return True
                except Exception as e:
                    logger.debug(f"{method.__name__} 失败: {e}")
                    continue

            logger.error("所有认证方式都失败了")
            return False

        except Exception as e:
            logger.error(f"登录过程异常: {e}")
            return False

    def check_already_logged(self):
        """检查是否已经登录"""
        try:
            response = self.session.get(
                self.config.login_url,
                timeout=10,
                allow_redirects=False
            )

            # 如果重定向到其他页面，说明已经登录
            if response.status_code in [301, 302]:
                location = response.headers.get('Location', '')
                if 'login' not in location.lower():
                    logger.info("检测到已登录状态")
                    return True

            # 检查页面内容
            if 'logout' in response.text.lower() or '已登录' in response.text:
                logger.info("检测到已登录状态")
                return True

            return False
        except:
            return False

    def try_ruijie_auth(self):
        """
        尝试锐捷认证
        常见于很多高校
        """
        try:
            # 获取登录页面
            login_page_url = urljoin(self.config.login_url, '/login')
            response = self.session.get(login_page_url, timeout=10)

            # 查找必要的参数
            # 锐捷认证通常需要以下参数
            data = {
                'userId': self.config.username,
                'password': self.encode_password_ruijie(self.config.password),
                'service': '',
                'queryString': '',
                'operatorPwd': '',
                'operatorUserId': '',
                'validcode': '',
                'passwordEncrypt': 'on'
            }

            # 尝试登录
            login_url = urljoin(self.config.login_url, '/cgi-bin/login')
            response = self.session.post(
                login_url,
                data=data,
                timeout=10
            )

            # 检查登录结果
            if self.check_login_success(response):
                return True

            return False
        except Exception as e:
            logger.debug(f"锐捷认证失败: {e}")
            return False

    def try_drcom_auth(self):
        """
        尝试Dr.COM认证
        常见于很多高校
        """
        try:
            # Dr.COM认证通常需要特定的参数
            data = {
                'DDDDD': f',0,{self.config.username}',
                'upass': self.config.password,
                '0MKKey': 'Login',
                'buttonClicked': '',
                'redirect_url': '',
                'err_flag': '',
                'username': self.config.username,
                'password': self.config.password,
                'user': self.config.username,
                'cmd': 'login',
                'Login': 'Login'
            }

            login_url = urljoin(self.config.login_url, '/login')
            response = self.session.post(
                login_url,
                data=data,
                timeout=10
            )

            if self.check_login_success(response):
                return True

            return False
        except Exception as e:
            logger.debug(f"Dr.COM认证失败: {e}")
            return False

    def try_shenlan_auth(self):
        """
        尝试深澜认证
        常见于很多高校
        """
        try:
            # 深澜认证通常需要以下参数
            data = {
                'username': self.config.username,
                'password': self.config.password,
                'isp': str(self.config.isp),
                'area': '',
                'random': str(int(time.time() * 1000)),
                'service': '',
                'queryString': '',
                'operatorPwd': '',
                'operatorUserId': '',
                'validcode': '',
                'passwordEncrypt': ''
            }

            login_url = urljoin(self.config.login_url, '/srun_portal_phone')
            response = self.session.post(
                login_url,
                data=data,
                timeout=10
            )

            if self.check_login_success(response):
                return True

            return False
        except Exception as e:
            logger.debug(f"深澜认证失败: {e}")
            return False

    def try_web_auth(self):
        """
        尝试通用Web认证
        适用于大多数校园网认证系统
        """
        try:
            # 获取登录页面
            response = self.session.get(
                self.config.login_url,
                timeout=10
            )

            # 尝试解析页面，查找表单
            form_data = self.parse_login_form(response.text)

            if not form_data:
                # 使用默认参数
                form_data = self.get_default_form_data()

            # 更新账号密码
            form_data.update({
                'username': self.config.username,
                'password': self.config.password,
                'isp': str(self.config.isp)
            })

            # 查找登录URL
            login_url = self.find_login_url(response.text)
            if not login_url:
                login_url = urljoin(self.config.login_url, '/login')

            # 发送登录请求
            response = self.session.post(
                login_url,
                data=form_data,
                timeout=10
            )

            if self.check_login_success(response):
                return True

            return False
        except Exception as e:
            logger.debug(f"Web认证失败: {e}")
            return False

    def encode_password_ruijie(self, password):
        """
        锐捷认证密码编码
        """
        try:
            # 简单的编码方式，可能需要根据实际情况调整
            encoded = ''
            for char in password:
                encoded += str(ord(char)) + ' '
            return encoded.strip()
        except:
            return password

    def parse_login_form(self, html_content):
        """
        解析登录表单
        """
        form_data = {}

        # 查找input标签
        inputs = re.findall(r'<input[^>]*name=["\']([^"\']+)["\'][^>]*value=["\']([^"\']*)["\']', html_content)
        for name, value in inputs:
            if name not in ['username', 'password']:
                form_data[name] = value

        return form_data if form_data else None

    def find_login_url(self, html_content):
        """
        查找登录URL
        """
        # 查找form标签
        form_match = re.search(r'<form[^>]*action=["\']([^"\']+)["\']', html_content)
        if form_match:
            action = form_match.group(1)
            if action.startswith('http'):
                return action
            else:
                return urljoin(self.config.login_url, action)

        return None

    def get_default_form_data(self):
        """
        获取默认表单数据
        """
        return {
            'userId': self.config.username,
            'password': self.config.password,
            'service': '',
            'queryString': '',
            'operatorPwd': '',
            'operatorUserId': '',
            'validcode': '',
            'passwordEncrypt': ''
        }

    def check_login_success(self, response):
        """
        检查登录是否成功
        """
        try:
            # 检查响应状态码
            if response.status_code == 200:
                # 检查响应内容
                text = response.text.lower()

                # 成功标志
                success_keywords = [
                    'login success',
                    '登录成功',
                    'welcome',
                    '欢迎',
                    '已登录',
                    'success',
                    'result":1',
                    '"result":1',
                    'result=1'
                ]

                for keyword in success_keywords:
                    if keyword in text:
                        return True

                # 检查是否重定向到成功页面
                if response.url and 'login' not in response.url.lower():
                    return True

            # 检查重定向
            if response.status_code in [301, 302]:
                location = response.headers.get('Location', '')
                if 'login' not in location.lower():
                    return True

            return False
        except Exception as e:
            logger.debug(f"检查登录结果异常: {e}")
            return False


if __name__ == "__main__":
    # 测试登录
    config = Config()
    login = CampusNetworkLogin(config)
    success = login.login()
    print(f"登录结果: {'成功' if success else '失败'}")
