"""
Confluence 浏览器模块
用于在Web界面中显示Confluence空间和页面信息
"""
import os
import streamlit as st
from streamlit_tree_select import tree_select
from atlassian import Confluence


def get_confluence_connection():
    """检查Confluence连接是否配置正确"""
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_user = os.getenv("CONFLUENCE_USER")
    confluence_token = os.getenv("CONFLUENCE_TOKEN")
    
    if not all([confluence_url, confluence_user, confluence_token]):
        st.error("Confluence配置不完整,请检查环境变量CONFLUENCE_URL、CONFLUENCE_USER和CONFLUENCE_TOKEN")
        return False

    return True


def get_confluence_client():
    """获取Confluence客户端实例"""
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_user = os.getenv("CONFLUENCE_USER")
    confluence_token = os.getenv("CONFLUENCE_TOKEN")

    return Confluence(
        url=confluence_url,
        username=confluence_user,
        password=confluence_token,
        cloud=True
    )


def get_spaces():
    """获取所有Confluence空间"""
    try:
        confluence = get_confluence_client()
        response = confluence.get_all_spaces(start=0, limit=9999, expand='description.plain,homepage')

        # 兼容不同响应格式
        if isinstance(response, dict) and 'results' in response:
            spaces_data = response['results']
        elif isinstance(response, list):
            spaces_data = response
        else:
            spaces_data = []

        result = []
        for space in spaces_data:
            result.append({
                'key': space.get('key', ''),
                'name': space.get('name', ''),
                'description': space.get('description', {}).get('plain', {}).get('value', '') if space.get('description') else '',
                'id': space.get('id', '')
            })
        print(f"成功获取 {len(result)} 个Confluence空间")
        return result
    except Exception as e:
        st.error(f"获取Confluence空间列表失败: {str(e)}")
        return []


def get_pages(space_key):
    """获取指定空间的页面"""
    try:
        confluence = get_confluence_client()
        response = confluence.get_all_pages_from_space(
            space=space_key,
            start=0,
            limit=9999,
            expand='space,history,ancestors'
        )

        # 兼容不同响应格式
        if isinstance(response, dict) and 'results' in response:
            pages_data = response['results']
        elif isinstance(response, list):
            pages_data = response
        else:
            pages_data = []

        result = []
        for page in pages_data:
            # 获取父页面ID（最后一个祖先通常是直接父页面）
            parent_id = None
            ancestors = page.get('ancestors', [])
            if ancestors:
                parent_id = ancestors[-1].get('id')

            result.append({
                'id': page.get('id', ''),
                'title': page.get('title', ''),
                'space': page.get('space', {}).get('key', space_key),
                'url': page.get('_links', {}).get('webui', f"/spaces/{space_key}/pages/{page.get('id', '')}"),
                'parent_id': parent_id,
                'ancestors': ancestors
            })
        print(f"成功获取 {len(result)} 个页面")
        return result
    except Exception as e:
        st.error(f"获取空间 {space_key} 的页面列表失败: {str(e)}")
        return []


def get_page_content(page_id):
    """获取页面内容"""
    try:
        confluence = get_confluence_client()

        # 获取页面详情和内容
        page = confluence.get_page_by_id(page_id=page_id, expand='space,history,body.storage')

        page_content = page.get('body', {}).get('storage', {}).get('value', '')

        result = {
            'id': page.get('id', ''),
            'title': page.get('title', ''),
            'space': page.get('space', {}).get('key', ''),
            'content': page_content,
            'version': page.get('version', {}).get('number', ''),
            'last_modified': page.get('history', {}).get('lastUpdated', {}).get('when', '') if page.get('history', {}).get('lastUpdated') else '',
            'url': f"{os.getenv('CONFLUENCE_URL')}{page.get('_links', {}).get('webui', '')}"
        }
        print(f"成功获取页面内容: {page_id}, 标题: {result['title']}")
        return result
    except Exception as e:
        st.error(f"获取页面 {page_id} 内容失败: {str(e)}")
        return None


def build_page_tree_for_selector(pages):
    """为tree_select组件构建页面树结构"""
    # 创建页面字典
    page_dict = {
        page['id']: {
            'id': page['id'],
            'title': page['title'],
            'url': page['url'],
            'parent_id': page['parent_id'],
            'ancestors': page['ancestors']
        }
        for page in pages
    }

    # 递归构建树节点
    def build_tree_node(page_info):
        # 找到所有子页面
        children = []
        for p_id, p_info in page_dict.items():
            if p_info['parent_id'] == page_info['id']:
                children.append(build_tree_node(p_info))

        # 创建树节点
        node = {
            'label': page_info['title'],
            'value': page_info['id']
        }

        if children:
            node['children'] = children

        return node

    # 找到所有根页面（没有父页面或父页面不在当前列表中）
    root_pages = [
        page_info for page_id, page_info in page_dict.items()
        if not page_info['parent_id'] or page_info['parent_id'] not in page_dict
    ]

    # 构建树结构
    tree_nodes = [build_tree_node(page_info) for page_info in root_pages]

    return tree_nodes


