"""
Confluence 页面层级结构测试
用于测试 Confluence 的页面层级结构组织方式
"""
import os
from dotenv import load_dotenv
from atlassian import Confluence

# 加载环境变量
load_dotenv()


def get_confluence_client():
    """获取Confluence客户端实例"""
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_user = os.getenv("CONFLUENCE_USER")
    confluence_token = os.getenv("CONFLUENCE_TOKEN")
    
    if not all([confluence_url, confluence_user, confluence_token]):
        raise ValueError("Confluence配置不完整，请检查环境变量CONFLUENCE_URL、CONFLUENCE_USER和CONFLUENCE_TOKEN")
    
    return Confluence(
        url=confluence_url,
        username=confluence_user,
        password=confluence_token,
        cloud=True
    )


def test_space_structure():
    """测试空间结构"""
    print("=== 测试 Confluence 空间结构 ===")
    try:
        confluence = get_confluence_client()
        # 获取所有空间
        response = confluence.get_all_spaces(start=0, limit=50, expand='description.plain,homepage')
        
        # 检查响应格式并相应处理
        if isinstance(response, dict) and 'results' in response:
            spaces_data = response['results']
        elif isinstance(response, list):
            spaces_data = response
        else:
            spaces_data = []
        
        print(f"找到 {len(spaces_data)} 个空间:")
        for space in spaces_data:
            print(f"  - 空间名称: {space.get('name', 'Unknown')}, 键: {space.get('key', 'Unknown')}, ID: {space.get('id', 'Unknown')}")
        
        return spaces_data
    except Exception as e:
        print(f"获取空间结构失败: {str(e)}")
        return []


def test_page_hierarchy(space_key):
    """测试页面层级结构"""
    print(f"\n=== 测试空间 {space_key} 的页面层级结构 ===")
    try:
        confluence = get_confluence_client()
        # 获取指定空间的页面
        response = confluence.get_all_pages_from_space(space=space_key, start=0, limit=100, expand='space,history,ancestors')
        
        # 检查响应格式并相应处理
        if isinstance(response, dict) and 'results' in response:
            pages_data = response['results']
        elif isinstance(response, list):
            pages_data = response
        else:
            pages_data = []
        
        print(f"空间 {space_key} 中找到 {len(pages_data)} 个页面:")
        
        # 创建页面字典便于查找
        page_dict = {}
        for page in pages_data:
            page_dict[page['id']] = {
                'id': page.get('id', ''),
                'title': page.get('title', ''),
                'space': page.get('space', {}).get('key', space_key),
                'ancestors': page.get('ancestors', []),
                'parent_id': None,
                'children': []
            }
        
        # 确定父页面关系
        for page_id, page_info in page_dict.items():
            ancestors = page_info['ancestors']
            if ancestors:
                # 最后一个祖先通常是直接父页面
                parent_id = ancestors[-1].get('id')
                if parent_id in page_dict:
                    page_dict[page_id]['parent_id'] = parent_id
                    # 将当前页面添加到父页面的子页面列表中
                    page_dict[parent_id]['children'].append(page_info)
        
        # 找到根页面（没有父页面的页面）
        root_pages = []
        for page_id, page_info in page_dict.items():
            if page_info['parent_id'] is None:
                root_pages.append(page_info)
        
        # 打印页面层级关系
        print("\n页面层级关系:")
        for page_id, page_info in page_dict.items():
            parent_id = page_info['parent_id']
            parent_title = '无' if parent_id is None else next((p['title'] for p in page_dict.values() if p['id'] == parent_id), '未知页面')
            print(f"  - 页面: {page_info['title']} (ID: {page_info['id']}) -> 父页面: {parent_title} (ID: {parent_id})")
        
        # 构建并打印完整的树形结构
        print(f"\n完整的树形结构 (根页面数量: {len(root_pages)}):")
        for root_page in root_pages:
            print_page_tree(root_page, 0, page_dict)
        
        return page_dict
    except Exception as e:
        print(f"获取页面层级结构失败: {str(e)}")
        return {}


def print_page_tree(page, level, page_dict):
    """递归打印页面树结构"""
    indent = "  " * level
    print(f"{indent}📁 {page['title']} (ID: {page['id']})")
    
    # 打印子页面
    for child in page['children']:
        print_page_tree(child, level + 1, page_dict)


def build_page_tree(page_dict):
    """构建页面树结构"""
    # 找到根页面（没有父页面的页面）
    root_pages = []
    for page_id, page_info in page_dict.items():
        if page_info['parent_id'] is None:
            root_pages.append(page_info)
    
    return root_pages


def print_tree(root_pages, page_dict, level=0):
    """打印树形结构"""
    indent = "  " * level
    for page_id in root_pages:
        if page_id in page_dict:
            page_info = page_dict[page_id]
            print(f"{indent}- {page_info['title']} (ID: {page_info['id']})")
            
            # 找到所有子页面
            children = [pid for pid, pinfo in page_dict.items() if pinfo['parent_id'] == page_id]
            if children:
                print_tree(children, page_dict, level + 1)


def test_specific_page_structure(page_id):
    """测试特定页面的详细结构"""
    print(f"\n=== 测试页面 {page_id} 的详细结构 ===")
    try:
        confluence = get_confluence_client()
        # 获取页面详情
        page = confluence.get_page_by_id(page_id=page_id, expand='space,history,ancestors,children.page,descendants.page')
        
        print(f"页面标题: {page.get('title', 'Unknown')}")
        print(f"页面ID: {page.get('id', 'Unknown')}")
        print(f"空间: {page.get('space', {}).get('key', 'Unknown')}")
        
        # 显示祖先页面
        ancestors = page.get('ancestors', [])
        print(f"祖先页面数量: {len(ancestors)}")
        for i, ancestor in enumerate(ancestors):
            print(f"  祖先 {i+1}: {ancestor.get('title', 'Unknown')} (ID: {ancestor.get('id', 'Unknown')})")
        
        # 显示子页面
        children = page.get('children', {}).get('page', {}).get('results', [])
        print(f"子页面数量: {len(children)}")
        for child in children:
            print(f"  子页面: {child.get('title', 'Unknown')} (ID: {child.get('id', 'Unknown')})")
        
        return page
    except Exception as e:
        print(f"获取页面详细结构失败: {str(e)}")
        return None


def main():
    """主测试函数"""
    print("开始测试 Confluence 页面层级结构...")
    
    # 测试空间结构
    spaces = test_space_structure()
    
    if spaces:
        # 使用第一个空间进行页面层级测试
        first_space_key = spaces[0].get('key')
        if first_space_key:
            print(f"\n使用空间 {first_space_key} 进行页面层级测试...")
            
            # 测试页面层级结构
            page_dict = test_page_hierarchy(first_space_key)
            
            # 如果有页面，测试第一个页面的详细结构
            if page_dict:
                first_page_id = next(iter(page_dict.keys()))
                test_specific_page_structure(first_page_id)
    
    print("\n测试完成.")


if __name__ == "__main__":
    main()