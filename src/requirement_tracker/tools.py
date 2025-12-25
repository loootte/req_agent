from crewai import Agent, Task, Crew
from crewai.tools import BaseTool as Tool, tool
import os

# 环境变量安全存放凭证（强烈推荐！）
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_TOKEN = os.getenv("CONFLUENCE_TOKEN")  # API Token
CONFLUENCE_SPACE = os.getenv("CONFLUENCE_SPACE")  # 如 "REQ"
CONFLUENCE_PARENT_ID = os.getenv("CONFLUENCE_PARENT_ID")  # 可选父页面ID

ADO_ORG_URL = os.getenv("ADO_ORG_URL")  # https://dev.azure.com/yourorg
ADO_PAT = os.getenv("ADO_PAT")
ADO_PROJECT = os.getenv("ADO_PROJECT")
ADO_FEATURE_TYPE = "Feature"  # 或你的自定义类型

# 如果用Jira
JIRA_URL = os.getenv("JIRA_URL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
JIRA_PROJECT = os.getenv("JIRA_PROJECT")


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

    credentials = BasicAuthentication('', ADO_PAT)
    connection = Connection(base_url=ADO_ORG_URL, creds=credentials)
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
        credentials = BasicAuthentication('', ADO_PAT)
        connection = Connection(base_url=ADO_ORG_URL, creds=credentials)
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
        credentials = BasicAuthentication('', ADO_PAT)
        connection = Connection(base_url=ADO_ORG_URL, creds=credentials)
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

    confluence = Confluence(url=CONFLUENCE_URL, token=CONFLUENCE_TOKEN)
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

    confluence = Confluence(url=CONFLUENCE_URL, token=CONFLUENCE_TOKEN)
    confluence.update_page(page_id=page_id, title=new_title)
    return "标题更新成功"


# Tool 5: 生成结构化需求文档HTML（可选）
@tool("Format Requirement Document")
def format_doc(problem: str, goal: str, artifacts: str, criteria: str, risks: str) -> str:
    """生成Confluence兼容的HTML文档"""
    return f"""
    <h1>Problem Statement</h1><p>{problem}</p>
"""
