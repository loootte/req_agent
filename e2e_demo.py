#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
端到端测试演示脚本
演示通过agent从文本创建ADO workitem和Confluence Page的完整流程
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def main():
    print("🚀 开始端到端集成测试演示")
    print("="*60)
    
    # 验证环境变量
    required_vars = [
        'DASHSCOPE_API_KEY',
        'CONFLUENCE_URL',
        'CONFLUENCE_USER', 
        'CONFLUENCE_TOKEN',
        'CONFLUENCE_SPACE',
        'ADO_ORG_URL',
        'ADO_PAT',
        'ADO_PROJECT'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ 缺少环境变量: {missing_vars}")
        return False
    else:
        print("✅ 环境变量验证通过")
    
    # 导入必要的模块
    try:
        from src.requirement_tracker.crew import run_crew
        from src.requirement_tracker.tools import (
            create_ado_feature,
            create_confluence_page,
            get_ado_connection,
            get_confluence_spaces
        )
        print("✅ 模块导入成功")
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False
    
    # 测试输入
    test_input = "创建一个自动化需求分析工具，用于分析用户需求并生成文档"
    print(f"📝 测试输入: {test_input}")
    
    # 运行端到端流程
    print("\n🔄 开始执行端到端流程...")
    try:
        result = run_crew(test_input, "qwen")
        print("✅ 端到端流程执行成功")
        
        # 解析结果
        if "ADO 工作项 ID" in result:
            import re
            workitem_match = re.search(r"工作项 ID: (\d+)", result)
            if workitem_match:
                workitem_id = workitem_match.group(1)
                print(f"✅ 成功创建ADO工作项: {workitem_id}")
        
        if "Confluence 页" in result:
            print("✅ 成功创建Confluence页面")
        
        print("\n📋 执行结果:")
        print(result)
        
        return True
    except Exception as e:
        print(f"❌ 端到端流程执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 端到端集成测试演示成功完成！")
    else:
        print("\n💥 端到端集成测试演示失败！")
        sys.exit(1)