#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows任务计划程序配置
用于设置开机自动登录校园网
"""

import os
import sys
import subprocess
import ctypes
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Windows任务计划程序管理类"""

    def __init__(self):
        self.task_name = "CampusNetworkAutoLogin"
        self.python_exe = sys.executable
        self.script_path = os.path.abspath(__file__)
        self.project_dir = os.path.dirname(self.script_path)
        self.main_script = os.path.join(self.project_dir, "main.py")

    def is_admin(self):
        """检查是否以管理员权限运行"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run_as_admin(self):
        """以管理员权限重新运行"""
        if not self.is_admin():
            logger.info("需要管理员权限，正在请求提升...")
            try:
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable,
                    " ".join(sys.argv), None, 1
                )
                sys.exit(0)
            except:
                logger.error("无法获取管理员权限")
                return False
        return True

    def create_batch_file(self):
        """创建批处理文件"""
        batch_content = f'''@echo off
title 校园网自动登录
echo 正在启动校园网自动登录程序...
cd /d "{self.project_dir}"
"{self.python_exe}" "{self.main_script}"
if errorlevel 1 (
    echo 登录失败，请检查配置
    pause
)
'''
        batch_path = os.path.join(self.project_dir, "start_login.bat")
        try:
            with open(batch_path, 'w', encoding='gbk') as f:
                f.write(batch_content)
            logger.info(f"已创建批处理文件: {batch_path}")
            return batch_path
        except Exception as e:
            logger.error(f"创建批处理文件失败: {e}")
            return None

    def create_vbs_file(self):
        """创建VBS文件（静默运行）"""
        vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """{self.python_exe}"" ""{self.main_script}""", 0, False
'''
        vbs_path = os.path.join(self.project_dir, "start_login_silent.vbs")
        try:
            with open(vbs_path, 'w', encoding='utf-8') as f:
                f.write(vbs_content)
            logger.info(f"已创建VBS文件: {vbs_path}")
            return vbs_path
        except Exception as e:
            logger.error(f"创建VBS文件失败: {e}")
            return None

    def create_task(self):
        """创建Windows任务计划程序任务"""
        try:
            # 创建批处理文件
            batch_path = self.create_batch_file()
            if not batch_path:
                return False

            # 创建VBS文件（用于静默运行）
            vbs_path = self.create_vbs_file()
            if not vbs_path:
                return False

            # 使用schtasks命令创建任务
            # 任务在用户登录时运行
            cmd = [
                'schtasks',
                '/create',
                '/tn', self.task_name,
                '/tr', f'"{vbs_path}"',
                '/sc', 'onlogon',
                '/rl', 'highest',
                '/f'  # 强制创建，覆盖已有任务
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=True
            )

            if result.returncode == 0:
                logger.info("任务计划程序任务创建成功")
                logger.info(f"任务名称: {self.task_name}")
                logger.info(f"触发器: 用户登录时")
                logger.info(f"运行方式: 最高权限")
                return True
            else:
                logger.error(f"创建任务失败: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"创建任务计划程序任务失败: {e}")
            return False

    def remove_task(self):
        """删除任务"""
        try:
            cmd = ['schtasks', '/delete', '/tn', self.task_name, '/f']
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=True
            )

            if result.returncode == 0:
                logger.info("任务已删除")
                return True
            else:
                logger.warning(f"删除任务失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"删除任务失败: {e}")
            return False

    def check_task(self):
        """检查任务是否存在"""
        try:
            cmd = ['schtasks', '/query', '/tn', self.task_name]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=True
            )
            return result.returncode == 0
        except:
            return False

    def run_task_now(self):
        """立即运行任务"""
        try:
            cmd = ['schtasks', '/run', '/tn', self.task_name]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=True
            )

            if result.returncode == 0:
                logger.info("任务已启动")
                return True
            else:
                logger.error(f"启动任务失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"启动任务失败: {e}")
            return False

    def setup(self):
        """设置开机自动登录"""
        print("=" * 50)
        print("校园网自动登录 - 开机启动设置")
        print("=" * 50)

        # 检查管理员权限
        if not self.is_admin():
            print("\n提示: 需要管理员权限才能创建任务计划程序")
            print("正在请求提升权限...")
            if not self.run_as_admin():
                print("无法获取管理员权限，请以管理员身份运行此程序")
                return False

        # 检查任务是否已存在
        if self.check_task():
            print(f"\n任务 '{self.task_name}' 已存在")
            choice = input("是否重新创建? (y/n): ").strip().lower()
            if choice == 'y':
                self.remove_task()
            else:
                print("跳过创建")
                return True

        # 创建任务
        print("\n正在创建开机自动登录任务...")
        success = self.create_task()

        if success:
            print("\n" + "=" * 50)
            print("设置完成！")
            print("=" * 50)
            print(f"任务名称: {self.task_name}")
            print("触发器: 用户登录时自动运行")
            print("运行方式: 最高权限")
            print("\n文件列表:")
            print(f"  - 主程序: {self.main_script}")
            print(f"  - 批处理: start_login.bat")
            print(f"  - VBS脚本: start_login_silent.vbs")
            print("\n管理命令:")
            print(f"  查看任务: schtasks /query /tn {self.task_name}")
            print(f"  运行任务: schtasks /run /tn {self.task_name}")
            print(f"  删除任务: schtasks /delete /tn {self.task_name} /f")
            print("=" * 50)
            return True
        else:
            print("\n设置失败，请检查错误信息")
            return False


def main():
    """主函数"""
    scheduler = TaskScheduler()
    success = scheduler.setup()
    if success:
        input("\n按回车键退出...")
    else:
        input("\n按回车键退出...")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
