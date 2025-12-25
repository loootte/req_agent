#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Confluence和ADO连接的脚本
"""

import os
import sys
from dotenv import load_dotenv
import urllib.parse

# 加载环境变量
load_dotenv()

def test_confluence_connection():
    """测试Confluence连接"""
    print("🧪 测试 Confluence 连接...")
    
    try:
        from atlassian import Confluence
    except ImportError:
        print("❌ 缺少 Confluence 依赖，请安装: pip install atlassian-python-api")
        return False
    
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_token = os.getenv("CONFLUENCE_TOKEN")
    confluence_space = os.getenv("CONFLUENCE_SPACE")
    
    if not all([confluence_url, confluence_token, confluence_space]):
        print("❌ Confluence 环境变量未完全配置")
        return False
    
    try:
        # 创建Confluence实例
        confluence = Confluence(url=confluence_url, token=confluence_token)
        
        # 尝试获取空间信息来测试连接
        spaces = confluence.get_all_spaces(limit=5)  # 只获取前5个空间
        space_keys = [space['key'] for space in spaces.get('values', [])]
        
        if confluence_space in space_keys:
            print(f"✅ Confluence 连接成功! 找到目标空间 {confluence_space}")
            return True
        else:
            print(f"✅ Confluence 连接成功! 可用空间: {space_keys}")
            print(f"⚠️  但目标空间 {confluence_space} 不在列表中")
            return True  # 连接成功，只是空间不存在
            
    except Exception as e:
        print(f"❌ Confluence 连接失败: {str(e)}")
        return False

def test_ado_connection():
    """测试ADO连接"""
    print("\n🧪 测试 Azure DevOps 连接...")
    
    try:
        from msrest.authentication import BasicAuthentication
        from azure.devops.connection import Connection
    except ImportError:
        print("❌ 缺少 Azure DevOps 依赖，请安装: pip install azure-devops")
        return False
    
    ado_org_url = os.getenv("ADO_ORG_URL")
    ado_pat = os.getenv("ADO_PAT")
    ado_project = os.getenv("ADO_PROJECT")
    
    # 移除ADO_PROJECT可能包含的引号
    if ado_project and (ado_project.startswith('"') or ado_project.startswith("'")):
        ado_project = ado_project.strip('"\'')
    
    if not all([ado_org_url, ado_pat, ado_project]):
        print("❌ ADO 环境变量未完全配置")
        print(f"  ADO_ORG_URL: {'已配置' if ado_org_url else '未配置'}")
        print(f"  ADO_PAT: {'已配置' if ado_pat else '未配置'}")
        print(f"  ADO_PROJECT: {'已配置' if ado_project else '未配置'}")
        return False
    
    try:
        credentials = BasicAuthentication('', ado_pat)
        connection = Connection(base_url=ado_org_url, creds=credentials)
        
        # 尝试获取项目列表来测试连接
        core_client = connection.clients.get_core_client()
        projects = core_client.get_projects()
        
        project_names = [proj.name for proj in projects]
        
        if ado_project in project_names:
            print(f"✅ ADO 连接成功! 找到目标项目 {ado_project}")
            return True
        else:
            print(f"✅ ADO 连接成功! 可用项目: {project_names}")
            print(f"⚠️  但目标项目 {ado_project} 不在列表中")
            return True  # 连接成功，只是项目不存在
            
    except Exception as e:
        print(f"❌ ADO 连接失败: {str(e)}")
        return False

def test_tools():
    """测试工具导入"""
    print("\n🧪 测试工具导入...")
    
    try:
        from src.requirement_tracker.tools import (
            create_ado_feature,
            create_confluence_page,
            update_confluence_title
        )
        print("✅ 工具导入成功!")
        return True
    except Exception as e:
        print(f"❌ 工具导入失败: {str(e)}")
        return False

def main():
    print("🔧 开始测试 Confluence 和 ADO 连接...")
    
    results = []
    results.append(test_confluence_connection())
    results.append(test_ado_connection())
    results.append(test_tools())
    
    print(f"\n📊 测试结果: {sum(results)}/{len(results)} 项通过")
    
    if all(results):
        print("🎉 所有测试通过！集成环境配置正确。")
        return True
    else:
        print("⚠️  有测试失败，请检查相关配置。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)