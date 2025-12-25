#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试Confluence连接问题
"""

import os
from dotenv import load_dotenv
from urllib.parse import urljoin

# 加载环境变量
load_dotenv()

def debug_confluence():
    """调试Confluence连接"""
    print("🔍 调试 Confluence 连接...")
    
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_token = os.getenv("CONFLUENCE_TOKEN")
    confluence_space = os.getenv("CONFLUENCE_SPACE")
    
    print(f"  URL: {confluence_url}")
    print(f"  Token 长度: {len(confluence_token) if confluence_token else 0}")
    print(f"  Space: {confluence_space}")
    
    if not all([confluence_url, confluence_token, confluence_space]):
        print("❌ 环境变量未完全配置")
        return False
    
    # 检查URL格式
    if not confluence_url.startswith(('https://', 'http://')):
        print("❌ URL 应该以 https:// 或 http:// 开头")
        return False
    
    # 尝试使用不同的认证方式
    try:
        from atlassian import Confluence
    except ImportError:
        print("❌ 缺少 atlassian-python-api 依赖")
        return False
    
    # 方法1: 使用基本认证 (token)
    try:
        print("\n📝 尝试使用 token 认证...")
        confluence = Confluence(
            url=confluence_url,
            username="email@example.com",  # 某些Atlassian实例需要用户名
            password=confluence_token,      # API token
            cloud=True
        )
        
        # 尝试获取空间信息
        spaces = confluence.get_all_spaces(limit=5)
        print(f"✅ 通过 token 认证成功! 找到 {len(spaces.get('values', []))} 个空间")
        
        # 检查目标空间是否存在
        space_keys = [space['key'] for space in spaces.get('values', [])]
        if confluence_space in space_keys:
            print(f"✅ 目标空间 {confluence_space} 存在")
        else:
            print(f"⚠️  目标空间 {confluence_space} 不存在于 {space_keys}")
        
        return True
    except Exception as e:
        print(f"❌ token 认证失败: {str(e)}")
    
    # 方法2: 尝试只使用API token认证
    try:
        print("\n📝 尝试使用 API token 认证...")
        confluence = Confluence(
            url=confluence_url,
            token=confluence_token,  # 直接使用token参数
            cloud=True
        )
        
        spaces = confluence.get_all_spaces(limit=5)
        print(f"✅ 通过 API token 认证成功! 找到 {len(spaces.get('values', []))} 个空间")
        
        return True
    except Exception as e:
        print(f"❌ API token 认证失败: {str(e)}")
    
    # 方法3: 尝试使用 basic auth
    try:
        print("\n📝 尝试使用 basic auth 认证...")
        # 通常 Confluence API 使用 email 作为用户名，API token 作为密码
        username = confluence_token.split(':')[0] if ':' in confluence_token else "email@example.com"
        password = confluence_token
        
        confluence = Confluence(
            url=confluence_url,
            username=username,
            password=password,
            cloud=True
        )
        
        spaces = confluence.get_all_spaces(limit=5)
        print(f"✅ 通过 basic auth 认证成功! 找到 {len(spaces.get('values', []))} 个空间")
        
        return True
    except Exception as e:
        print(f"❌ basic auth 认证失败: {str(e)}")
    
    print("\n❌ 所有认证方法都失败了")
    print("\n💡 可能的解决方案:")
    print("   1. 检查 Confluence API token 是否正确生成")
    print("   2. 确认 Confluence 空间 key 是否正确")
    print("   3. 验证账户是否有访问该空间的权限")
    print("   4. 检查 URL 格式是否正确 (例如: https://yourcompany.atlassian.net)")
    
    return False

if __name__ == "__main__":
    debug_confluence()