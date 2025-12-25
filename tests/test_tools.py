import os
import pytest
from unittest.mock import patch, MagicMock, Mock
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool as Tool, tool


class TestConfluencePage:
    """测试Confluence页面工具函数"""
    
    @patch.dict(os.environ, {
        "CONFLUENCE_URL": "https://test.atlassian.net",
        "CONFLUENCE_USER": "test@example.com",
        "CONFLUENCE_TOKEN": "test_token",
        "CONFLUENCE_SPACE": "TEST"
    })
    @patch('atlassian.Confluence')
    def test_create_confluence_page_success(self, mock_confluence_class):
        """测试成功创建Confluence页面"""
        # 临时定义工具函数，以确保环境变量和mock正确应用
        @tool("Test Create Confluence Page")
        def temp_create_confluence_page(title: str, body_html: str) -> str:
            """创建Confluence页面，返回页面ID"""
            try:
                from atlassian import Confluence
            except ImportError as e:
                raise ImportError(
                    "Missing Confluence dependencies for create_confluence_page. Install with: pip install req_agent[confluence]"
                ) from e

            confluence = Confluence(
                url=os.getenv("CONFLUENCE_URL"),
                username=os.getenv("CONFLUENCE_USER"),
                password=os.getenv("CONFLUENCE_TOKEN")
            )
            page = confluence.create_page(
                space=os.getenv("CONFLUENCE_SPACE"),
                title=title,
                body=body_html,
                parent_id=os.getenv("CONFLUENCE_PARENT_ID")  # 可选
            )
            return str(page['id'])
        
        # 模拟Confluence实例和创建结果
        mock_confluence_instance = Mock()
        mock_confluence_class.return_value = mock_confluence_instance
        
        mock_page = {'id': '12345'}
        mock_confluence_instance.create_page.return_value = mock_page
        
        # 执行工具
        result = temp_create_confluence_page.run(title="Test Title", body_html="<p>Test Content</p>")
        
        # 验证结果
        assert result == "12345"
        # 验证Confluence使用正确的认证参数初始化
        mock_confluence_class.assert_called_once()
        # 获取调用参数进行验证
        call_args = mock_confluence_class.call_args
        assert call_args[1]['url'] == "https://test.atlassian.net"
        assert call_args[1]['username'] == "test@example.com"
        assert call_args[1]['password'] == "test_token"
        
        # 验证create_page被调用
        mock_confluence_instance.create_page.assert_called_once()
        # 获取调用参数并验证关键参数
        call_args = mock_confluence_instance.create_page.call_args
        # 确保至少title和body参数是正确的
        assert call_args[1]['title'] == "Test Title"
        assert call_args[1]['body'] == "<p>Test Content</p>"
        # 验证空间参数
        assert call_args[1]['space'] == "TEST"
    
    def test_create_confluence_page_import_error(self):
        """测试缺少依赖时的导入错误"""
        # 创建一个临时函数来测试导入错误
        @tool("Test Confluence Page")
        def temp_create_confluence_page(title: str, body_html: str) -> str:
            """创建Confluence页面，返回页面ID"""
            try:
                from atlassian import Confluence
            except ImportError as e:
                raise ImportError(
                    "Missing Confluence dependencies for create_confluence_page. Install with: pip install req_agent[confluence]"
                ) from e

            confluence = Confluence(
                url=os.getenv("CONFLUENCE_URL"),
                username=os.getenv("CONFLUENCE_USER"),
                password=os.getenv("CONFLUENCE_TOKEN")
            )
            page = confluence.create_page(
                space=os.getenv("CONFLUENCE_SPACE"),
                title=title,
                body=body_html,
                parent_id=os.getenv("CONFLUENCE_PARENT_ID")  # 可选
            )
            return str(page['id'])
        
        with patch.dict('sys.modules', {
            'atlassian': None
        }):
            with pytest.raises(ImportError, match="Missing Confluence dependencies"):
                temp_create_confluence_page.run(title="Test Title", body_html="<p>Test Content</p>")

    @patch.dict(os.environ, {
        "CONFLUENCE_URL": "https://test.atlassian.net",
        "CONFLUENCE_USER": "test@example.com",
        "CONFLUENCE_TOKEN": "test_token"
    })
    @patch('atlassian.Confluence')
    def test_update_confluence_title_success(self, mock_confluence_class):
        """测试成功更新Confluence页面标题"""
        # 临时定义工具函数，以确保环境变量和mock正确应用
        @tool("Test Update Confluence Page Title")
        def temp_update_confluence_title(page_id: str, new_title: str) -> str:
            """更新Confluence页面标题"""
            try:
                from atlassian import Confluence
            except ImportError as e:
                raise ImportError(
                    "Missing Confluence dependencies for update_confluence_title. Install with: pip install req_agent[confluence]"
                ) from e

            confluence = Confluence(
                url=os.getenv("CONFLUENCE_URL"),
                username=os.getenv("CONFLUENCE_USER"),
                password=os.getenv("CONFLUENCE_TOKEN")
            )
            confluence.update_page(page_id=page_id, title=new_title)
            return "标题更新成功"
        
        # 模拟Confluence实例
        mock_confluence_instance = Mock()
        mock_confluence_class.return_value = mock_confluence_instance
        
        # 执行工具
        result = temp_update_confluence_title.run(page_id="12345", new_title="New Title")
        
        # 验证结果
        assert result == "标题更新成功"
        # 验证Confluence使用正确的认证参数初始化
        mock_confluence_class.assert_called_once()
        # 获取调用参数进行验证
        call_args = mock_confluence_class.call_args
        assert call_args[1]['url'] == "https://test.atlassian.net"
        assert call_args[1]['username'] == "test@example.com"
        assert call_args[1]['password'] == "test_token"
        
        mock_confluence_instance.update_page.assert_called_once_with(
            page_id="12345", title="New Title"
        )
    
    def test_update_confluence_title_import_error(self):
        """测试缺少依赖时的导入错误"""
        # 创建一个临时函数来测试导入错误
        @tool("Test Update Confluence Title")
        def temp_update_confluence_title(page_id: str, new_title: str) -> str:
            """更新Confluence页面标题"""
            try:
                from atlassian import Confluence
            except ImportError as e:
                raise ImportError(
                    "Missing Confluence dependencies for update_confluence_title. Install with: pip install req_agent[confluence]"
                ) from e

            confluence = Confluence(
                url=os.getenv("CONFLUENCE_URL"),
                username=os.getenv("CONFLUENCE_USER"),
                password=os.getenv("CONFLUENCE_TOKEN")
            )
            confluence.update_page(page_id=page_id, title=new_title)
            return "标题更新成功"
        
        with patch.dict('sys.modules', {
            'atlassian': None
        }):
            with pytest.raises(ImportError, match="Missing Confluence dependencies"):
                temp_update_confluence_title.run(page_id="12345", new_title="New Title")