def initialize_session_state():
    """初始化session_state"""
    if 'selected_page_id' not in st.session_state:
        st.session_state.selected_page_id = None

    if 'tree_expanded' not in st.session_state:
        st.session_state.tree_expanded = []

    if 'tree_checked' not in st.session_state:
        st.session_state.tree_checked = []

    # 用于存储缓存的页面内容
    if 'cached_page_content' not in st.session_state:
        st.session_state.cached_page_content = {}


def render_page_tree(tree_nodes):
    """渲染页面树形选择器"""
    if not tree_nodes:
        st.info("空间中没有找到页面")
        return None

    # 渲染树形选择器
    result = tree_select(
        tree_nodes,
        checked=st.session_state.tree_checked,
        expanded=st.session_state.tree_expanded,
        only_leaf_checkboxes=False,
        no_cascade=True
    )

    if result:
        # 始终同步展开状态
        st.session_state.tree_expanded = result.get('expanded', [])

        # 只在选中状态变化时更新选中的页面ID
        new_checked = result.get('checked', [])
        if new_checked != st.session_state.tree_checked:
            st.session_state.tree_checked = new_checked
            # 更新选中的页面ID
            st.session_state.selected_page_id = new_checked[0] if new_checked else None
            return st.session_state.selected_page_id

    return st.session_state.selected_page_id


def render_page_content(page_id):
    """渲染页面内容"""
    # 检查缓存
    if page_id in st.session_state.cached_page_content:
        page_content = st.session_state.cached_page_content[page_id]
    else:
        # 获取页面内容
        with st.spinner("正在加载页面内容..."):
            page_content = get_page_content(page_id)

        if page_content:
            # 缓存页面内容
            st.session_state.cached_page_content[page_id] = page_content

    if not page_content:
        st.error("无法加载页面内容")
        return

    # 显示页面信息
    st.subheader(page_content['title'])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("页面ID", page_content['id'])
    with col2:
        st.metric("空间", page_content['space'])
    with col3:
        st.metric("版本", page_content['version'])
    with col4:
        st.write("**最后修改**")
        st.write(page_content['last_modified'][:10] if page_content['last_modified'] else "未知")

    # 显示页面内容
    if page_content['content']:
        with st.expander("📄 页面内容", expanded=True):
            try:
                st.markdown(page_content['content'], unsafe_allow_html=True)
            except Exception as e:
                st.text(page_content['content'])
    else:
        st.info("页面内容为空")

    # 操作按钮
    col1, col2 = st.columns([1, 5])
    with col1:
        st.link_button("🔗 在Confluence中打开", page_content['url'])
    with col2:
        if st.button("🔄 刷新内容"):
            # 清除缓存并重新加载
            if page_id in st.session_state.cached_page_content:
                del st.session_state.cached_page_content[page_id]
            st.rerun()


def show_confluence_browser():
    """显示Confluence浏览器界面"""
    st.title("📚 Confluence 浏览器")

    # 初始化session状态
    initialize_session_state()

    # 检查Confluence连接配置
    if not get_confluence_connection():
        st.warning("⚠️ 请先配置Confluence连接信息")
        return

    # 获取配置的空间键
    configured_space_key = os.getenv("CONFLUENCE_SPACE")

    if not configured_space_key:
        st.warning("⚠️ 请先在环境变量中配置 CONFLUENCE_SPACE")
        return

    # 获取空间信息
    with st.spinner(f"正在连接到空间 {configured_space_key}..."):
        all_spaces = get_spaces()
        target_space = next((s for s in all_spaces if s['key'] == configured_space_key), None)

    # 显示空间信息
    if target_space:
        st.info(f"📁 **{target_space['name']}** ({target_space['key']})" +
                (f" - {target_space['description']}" if target_space['description'] else ""))
    else:
        st.info(f"📁 空间: {configured_space_key}")

    # 创建左右布局
    col1, col2 = st.columns([1, 3])

    with col1:
        st.subheader("🗂️ 页面树")

        # 获取页面列表
        with st.spinner("正在加载页面列表..."):
            pages = get_pages(configured_space_key)

        if pages:
            # 构建树形结构
            tree_nodes = build_page_tree_for_selector(pages)

            # 渲染树形选择器
            selected_page_id = render_page_tree(tree_nodes)
        else:
            st.info(f"空间 {configured_space_key} 中没有找到页面")

    with col2:
        # 显示页面内容
        if st.session_state.selected_page_id:
            render_page_content(st.session_state.selected_page_id)
        else:
            st.info("👈 请从左侧选择一个页面")

