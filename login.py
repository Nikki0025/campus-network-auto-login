#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dr.COM 校园网登录模块"""

import re
import json
import base64
import random
import logging
import requests
import urllib3
from config import Config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)

# ISP 后缀映射
ISP_SUFFIX = {1: "", 2: "@cmcc", 3: "@lt", 4: "@dx"}


class CampusNetworkLogin:
    """Dr.COM 校园网登录"""

    def __init__(self, config: Config):
        self.config = config
        self.server = config.auth_server
        self.session = requests.Session()
        self.session.verify = False

    def login(self):
        """登录校园网（已登录则跳过）"""
        if self._check_online():
            return True

        for attempt in range(self.config.max_retries):
            logger.info(f"尝试登录... (第 {attempt + 1}/{self.config.max_retries} 次)")
            if self._drcom_login():
                return True
            if attempt < self.config.max_retries - 1:
                import time
                time.sleep(self.config.retry_interval)

        logger.error("登录失败")
        return False

    def _check_online(self):
        """通过 chkstatus 检查是否已在线"""
        data = self._request(f"http://{self.server}/drcom/chkstatus", raw=True)
        if data and data.get('result') == 1:
            logger.info("已登录，无需重复登录")
            return True
        return False

    def _drcom_login(self):
        """Dr.COM eportal 登录（参数格式来自浏览器抓包）"""
        # 账号格式: ,0,username@suffix
        suffix = ISP_SUFFIX.get(self.config.isp, "")
        account = f",0,{self.config.username}{suffix}"
        password_b64 = base64.b64encode(self.config.password.encode()).decode()

        # 获取网络信息
        net = self._get_net_info()

        params = {
            'callback': 'drcom_login',
            'login_method': '1',
            'user_account': account,
            'user_password': password_b64,
            'wlan_user_ip': net.get('ip', ''),
            'wlan_user_ipv6': '',
            'wlan_user_mac': net.get('mac', ''),
            'wlan_vlan_id': net.get('vlan', '0'),
            'wlan_ac_ip': net.get('ac_ip', ''),
            'wlan_ac_name': '',
            'authex_enable': '',
            'jsVersion': '4.2.2',
            'terminal_type': '1',
            'lang': 'zh-cn',
            'program_index': '',
            'page_index': '',
            'v': str(random.randint(1000, 9999)),
        }

        logger.info(f"Dr.COM 登录: {account}")
        data = self._request(
            f"http://{self.server}:801/eportal/portal/login",
            params=params
        )

        if not data:
            return False

        result = data.get('result', -1)
        ret_code = data.get('ret_code', -1)

        if result == 1:
            logger.info("登录成功" if ret_code == 0 else "IP 已在线")
            return True

        logger.warning(f"登录失败: {data.get('msg', '')}")
        return False

    def _get_net_info(self):
        """获取网络信息（IP、MAC、VLAN）"""
        data = self._request(f"http://{self.server}/drcom/chkstatus", raw=True)
        if not data:
            return {}
        return {
            'ip': data.get('v4ip') or data.get('ss5') or '',
            'mac': data.get('olmac') or '',
            'vlan': str(data.get('vid', 0)),
            'ac_ip': data.get('wlanacip') or '',
        }

    def _request(self, url, params=None, raw=False):
        """发送 JSONP 请求并解析响应"""
        try:
            if params is None:
                params = {}
            params.setdefault('callback', 'dr')
            params.setdefault('jsVersion', '4.X')

            r = self.session.get(url, params=params, timeout=10)
            match = re.search(r'\{.*\}', r.text)
            if not match:
                return {} if raw else False

            data = json.loads(match.group(0))
            if not raw:
                logger.info(f"响应: result={data.get('result')}, msg={data.get('msg', '')}")
            return data
        except Exception as e:
            logger.debug(f"请求失败 {url}: {e}")
            return {} if raw else False