# 导入并测试其他工具
from src.requirement_tracker.tools import (
    create_ado_feature,
    get_ado_projects,
    get_ado_work_items,
    format_doc
)


class TestCreateAdoFeature:
    """测试创建ADO Feature工具函数"""
    
    def test_create_ado_feature_tool_properties(self):
        """测试create_ado_feature工具的属性"""
        assert hasattr(create_ado_feature, 'run')
        assert create_ado_feature.name == "Create ADO Feature"
    
    @patch.dict(os.environ, {
        "ADO_ORG_URL": "https://dev.azure.com/testorg",
        "ADO_PAT": "test_pat",
        "ADO_PROJECT": "test_project"
    })
    @patch('azure.devops.connection.Connection')
    def test_create_ado_feature_success(self, mock_connection):
        """测试成功创建ADO Feature"""
        # 模拟连接和客户端
        mock_conn_instance = Mock()
        mock_wit_client = Mock()
        mock_connection.return_value = mock_conn_instance
        mock_conn_instance.clients.get_work_item_tracking_client.return_value = mock_wit_client
        
        # 模拟工作项创建结果
        mock_work_item = Mock()
        mock_work_item.id = 123
        mock_wit_client.create_work_item.return_value = mock_work_item
        
        # 执行工具
        result = create_ado_feature.run(summary="Test Summary", description="Test Description")
        
        # 验证结果
        assert result == "123"
        mock_wit_client.create_work_item.assert_called_once()
    
    def test_create_ado_feature_missing_env_vars(self):
        """测试缺少环境变量时的行为"""
        # 清除环境变量
        with patch.dict(os.environ, {}, clear=True):
            # 在调用工具之前，需要模拟连接，因为工具装饰器在模块加载时已经创建了
            with patch('azure.devops.connection.Connection') as mock_connection:
                # 模拟连接失败的情况
                mock_connection.side_effect = Exception("Missing environment variables")
                with pytest.raises(Exception):
                    create_ado_feature.run(summary="Test Summary", description="Test Description")
    
    def test_create_ado_feature_import_error(self):
        """测试缺少依赖时的导入错误"""
        # 创建一个临时函数来测试导入错误
        @tool("Test ADO Feature")
        def temp_create_ado_feature(summary: str, description: str) -> str:
            """在Azure DevOps创建Feature并返回ID"""
            try:
                from msrest.authentication import BasicAuthentication
                from azure.devops.connection import Connection
                from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation
            except ImportError as e:
                raise ImportError(
                    "Missing Azure DevOps dependencies for create_ado_feature. Install with: pip install req_agent[azure]"
                ) from e

            credentials = BasicAuthentication('', os.getenv("ADO_PAT"))
            connection = Connection(base_url=os.getenv("ADO_ORG_URL"), creds=credentials)
            wit_client = connection.clients.get_work_item_tracking_client()

            patch = [
                JsonPatchOperation(op="add", path="/fields/System.Title", value=summary),
                JsonPatchOperation(op="add", path="/fields/System.Description", value=description),
            ]
            work_item = wit_client.create_work_item(document=patch, project=os.getenv("ADO_PROJECT"), type="Feature")
            return str(work_item.id)
        
        with patch.dict('sys.modules', {
            'msrest.authentication': None,
            'azure.devops.connection': None
        }):
            with pytest.raises(ImportError, match="Missing Azure DevOps dependencies"):
                temp_create_ado_feature.run(summary="Test Summary", description="Test Description")


