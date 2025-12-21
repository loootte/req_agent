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
