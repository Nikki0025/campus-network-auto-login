#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校园网自动登录程序
支持开机自动连接校园网
"""

import sys
import time
import logging
from datetime import datetime
from login import CampusNetworkLogin
from config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('campus_network.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def check_network_connection():
    """检查网络连接状态"""
    import subprocess
    try:
        # 尝试ping网关
        result = subprocess.run(
            ['ping', '-n', '1', '-w', '1000', '172.16.4.14'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False


def wait_for_network(timeout=60):
    """等待网络连接就绪"""
    logger.info("等待网络连接就绪...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        if check_network_connection():
            logger.info("网络连接已就绪")
            return True
        time.sleep(2)

    logger.warning("等待网络连接超时")
    return False


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("校园网自动登录程序启动")
    logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)

    # 加载配置
    config = Config()

    # 等待网络连接
    if not wait_for_network():
        logger.error("无法连接到网络，请检查网络设置")
        return False

    # 创建登录实例
    login = CampusNetworkLogin(config)

    # 尝试登录
    max_retries = 3
    for attempt in range(max_retries):
        logger.info(f"尝试登录... (第 {attempt + 1}/{max_retries} 次)")

        success = login.login()
        if success:
            logger.info("登录成功！")
            return True

        logger.warning(f"第 {attempt + 1} 次登录失败")
        if attempt < max_retries - 1:
            time.sleep(5)

    logger.error("登录失败，请检查账号密码或网络设置")
    return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序异常: {e}")
        sys.exit(1)