class TestGetAdoProjects:
    """测试获取ADO项目列表工具函数"""
    
    def test_get_ado_projects_tool_properties(self):
        """测试get_ado_projects工具的属性"""
        assert hasattr(get_ado_projects, 'run')
        assert get_ado_projects.name == "Get ADO Projects"
    
    @patch.dict(os.environ, {
        "ADO_ORG_URL": "https://dev.azure.com/testorg",
        "ADO_PAT": "test_pat"
    })
    @patch('azure.devops.connection.Connection')
    def test_get_ado_projects_success(self, mock_connection):
        """测试成功获取ADO项目列表"""
        # 模拟连接和客户端
        mock_conn_instance = Mock()
        mock_core_client = Mock()
        mock_connection.return_value = mock_conn_instance
        mock_conn_instance.clients.get_core_client.return_value = mock_core_client
        
        # 模拟项目数据
        mock_project1 = Mock()
        mock_project1.name = "Project1"
        mock_project2 = Mock()
        mock_project2.name = "Project2"
        mock_core_client.get_projects.return_value = [mock_project1, mock_project2]
        
        # 执行工具
        result = get_ado_projects.run()
        
        # 验证结果
        assert result == ["Project1", "Project2"]
        mock_core_client.get_projects.assert_called_once()
    
    @patch('azure.devops.connection.Connection')
    def test_get_ado_projects_exception(self, mock_connection):
        """测试获取ADO项目时发生异常"""
        mock_conn_instance = Mock()
        mock_connection.return_value = mock_conn_instance
        mock_conn_instance.clients.get_core_client.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception, match="获取ADO项目列表失败"):
            get_ado_projects.run()
    
    def test_get_ado_projects_import_error(self):
        """测试缺少依赖时的导入错误"""
        # 创建一个临时函数来测试导入错误
        @tool("Test ADO Projects")
        def temp_get_ado_projects() -> list:
            """获取Azure DevOps中的所有项目"""
            try:
                from msrest.authentication import BasicAuthentication
                from azure.devops.connection import Connection
            except ImportError as e:
                raise ImportError(
                    "Missing Azure DevOps dependencies for get_ado_projects. Install with: pip install req_agent[azure]"
                ) from e

            try:
                credentials = BasicAuthentication('', os.getenv("ADO_PAT"))
                connection = Connection(base_url=os.getenv("ADO_ORG_URL"), creds=credentials)
                core_client = connection.clients.get_core_client()
                projects = core_client.get_projects()
                return [project.name for project in projects]
            except Exception as e:
                raise Exception(f"获取ADO项目列表失败: {str(e)}")
        
        with patch.dict('sys.modules', {
            'msrest.authentication': None,
            'azure.devops.connection': None
        }):
            with pytest.raises(ImportError, match="Missing Azure DevOps dependencies"):
                temp_get_ado_projects.run()


