#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 Confluence 认证的正确方法
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_confluence_auth():
    """测试正确的 Confluence 认证方法"""
    print("🔍 测试正确的 Confluence 认证方法...")
    
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_token = os.getenv("CONFLUENCE_TOKEN")
    confluence_space = os.getenv("CONFLUENCE_SPACE")
    
    print(f"URL: {confluence_url}")
    print(f"Space: {confluence_space}")
    print(f"Token length: {len(confluence_token) if confluence_token else 0}")
    
    if not all([confluence_url, confluence_token, confluence_space]):
        print("❌ 环境变量未完全配置")
        return False
    
    try:
        from atlassian import Confluence
    except ImportError:
        print("❌ 缺少 atlassian-python-api 依赖")
        return False
    
    # 使用与工具中相同的方法
    try:
        print("\n📝 使用工具中的认证方法...")
        confluence = Confluence(url=confluence_url, token=confluence_token)
        
        # 尝试一个简单的API调用 - 获取当前用户信息
        try:
            user_info = confluence.get_user_details_by_username("", "anonymous")  # 获取当前用户
            print("✅ 基本连接成功")
        except:
            print("⚠️  获取用户信息失败，但连接可能正常")
        
        # 尝试获取空间信息
        spaces = confluence.get_all_spaces(limit=5)
        print(f"✅ 成功获取空间列表，找到 {len(spaces.get('values', []))} 个空间")
        
        # 检查特定空间
        space_info = confluence.get_space(confluence_space, expand="description.plain,homepage")
        print(f"✅ 成功访问空间 {confluence_space}: {space_info.get('name', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 认证失败: {str(e)}")
        
        # 根据错误类型提供调试建议
        error_str = str(e).lower()
        if "403" in error_str or "forbidden" in error_str or "access" in error_str:
            print("\n💡 403 错误可能原因:")
            print("   - API token 权限不足")
            print("   - 账户没有访问 Confluence 的权限")
            print("   - 账户没有访问特定空间的权限")
            print("   - URL 格式不正确")
        elif "401" in error_str or "unauthorized" in error_str:
            print("\n💡 401 错误可能原因:")
            print("   - API token 错误")
            print("   - 用户名/密码错误")
        else:
            print(f"\n💡 其他错误: {error_str}")
        
        return False

def check_confluence_config():
    """检查 Confluence 配置是否正确"""
    print("\n🔍 检查 Confluence 配置...")
    
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_token = os.getenv("CONFLUENCE_TOKEN")
    confluence_space = os.getenv("CONFLUENCE_SPACE")
    
    issues = []
    
    # 检查 URL 格式
    if not confluence_url or not confluence_url.startswith('https://') or 'atlassian.net' not in confluence_url:
        issues.append("URL 格式可能不正确（应为 https://yourcompany.atlassian.net）")
    
    # 检查 token 长度
    if confluence_token and len(confluence_token) != 192:  # Atlassian API token 标准长度
        issues.append(f"API token 长度异常（标准长度为192字符，当前为{len(confluence_token)}字符）")
    
    # 检查空间格式
    if confluence_space and not confluence_space.isupper():
        issues.append("Confluence 空间 key 通常为大写字母")
    
    if issues:
        print("❌ 发现配置问题:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        return False
    else:
        print("✅ 配置格式正确")
        return True

if __name__ == "__main__":
    check_confluence_config()
    print()
    test_confluence_auth()