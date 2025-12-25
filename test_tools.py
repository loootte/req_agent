#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试Confluence和ADO集成的测试脚本
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__)))

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
        print(f"  CONFLUENCE_URL: {'已配置' if confluence_url else '未配置'}")
        print(f"  CONFLUENCE_TOKEN: {'已配置' if confluence_token else '未配置'}")
        print(f"  CONFLUENCE_SPACE: {'已配置' if confluence_space else '未配置'}")
        return False
    
    try:
        confluence = Confluence(url=confluence_url, token=confluence_token)
        # 尝试获取空间信息来测试连接
        spaces = confluence.get_all_spaces(limit=1)
        print(f"✅ Confluence 连接成功! 空间数量: {len(spaces.get('values', []))}")
        return True
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
    
    if not all([ado_org_url, ado_pat, ado_project]):
        print("❌ ADO 环境变量未完全配置")
        print(f"  ADO_ORG_URL: {'已配置' if ado_org_url else '未配置'}")
        print(f"  ADO_PAT: {'已配置' if ado_pat else '未配置'}")
        print(f"  ADO_PROJECT: {'已配置' if ado_project else '未配置'}")
        return False
    
    try:
        credentials = BasicAuthentication('', ado_pat)
        connection = Connection(base_url=ado_org_url, creds=credentials)
        # 尝试获取项目客户端来测试连接
        core_client = connection.clients.get_core_client()
        # 尝试获取特定项目信息来测试连接
        import urllib.parse
        encoded_project = urllib.parse.quote(ado_project, safe='')
        project = core_client.get_project(project_id=encoded_project)
        print(f"✅ ADO 连接成功! 项目: {project.name}")
        return True
    except Exception as e:
        print(f"❌ ADO 连接失败: {str(e)}")
        return False

def test_tools_import():
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
    print("🔧 开始调试 Confluence 和 ADO 集成...")
    
    results = []
    results.append(test_confluence_connection())
    results.append(test_ado_connection())
    results.append(test_tools_import())
    
    print(f"\n📊 测试结果: {sum(results)}/{len(results)} 项通过")
    
    if all(results):
        print("🎉 所有测试通过！集成环境配置正确。")
    else:
        print("⚠️  有测试失败，请检查相关配置。")

if __name__ == "__main__":
    main()