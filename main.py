#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校园网自动登录程序"""

import os
import sys
import time
import logging
import subprocess
from datetime import datetime
from login import CampusNetworkLogin
from config import Config, BASE_DIR

# 日志配置
log_path = os.path.join(BASE_DIR, 'campus_network.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

AUTH_SERVER = "172.16.4.14"


def wait_for_network(timeout=60):
    """等待网络连接就绪（ping 认证服务器）"""
    logger.info("等待网络连接就绪...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            result = subprocess.run(
                ['ping', '-n', '1', '-w', '1000', AUTH_SERVER],
                capture_output=True, timeout=5
            )
            if result.returncode == 0:
                logger.info("网络连接已就绪")
                return True
        except Exception:
            pass
        time.sleep(2)
    logger.warning("等待网络连接超时")
    return False


def main():
    logger.info("=" * 50)
    logger.info(f"校园网自动登录 - {datetime.now():%Y-%m-%d %H:%M:%S}")
    logger.info("=" * 50)

    config = Config()

    if not wait_for_network(config.network_timeout):
        logger.error("无法连接到网络")
        return False

    login = CampusNetworkLogin(config)
    if login.login():
        logger.info("登录成功！")
        return True

    logger.error("登录失败，请检查账号密码或网络设置")
    return False


if __name__ == "__main__":
    try:
        sys.exit(0 if main() else 1)
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序异常: {e}")
        sys.exit(1)
