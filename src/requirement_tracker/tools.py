from crewai import Agent, Task, Crew
from crewai.tools import BaseTool as Tool, tool
import os

# 环境变量安全存放凭证（强烈推荐！）
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_USER = os.getenv("CONFLUENCE_USER")  # 用户邮箱
CONFLUENCE_TOKEN = os.getenv("CONFLUENCE_TOKEN")  # API Token
CONFLUENCE_SPACE = os.getenv("CONFLUENCE_SPACE")  # 如 "REQ"
CONFLUENCE_PARENT_ID = os.getenv("CONFLUENCE_PARENT_ID")  # 可选父页面ID

ADO_ORG_URL = os.getenv("ADO_ORG_URL")  # https://dev.azure.com/yourorg
ADO_PAT = os.getenv("ADO_PAT")
ADO_PROJECT = os.getenv("ADO_PROJECT")
ADO_FEATURE_TYPE = os.getenv("ADO_FEATURE_TYPE", "Feature")  # 默认值为 "Feature"

# 如果用Jira
JIRA_URL = os.getenv("JIRA_URL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
JIRA_PROJECT = os.getenv("JIRA_PROJECT")


def get_ado_connection():
    """获取Azure DevOps连接的通用函数"""
    try:
        from msrest.authentication import BasicAuthentication
        from azure.devops.connection import Connection
    except ImportError as e:
        raise ImportError(
            "Missing Azure DevOps dependencies. Install with: pip install req_agent[azure]"
        ) from e

    if not ADO_PAT or not ADO_ORG_URL:
        raise Exception("ADO配置不完整，请检查环境变量ADO_ORG_URL和ADO_PAT")

    try:
        credentials = BasicAuthentication('', ADO_PAT)
        connection = Connection(base_url=ADO_ORG_URL, creds=credentials)
        return connection
    except Exception as e:
        raise Exception(f"ADO连接失败: {str(e)}")


# Tool 1: 在ADO创建Feature
@tool("Create ADO Feature")
def create_ado_feature(summary: str, description: str) -> str:
    """在Azure DevOps创建Feature并返回ID"""
    try:
        from msrest.authentication import BasicAuthentication
        from azure.devops.connection import Connection
        from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation
    except ImportError as e:
        raise ImportError(
            "Missing Azure DevOps dependencies for create_ado_feature. Install with: pip install req_agent[azure]"
        ) from e

    connection = get_ado_connection()
    wit_client = connection.clients.get_work_item_tracking_client()

    patch = [
        JsonPatchOperation(op="add", path="/fields/System.Title", value=summary),
        JsonPatchOperation(op="add", path="/fields/System.Description", value=description),
        # 加其他字段如 Acceptance Criteria 等
    ]
    work_item = wit_client.create_work_item(document=patch, project=ADO_PROJECT, type=ADO_FEATURE_TYPE)
    return str(work_item.id)


# Tool 2: 获取ADO项目列表
@tool("Get ADO Projects")
def get_ado_projects() -> list:
    """获取Azure DevOps中的所有项目"""
    try:
        from msrest.authentication import BasicAuthentication
        from azure.devops.connection import Connection
    except ImportError as e:
        raise ImportError(
            "Missing Azure DevOps dependencies for get_ado_projects. Install with: pip install req_agent[azure]"
        ) from e

    try:
        connection = get_ado_connection()
        core_client = connection.clients.get_core_client()
        projects = core_client.get_projects()
        return [project.name for project in projects]
    except Exception as e:
        raise Exception(f"获取ADO项目列表失败: {str(e)}")


# Tool 2.1: 获取ADO工作项
@tool("Get ADO Work Items")
def get_ado_work_items(project_name: str, work_item_type: str = "Feature") -> list:
    """获取指定项目中的工作项"""
    try:
        from msrest.authentication import BasicAuthentication
        from azure.devops.connection import Connection
        from azure.devops.v7_1.work_item_tracking.models import Wiql
    except ImportError as e:
        raise ImportError(
            "Missing Azure DevOps dependencies for get_ado_work_items. Install with: pip install req_agent[azure]"
        ) from e

    try:
        connection = get_ado_connection()
        wit_client = connection.clients.get_work_item_tracking_client()
        
        # 查询工作项的WIQL查询
        # 对项目名称和工作项类型进行适当的转义处理
        escaped_project_name = project_name.replace("'", "''")
        escaped_work_item_type = work_item_type.replace("'", "''")
        
        wiql_query = Wiql(
            query=f"""
            SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType], [System.AssignedTo]
            FROM WorkItems
            WHERE [System.TeamProject] = '{escaped_project_name}'
            AND [System.WorkItemType] = '{escaped_work_item_type}'
            ORDER BY [System.Id] DESC
            """
        )
        
        # 添加调试信息
        print(f"执行WIQL查询: 项目='{escaped_project_name}', 类型='{escaped_work_item_type}'")
        print(f"完整查询语句: {wiql_query.query}")
        
        # 执行查询
        query_result = wit_client.query_by_wiql(wiql=wiql_query)
        work_items = []
        
        if query_result.work_items:
            print(f"查询返回 {len(query_result.work_items)} 个工作项")
            # 获取详细的工作项信息
            work_item_ids = [item.id for item in query_result.work_items]
            if work_item_ids:
                # 分批获取工作项详情，避免404错误（ADO API对批量请求有限制）
                batch_size = 200  # ADO API推荐的批量大小
                for i in range(0, len(work_item_ids), batch_size):
                    batch_ids = work_item_ids[i:i + batch_size]
                    print(f"获取批次 {i//batch_size + 1}: {len(batch_ids)} 个工作项")
                    
                    batch_items = wit_client.get_work_items(ids=batch_ids)
                    for item in batch_items:
                        work_items.append({
                            'id': item.id,
                            'title': item.fields.get('System.Title', 'No Title'),
                            'type': item.fields.get('System.WorkItemType', 'N/A'),
                            'state': item.fields.get('System.State', 'N/A'),
                            'assigned_to': item.fields.get('System.AssignedTo', {}).get('displayName', 'Unassigned') if item.fields.get('System.AssignedTo') else 'Unassigned',
                            'description': item.fields.get('System.Description', 'N/A')
                        })
        else:
            print("查询返回0个工作项")
        
        print(f"成功获取 {len(work_items)} 个工作项")
        return work_items
    except Exception as e:
        print(f"获取ADO工作项失败: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        raise Exception(f"获取ADO工作项失败: {str(e)}")


# Tool 2.2: 获取ADO Area路径
@tool("Get ADO Area Paths")
def get_area_paths(project_name: str) -> list:
    """获取指定项目的所有Area路径"""
    try:
        from msrest.authentication import BasicAuthentication
        from azure.devops.connection import Connection
    except ImportError as e:
        raise ImportError(
            "Missing Azure DevOps dependencies for get_area_paths. Install with: pip install req_agent[azure]"
        ) from e

    try:
        connection = get_ado_connection()
        
        # 获取 Work Item Tracking 客户端
        wit_client = connection.clients.get_work_item_tracking_client()
        
        # 获取 Area Path 分类节点
        try:
            # 获取根节点及其所有子节点
            area_root = wit_client.get_classification_node(
                project=project_name,
                structure_group='areas',
                depth=100  # 获取所有层级
            )
            
            # 递归提取所有Area路径
            def extract_areas(node, parent_path=""):
                areas = []
                current_path = f"{parent_path}\\{node.name}" if parent_path else node.name
                
                # 添加当前节点
                areas.append({
                    'name': node.name,
                    'path': current_path,
                    'id': node.id
                })
                
                # 递归处理子节点
                if hasattr(node, 'children') and node.children:
                    for child in node.children:
                        areas.extend(extract_areas(child, current_path))
                
                return areas
            
            # 提取所有Area路径
            if hasattr(area_root, 'children') and area_root.children:
                all_areas = []
                for child in area_root.children:
                    all_areas.extend(extract_areas(child))
                return all_areas
            else:
                # 如果没有子节点，返回根节点本身
                return [{
                    'name': area_root.name,
                    'path': area_root.name,
                    'id': area_root.id
                }] if area_root.name else []
                
        except Exception as e:
            print(f"获取 Area Path 失败: {str(e)}")
            return []
    except Exception as e:
        raise Exception(f"获取项目 {project_name} 的Area路径失败: {str(e)}")


# Tool 2.3: 获取ADO工作项（支持Area过滤）
@tool("Get ADO Work Items with Area Filter")
def get_ado_work_items_with_area(project_name: str, work_item_type: str = "Feature", area_path: str = None) -> list:
    """获取指定项目的工作项，支持Area路径过滤"""
    try:
        from msrest.authentication import BasicAuthentication
        from azure.devops.connection import Connection
        from azure.devops.v7_1.work_item_tracking.models import Wiql
    except ImportError as e:
        raise ImportError(
            "Missing Azure DevOps dependencies for get_ado_work_items_with_area. Install with: pip install req_agent[azure]"
        ) from e

    try:
        connection = get_ado_connection()
        wit_client = connection.clients.get_work_item_tracking_client()
        
        # 构建查询条件
        where_clause = f"[System.TeamProject] = '{project_name.replace("'", "''")}' AND [System.WorkItemType] = '{work_item_type.replace("'", "''")}'"
        
        # 如果指定了Area，则添加Area过滤条件
        if area_path:
            escaped_area_path = area_path.replace("'", "''")
            where_clause += f" AND [System.AreaPath] = '{escaped_area_path}'"
        
        # 查询工作项的WIQL查询
        wiql_query = Wiql(
            query=f"""
            SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType], [System.AssignedTo], [System.AreaPath], [System.Description]
            FROM WorkItems
            WHERE {where_clause}
            ORDER BY [System.Id] DESC
            """
        )
        
        # 执行查询
        query_result = wit_client.query_by_wiql(wiql=wiql_query)
        work_items = []
        
        if query_result.work_items:
            # 获取详细的工作项信息
            work_item_ids = [item.id for item in query_result.work_items]
            if work_item_ids:
                # 分批获取工作项详情，避免404错误（ADO API对批量请求有限制）
                batch_size = 200  # ADO API推荐的批量大小
                for i in range(0, len(work_item_ids), batch_size):
                    batch_ids = work_item_ids[i:i + batch_size]
                    
                    batch_items = wit_client.get_work_items(ids=batch_ids)
                    for item in batch_items:
                        work_items.append({
                            'id': item.id,
                            'title': item.fields.get('System.Title', 'No Title'),
                            'type': item.fields.get('System.WorkItemType', 'N/A'),
                            'state': item.fields.get('System.State', 'N/A'),
                            'area_path': item.fields.get('System.AreaPath', 'N/A'),
                            'assigned_to': item.fields.get('System.AssignedTo', {}).get('displayName', 'Unassigned') if item.fields.get('System.AssignedTo') else 'Unassigned',
                            'description': item.fields.get('System.Description', 'N/A')
                        })
        
        return work_items
    except Exception as e:
        print(f"获取ADO工作项失败: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        raise Exception(f"获取ADO工作项失败: {str(e)}")


# Tool 3: 创建Confluence页面
@tool("Create Confluence Page")
def create_confluence_page(title: str, body_html: str) -> str:
    """创建Confluence页面，返回页面ID"""
    try:
        from atlassian import Confluence
    except ImportError as e:
        raise ImportError(
            "Missing Confluence dependencies for create_confluence_page. Install with: pip install req_agent[confluence]"
        ) from e

    # 使用用户名和API token进行认证
    confluence = Confluence(
        url=CONFLUENCE_URL, 
        username=CONFLUENCE_USER,  # 用户邮箱
        password=CONFLUENCE_TOKEN  # API Token
    )
    page = confluence.create_page(
        space=CONFLUENCE_SPACE,
        title=title,
        body=body_html,
        parent_id=CONFLUENCE_PARENT_ID  # 可选
    )
    return str(page['id'])


# Tool 4: 更新Confluence页面标题
@tool("Update Confluence Page Title")
def update_confluence_title(page_id: str, new_title: str) -> str:
    """更新Confluence页面标题"""
    try:
        from atlassian import Confluence
    except ImportError as e:
        raise ImportError(
            "Missing Confluence dependencies for update_confluence_title. Install with: pip install req_agent[confluence]"
        ) from e

    # 使用用户名和API token进行认证
    confluence = Confluence(
        url=CONFLUENCE_URL, 
        username=CONFLUENCE_USER,  # 用户邮箱
        password=CONFLUENCE_TOKEN  # API Token
    )
    confluence.update_page(page_id=page_id, title=new_title)
    return "标题更新成功"


# Tool 5: 获取Confluence空间列表
@tool("Get Confluence Spaces")
def get_confluence_spaces(max_results: int = 100) -> list:
    """获取Confluence中的所有空间"""
    try:
        from atlassian import Confluence
    except ImportError as e:
        raise ImportError(
            "Missing Confluence dependencies for get_confluence_spaces. Install with: pip install req_agent[confluence]"
        ) from e

    try:
        # 使用用户名和API token进行认证
        confluence = Confluence(
            url=CONFLUENCE_URL,
            username=CONFLUENCE_USER,  # 用户邮箱
            password=CONFLUENCE_TOKEN  # API Token
        )
        
        # 获取空间列表
        response = confluence.get_all_spaces(start=0, limit=max_results, expand='description.plain,homepage')

        # 检查响应格式并相应处理
        if isinstance(response, dict) and 'results' in response:
            spaces_data = response['results']
        elif isinstance(response, list):
            spaces_data = response
        else:
            spaces_data = []

        space_list = []

        for space in spaces_data:
            # 处理空间描述，兼容字符串和字典格式
            description = ''
            if space.get('description'):
                desc_data = space.get('description')
                if isinstance(desc_data, dict):
                    description = desc_data.get('plain', {}).get('value', '')
                elif isinstance(desc_data, str):
                    description = desc_data
            
            space_list.append({
                'key': space.get('key', ''),
                'name': space.get('name', ''),
                'id': space.get('id', ''),
                'description': description
            })

        return space_list
    except Exception as e:
        raise Exception(f"获取Confluence空间列表失败: {str(e)}")


# Tool 6: 获取Confluence页面列表
@tool("Get Confluence Pages")
def get_confluence_pages(space_key: str, max_results: int = 100) -> list:
    """获取指定空间中的所有页面"""
    try:
        from atlassian import Confluence
    except ImportError as e:
        raise ImportError(
            "Missing Confluence dependencies for get_confluence_pages. Install with: pip install req_agent[confluence]"
        ) from e

    try:
        # 使用用户名和API token进行认证
        confluence = Confluence(
            url=CONFLUENCE_URL,
            username=CONFLUENCE_USER,  # 用户邮箱
            password=CONFLUENCE_TOKEN  # API Token
        )
        
        # 获取页面列表
        response = confluence.get_all_pages_from_space(space=space_key, start=0, limit=max_results, expand='space,history,ancestors')

        # 检查响应格式并相应处理
        if isinstance(response, dict) and 'results' in response:
            pages_data = response['results']
        elif isinstance(response, list):
            pages_data = response
        else:
            pages_data = []

        page_list = []

        for page in pages_data:
            # 获取父页面信息
            parent_id = None
            ancestors = page.get('ancestors', [])
            if ancestors:
                # 最后一个祖先通常是直接父页面
                parent_id = ancestors[-1].get('id')

            page_list.append({
                'id': page.get('id', ''),
                'title': page.get('title', ''),
                'space': page.get('space', {}).get('key', space_key),
                'url': f"{CONFLUENCE_URL}{page.get('_links', {}).get('webui', f'/spaces/{space_key}/pages/{page.get("id", "")}') if page.get('_links') else f'/spaces/{space_key}/pages/{page.get("id", "")}'}",
                'content': page.get('body', {}).get('storage', {}).get('value', '') if page.get('body', {}).get('storage') else '',
                'version': page.get('version', {}).get('number', 0) if page.get('version') else 0,
                'created_date': page.get('history', {}).get('createdDate', '') if page.get('history') else '',
                'parent_id': parent_id
            })

        return page_list
    except Exception as e:
        raise Exception(f"获取空间 {space_key} 的页面列表失败: {str(e)}")


# Tool 7: 获取Confluence页面内容
@tool("Get Confluence Page Content")
def get_confluence_page_content(page_id: str) -> dict:
    """获取指定页面的内容"""
    try:
        from atlassian import Confluence
    except ImportError as e:
        raise ImportError(
            "Missing Confluence dependencies for get_confluence_page_content. Install with: pip install req_agent[confluence]"
        ) from e

    try:
        # 使用用户名和API token进行认证
        confluence = Confluence(
            url=CONFLUENCE_URL,
            username=CONFLUENCE_USER,  # 用户邮箱
            password=CONFLUENCE_TOKEN  # API Token
        )
        
        # 获取页面详情
        page = confluence.get_page_by_id(page_id=page_id, expand='space,history')

        if page:
            # 获取页面内容
            content = confluence.get_page_by_id(page_id=page_id, expand='body.storage')
            page_content = content.get('body', {}).get('storage', {}).get('value', '') if content else ''
            
            result = {
                'id': page.get('id', ''),
                'title': page.get('title', ''),
                'space': page.get('space', {}).get('key', ''),
                'url': f"{CONFLUENCE_URL}{page.get('_links', {}).get('webui', '')}",
                'content': page_content,
                'version': page.get('version', {}).get('number', 0) if page.get('version') else 0,
                'created_date': page.get('history', {}).get('createdDate', '') if page.get('history') else '',
                'last_modified': page.get('history', {}).get('lastUpdated', {}).get('when', '') if page.get('history', {}).get('lastUpdated') else ''
            }
            return result
        else:
            raise Exception(f"页面 {page_id} 不存在")
    except Exception as e:
        raise Exception(f"获取页面 {page_id} 内容失败: {str(e)}")


# Tool 8: 生成结构化需求文档HTML（可选）
@tool("Format Requirement Document")
def format_doc(problem: str, goal: str, artifacts: str, criteria: str, risks: str) -> str:
    """生成Confluence兼容的HTML文档"""
    return f"""
    <h1>Problem Statement</h1><p>{problem}</p>
"""