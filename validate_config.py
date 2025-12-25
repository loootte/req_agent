#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证配置信息的脚本
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def validate_config():
    """验证配置信息"""
    print("🔍 验证配置信息...")
    
    # 验证Confluence配置
    print("\n📋 Confluence 配置:")
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_token = os.getenv("CONFLUENCE_TOKEN")
    confluence_space = os.getenv("CONFLUENCE_SPACE")
    
    print(f"  CONFLUENCE_URL: {confluence_url}")
    print(f"  CONFLUENCE_TOKEN 长度: {len(confluence_token) if confluence_token else 0} 字符")
    print(f"  CONFLUENCE_SPACE: {confluence_space}")
    
    # 验证ADO配置
    print("\n📋 Azure DevOps 配置:")
    ado_org_url = os.getenv("ADO_ORG_URL")
    ado_pat = os.getenv("ADO_PAT")
    ado_project = os.getenv("ADO_PROJECT")
    
    print(f"  ADO_ORG_URL: {ado_org_url}")
    print(f"  ADO_PAT 长度: {len(ado_pat) if ado_pat else 0} 字符")
    print(f"  ADO_PROJECT: {ado_project}")
    
    # 验证其他配置
    print("\n📋 其他配置:")
    dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
    print(f"  DASHSCOPE_API_KEY 长度: {len(dashscope_api_key) if dashscope_api_key else 0} 字符")
    
    # 检查配置完整性
    print("\n✅ 配置完整性检查:")
    confluence_complete = all([confluence_url, confluence_token, confluence_space])
    ado_complete = all([ado_org_url, ado_pat, ado_project])
    
    print(f"  Confluence 配置完整: {'是' if confluence_complete else '否'}")
    print(f"  ADO 配置完整: {'是' if ado_complete else '否'}")
    
    if confluence_complete:
        print(f"  Confluence URL 格式: {'有效' if confluence_url.startswith('https://') and 'atlassian.net' in confluence_url else '可能无效'}")
    if ado_complete:
        print(f"  ADO URL 格式: {'有效' if ado_org_url.startswith('https://') and 'dev.azure.com' in ado_org_url else '可能无效'}")
    
    return confluence_complete and ado_complete

def validate_ado_project_name():
    """检查ADO项目名称是否需要特殊处理"""
    ado_project = os.getenv("ADO_PROJECT")
    print(f"\n🔍 ADO 项目名称分析: {repr(ado_project)}")
    
    if ado_project and ' ' in ado_project:
        print("  ⚠️  项目名称包含空格，这可能导致API调用问题")
        print(f"  🔧 建议的URL编码: {ado_project.replace(' ', '%20')}")
    
if __name__ == "__main__":
    load_dotenv()  # 确保环境变量被加载
    is_valid = validate_config()
    validate_ado_project_name()
    
    print(f"\n{'✅' if is_valid else '❌'} 配置验证完成")