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
    confluence_user = os.getenv("CONFLUENCE_USER")
    confluence_token = os.getenv("CONFLUENCE_TOKEN")
    confluence_space = os.getenv("CONFLUENCE_SPACE")
    
    print(f"URL: {confluence_url}")
    print(f"User: {confluence_user}")
    print(f"Space: {confluence_space}")
    print(f"Token length: {len(confluence_token) if confluence_token else 0}")
    
    if not all([confluence_url, confluence_user, confluence_token, confluence_space]):
        print("❌ 环境变量未完全配置")
        print("   请确保设置了: CONFLUENCE_URL, CONFLUENCE_USER, CONFLUENCE_TOKEN, CONFLUENCE_SPACE")
        return False
    
    try:
        from atlassian import Confluence
    except ImportError:
        print("❌ 缺少 atlassian-python-api 依赖")
        print("   安装命令: pip install atlassian-python-api")
        return False
    
    # 使用更新后的认证方法（用户名 + API token）
    try:
        print("\n📝 使用更新后的认证方法 (用户名 + API token)...")
        confluence = Confluence(
            url=confluence_url,
            username=confluence_user,  # 用户邮箱
            password=confluence_token  # API token
        )
        
        # 尝试一个简单的API调用 - 获取当前用户信息
        try:
            # 尝试获取当前用户信息
            user_info = confluence.get_user_details_by_username("", confluence_user)
            print("✅ 用户认证成功")
        except:
            print("⚠️  获取用户信息失败，但连接可能正常")
        
        # 尝试获取空间信息
        spaces = confluence.get_all_spaces(limit=5)
        print(f"✅ 成功获取空间列表，找到 {len(spaces.get('values', []))} 个空间")
        
        # 检查特定空间
        try:
            space_info = confluence.get_space(confluence_space, expand="description.plain,homepage")
            print(f"✅ 成功访问空间 {confluence_space}: {space_info.get('name', 'Unknown')}")
        except Exception as e:
            print(f"⚠️  访问空间失败: {str(e)}")
            # 尝试列出所有空间以帮助调试
            all_spaces = confluence.get_all_spaces(limit=100)
            space_keys = [space['key'] for space in all_spaces.get('values', [])]
            if confluence_space not in space_keys:
                print(f"   提示: 空间 '{confluence_space}' 不存在，可用空间: {space_keys[:10]}...")
        
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
            print("   - 用户名/邮箱错误")
            print("   - 用户名和token不匹配")
        else:
            print(f"\n💡 其他错误: {error_str}")
        
        return False

def check_confluence_config():
    """检查 Confluence 配置是否正确"""
    print("\n🔍 检查 Confluence 配置...")
    
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_user = os.getenv("CONFLUENCE_USER")
    confluence_token = os.getenv("CONFLUENCE_TOKEN")
    confluence_space = os.getenv("CONFLUENCE_SPACE")
    
    issues = []
    
    # 检查 URL 格式
    if not confluence_url or not confluence_url.startswith('https://'):
        issues.append("URL 必须以 https:// 开头")
    elif 'atlassian.net' not in confluence_url and 'jira.com' not in confluence_url:
        issues.append("URL 格式可能不正确（应为 https://yourcompany.atlassian.net 或 https://yourcompany.jira.com）")
    
    # 检查用户邮箱格式
    if not confluence_user or '@' not in confluence_user or '.' not in confluence_user:
        issues.append("CONFLUENCE_USER 应为有效的邮箱地址")
    
    # 检查 token 长度（Atlassian API token 通常为长字符串）
    if confluence_token and len(confluence_token) < 10:
        issues.append("API token 长度过短，可能不正确")
    
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

def test_legacy_auth():
    """测试旧的认证方法（仅用于对比）"""
    print("\n🔍 测试旧的认证方法 (仅用于对比)...")
    
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_token = os.getenv("CONFLUENCE_TOKEN")
    
    if not all([confluence_url, confluence_token]):
        print("   跳过 - 环境变量未配置完整")
        return None
    
    try:
        from atlassian import Confluence
        
        print("   尝试使用旧的 token-only 认证方法...")
        confluence = Confluence(url=confluence_url, token=confluence_token)
        
        # 尝试简单的API调用
        try:
            spaces = confluence.get_all_spaces(limit=1)
            print("   ⚠️ 旧方法意外成功 - 请忽略此结果")
            return "unexpected_success"
        except Exception as e:
            if "401" in str(e) or "unauthorized" in str(e).lower():
                print("   ✅ 旧方法失败（预期结果 - 需要使用用户名+token方法）")
                return "expected_failure"
            else:
                print(f"   ❓ 旧方法失败，但错误类型不同: {str(e)}")
                return "other_failure"
    except Exception as e:
        print(f"   ❌ 旧方法测试失败: {str(e)}")
        return "test_error"

if __name__ == "__main__":
    print("Confluence API 认证测试工具")
    print("="*50)
    
    # 检查配置
    config_ok = check_confluence_config()
    
    if config_ok:
        print()
        # 测试旧方法（用于对比）
        test_legacy_auth()
        
        print()
        # 测试新方法
        success = test_confluence_auth()
        
        if success:
            print("\n🎉 Confluence 认证测试成功！")
            print("   您的配置已正确设置，可以正常使用 Confluence API。")
        else:
            print("\n❌ Confluence 认证测试失败")
            print("   请根据上述错误信息检查您的配置。")
    else:
        print("\n❌ 配置检查失败")
        print("   请先解决配置问题，然后重新运行测试。")