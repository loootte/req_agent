#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
运行pipeline测试（排除端到端测试）
此脚本运行所有测试，但排除需要外部服务的端到端测试
"""

import subprocess
import sys
from pathlib import Path

def run_pipeline_tests():
    """运行pipeline测试（排除e2e测试）"""
    print("🚀 开始运行pipeline测试（排除端到端测试）...")
    print("="*60)
    
    # 运行所有测试，但排除e2e标记的测试
    cmd = [
        sys.executable, "-m", "pytest", 
        "-m", "not e2e",  # 排除e2e测试
        "--strict-markers",  # 确保标记被正确定义
        "-v"  # 详细输出
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 测试运行成功！")
        print(f"标准输出:\n{result.stdout}")
        if result.stderr:
            print(f"错误输出:\n{result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 测试运行失败！")
        print(f"返回码: {e.returncode}")
        print(f"标准输出:\n{e.stdout}")
        print(f"错误输出:\n{e.stderr}")
        return False

def run_e2e_tests():
    """运行端到端测试（单独运行）"""
    print("\n🧪 运行端到端测试...")
    print("="*60)
    
    # 单独运行e2e测试
    cmd = [
        sys.executable, "-m", "pytest",
        "-m", "e2e",  # 只运行e2e测试
        "-v"  # 详细输出
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 端到端测试运行成功！")
        print(f"标准输出:\n{result.stdout}")
        if result.stderr:
            print(f"错误输出:\n{result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 端到端测试运行失败！")
        print(f"返回码: {e.returncode}")
        print(f"标准输出:\n{e.stdout}")
        print(f"错误输出:\n{e.stderr}")
        return False

if __name__ == "__main__":
    print("选择运行模式:")
    print("1. 运行pipeline测试（排除e2e）")
    print("2. 运行端到端测试")
    print("3. 两者都运行")
    
    choice = input("请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        success = run_pipeline_tests()
        if success:
            print("\n🎉 Pipeline测试运行完成！")
        else:
            print("\n💥 Pipeline测试失败！")
            sys.exit(1)
    elif choice == "2":
        success = run_e2e_tests()
        if success:
            print("\n🎉 端到端测试运行完成！")
        else:
            print("\n💥 端到端测试失败！")
            sys.exit(1)
    elif choice == "3":
        print("首先运行pipeline测试...")
        pipeline_success = run_pipeline_tests()
        
        print("\n然后运行端到端测试...")
        e2e_success = run_e2e_tests()
        
        if pipeline_success and e2e_success:
            print("\n🎉 所有测试运行完成！")
        else:
            print("\n💥 有些测试失败！")
            if not pipeline_success:
                print("- Pipeline测试失败")
            if not e2e_success:
                print("- 端到端测试失败")
            sys.exit(1)
    else:
        print("无效选择，运行pipeline测试...")
        success = run_pipeline_tests()
        if success:
            print("\n🎉 Pipeline测试运行完成！")
        else:
            print("\n💥 Pipeline测试失败！")
            sys.exit(1)