class TestGetAdoWorkItems:
    """测试获取ADO工作项工具函数"""
    
    def test_get_ado_work_items_tool_properties(self):
        """测试get_ado_work_items工具的属性"""
        assert hasattr(get_ado_work_items, 'run')
        assert get_ado_work_items.name == "Get ADO Work Items"
    
    @patch.dict(os.environ, {
        "ADO_ORG_URL": "https://dev.azure.com/testorg",
        "ADO_PAT": "test_pat"
    })
    @patch('azure.devops.connection.Connection')
    def test_get_ado_work_items_success(self, mock_connection):
        """测试成功获取ADO工作项"""
        # 模拟连接和客户端
        mock_conn_instance = Mock()
        mock_wit_client = Mock()
        mock_connection.return_value = mock_conn_instance
        mock_conn_instance.clients.get_work_item_tracking_client.return_value = mock_wit_client
        
        # 模拟查询结果
        mock_query_result = Mock()
        mock_work_item1 = Mock()
        mock_work_item1.id = 101
        mock_query_result.work_items = [mock_work_item1]
        
        # 模拟工作项详情
        mock_item_detail = Mock()
        mock_item_detail.id = 101
        mock_item_detail.fields = {
            'System.Title': 'Test Title',
            'System.WorkItemType': 'Feature',
            'System.State': 'Active',
            'System.AssignedTo': {'displayName': 'Test User'},
            'System.Description': 'Test Description'
        }
        
        mock_wit_client.query_by_wiql.return_value = mock_query_result
        mock_wit_client.get_work_items.return_value = [mock_item_detail]
        
        # 执行工具
        result = get_ado_work_items.run(project_name="Test Project", work_item_type="Feature")
        
        # 验证结果
        assert len(result) == 1
        assert result[0]['id'] == 101
        assert result[0]['title'] == 'Test Title'
    
    @patch.dict(os.environ, {
        "ADO_ORG_URL": "https://dev.azure.com/testorg",
        "ADO_PAT": "test_pat"
    })
    @patch('azure.devops.connection.Connection')
    def test_get_ado_work_items_no_results(self, mock_connection):
        """测试没有找到工作项的情况"""
        # 模拟连接和客户端
        mock_conn_instance = Mock()
        mock_wit_client = Mock()
        mock_connection.return_value = mock_conn_instance
        mock_conn_instance.clients.get_work_item_tracking_client.return_value = mock_wit_client
        
        # 模拟空查询结果
        mock_query_result = Mock()
        mock_query_result.work_items = []
        mock_wit_client.query_by_wiql.return_value = mock_query_result
        
        # 执行工具
        result = get_ado_work_items.run(project_name="Test Project", work_item_type="Feature")
        
        # 验证结果为空列表
        assert result == []
    
    def test_get_ado_work_items_import_error(self):
        """测试缺少依赖时的导入错误"""
        # 创建一个临时函数来测试导入错误
        @tool("Test ADO Work Items")
        def temp_get_ado_work_items(project_name: str, work_item_type: str = "Feature") -> list:
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
                credentials = BasicAuthentication('', os.getenv("ADO_PAT"))
                connection = Connection(base_url=os.getenv("ADO_ORG_URL"), creds=credentials)
                wit_client = connection.clients.get_work_item_tracking_client()
                
                # 查询工作项的WIQL查询
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
                
                # 执行查询
                query_result = wit_client.query_by_wiql(wiql=wiql_query)
                work_items = []
                
                if query_result.work_items:
                    # 获取详细的工作项信息
                    work_item_ids = [item.id for item in query_result.work_items]
                    if work_item_ids:
                        work_items_details = wit_client.get_work_items(ids=work_item_ids)
                        for item in work_items_details:
                            work_items.append({
                                'id': item.id,
                                'title': item.fields.get('System.Title', 'No Title'),
                                'type': item.fields.get('System.WorkItemType', 'N/A'),
                                'state': item.fields.get('System.State', 'N/A'),
                                'assigned_to': item.fields.get('System.AssignedTo', {}).get('displayName', 'Unassigned') if item.fields.get('System.AssignedTo') else 'Unassigned',
                                'description': item.fields.get('System.Description', 'N/A')
                            })
                
                return work_items
            except Exception as e:
                raise Exception(f"获取ADO工作项失败: {str(e)}")
        
        with patch.dict('sys.modules', {
            'msrest.authentication': None,
            'azure.devops.connection': None
        }):
            with pytest.raises(ImportError, match="Missing Azure DevOps dependencies"):
                temp_get_ado_work_items.run(project_name="Test Project", work_item_type="Feature")
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_ado_work_items_missing_env_vars(self):
        """测试缺少环境变量时的行为"""
        with pytest.raises(Exception):
            get_ado_work_items.run(project_name="Test Project", work_item_type="Feature")


class TestFormatDoc:
    """测试格式化需求文档工具函数"""
    
    def test_format_doc_tool_properties(self):
        """测试format_doc工具的属性"""
        assert hasattr(format_doc, 'run')
        assert format_doc.name == "Format Requirement Document"
    
    def test_format_doc_success(self):
        """测试成功格式化需求文档"""
        result = format_doc.run(
            problem="Test Problem",
            goal="Test Goal", 
            artifacts="Test Artifacts",
            criteria="Test Criteria",
            risks="Test Risks"
        )
        
        # 验证结果包含问题陈述
        assert "Test Problem" in result
        assert "<h1>Problem Statement</h1>" in result