"""
测试tools.py中的边缘情况和异常处理，以提高测试覆盖率
"""
import unittest
from unittest.mock import patch, MagicMock
import os


class TestToolsEdgeCases(unittest.TestCase):
    """测试tools.py中的边缘情况和异常处理"""

    def setUp(self):
        """设置测试环境"""
        # 保存原始环境变量
        self.original_env = {
            'ADO_PAT': os.getenv('ADO_PAT'),
            'ADO_ORG_URL': os.getenv('ADO_ORG_URL'),
            'CONFLUENCE_URL': os.getenv('CONFLUENCE_URL'),
            'CONFLUENCE_USER': os.getenv('CONFLUENCE_USER'),
            'CONFLUENCE_TOKEN': os.getenv('CONFLUENCE_TOKEN'),
            'CONFLUENCE_SPACE': os.getenv('CONFLUENCE_SPACE'),
        }

    def tearDown(self):
        """清理测试环境"""
        # 恢复原始环境变量
        for key, value in self.original_env.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]

    @patch('src.requirement_tracker.tools.ADO_PAT', '')
    @patch('src.requirement_tracker.tools.ADO_ORG_URL', '')
    def test_get_ado_connection_missing_config(self):
        """测试ADO连接配置缺失的情况"""
        from src.requirement_tracker.tools import get_ado_connection
        
        with self.assertRaises(Exception) as context:
            get_ado_connection()
        
        self.assertIn("ADO配置不完整", str(context.exception))

    @patch.dict(os.environ, {
        'ADO_PAT': 'test_pat',
        'ADO_ORG_URL': 'https://dev.azure.com/testorg'
    })
    def test_get_ado_connection_import_error(self):
        """测试ADO连接时的导入错误"""
        from src.requirement_tracker.tools import get_ado_connection

        with patch.dict('sys.modules', {
            'msrest.authentication': None,
            'azure.devops.connection': None
        }):
            with self.assertRaises(ImportError) as context:
                get_ado_connection()
            self.assertIn("Missing Azure DevOps dependencies", str(context.exception))

    @patch.dict(os.environ, {
        'ADO_PAT': 'test_pat',
        'ADO_ORG_URL': 'https://dev.azure.com/testorg'
    })
    def test_get_ado_projects_import_error(self):
        """测试ADO项目获取时的导入错误"""
        from src.requirement_tracker.tools import get_ado_projects

        with patch.dict('sys.modules', {
            'msrest.authentication': None,
            'azure.devops.connection': None
        }):
            with self.assertRaises(ImportError) as context:
                get_ado_projects._run()
            self.assertIn("Missing Azure DevOps dependencies", str(context.exception))

    @patch.dict(os.environ, {
        'ADO_PAT': 'test_pat',
        'ADO_ORG_URL': 'https://dev.azure.com/testorg'
    })
    def test_get_ado_work_items_import_error(self):
        """测试获取ADO工作项时的导入错误"""
        from src.requirement_tracker.tools import get_ado_work_items

        with patch.dict('sys.modules', {
            'msrest.authentication': None,
            'azure.devops.connection': None,
            'azure.devops.v7_1.work_item_tracking.models': None
        }):
            with self.assertRaises(ImportError) as context:
                get_ado_work_items._run(project_name="Test Project")
            self.assertIn("Missing Azure DevOps dependencies", str(context.exception))

    def test_get_confluence_spaces_import_error(self):
        """测试获取Confluence空间时的导入错误"""
        from src.requirement_tracker.tools import get_confluence_spaces

        with patch.dict('sys.modules', {
            'atlassian': None
        }):
            with self.assertRaises(ImportError) as context:
                get_confluence_spaces._run()
            self.assertIn("Missing Confluence dependencies", str(context.exception))

    def test_create_confluence_page_import_error(self):
        """测试创建Confluence页面时的导入错误"""
        from src.requirement_tracker.tools import create_confluence_page

        with patch.dict('sys.modules', {
            'atlassian': None
        }):
            with self.assertRaises(ImportError) as context:
                create_confluence_page._run(title="Test", body_html="<p>Test</p>")
            self.assertIn("Missing Confluence dependencies", str(context.exception))

    def test_get_confluence_pages_import_error(self):
        """测试获取Confluence页面时的导入错误"""
        from src.requirement_tracker.tools import get_confluence_pages

        with patch.dict('sys.modules', {
            'atlassian': None
        }):
            with self.assertRaises(ImportError) as context:
                get_confluence_pages._run(space_key="TEST")
            self.assertIn("Missing Confluence dependencies", str(context.exception))

    def test_get_confluence_page_content_import_error(self):
        """测试获取Confluence页面内容时的导入错误"""
        from src.requirement_tracker.tools import get_confluence_page_content

        with patch.dict('sys.modules', {
            'atlassian': None
        }):
            with self.assertRaises(ImportError) as context:
                get_confluence_page_content._run(page_id="12345")
            self.assertIn("Missing Confluence dependencies", str(context.exception))

    def test_delete_confluence_page_import_error(self):
        """测试删除Confluence页面时的导入错误"""
        from src.requirement_tracker.tools import delete_confluence_page

        with patch.dict('sys.modules', {
            'atlassian': None
        }):
            with self.assertRaises(ImportError) as context:
                delete_confluence_page._run(page_id="12345")
            self.assertIn("Missing Confluence dependencies", str(context.exception))

    def test_delete_ado_workitem_import_error(self):
        """测试删除ADO工作项时的导入错误"""
        from src.requirement_tracker.tools import delete_ado_workitem

        with patch.dict('sys.modules', {
            'msrest.authentication': None,
            'azure.devops.connection': None,
            'azure.devops.exceptions': None
        }):
            with self.assertRaises(ImportError) as context:
                delete_ado_workitem._run(workitem_id="12345")
            self.assertIn("Missing Azure DevOps dependencies", str(context.exception))

    @patch.dict(os.environ, {
        'ADO_PAT': 'test_pat',
        'ADO_ORG_URL': 'https://dev.azure.com/testorg'
    })
    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_get_ado_projects_exception(self, mock_get_ado_connection):
        """测试ADO项目获取时的异常"""
        from src.requirement_tracker.tools import get_ado_projects

        # 模拟连接和客户端异常
        mock_conn_instance = MagicMock()
        mock_core_client = MagicMock()
        mock_get_ado_connection.return_value = mock_conn_instance
        mock_conn_instance.clients.get_core_client.return_value = mock_core_client
        mock_core_client.get_projects.side_effect = Exception("Connection failed")

        with self.assertRaises(Exception) as context:
            get_ado_projects._run()
        self.assertIn("获取ADO项目列表失败", str(context.exception))

    @patch.dict(os.environ, {
        'ADO_PAT': 'test_pat',
        'ADO_ORG_URL': 'https://dev.azure.com/testorg'
    })
    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_get_ado_work_items_exception(self, mock_get_ado_connection):
        """测试获取ADO工作项时的异常"""
        from src.requirement_tracker.tools import get_ado_work_items

        # 模拟连接和客户端异常
        mock_conn_instance = MagicMock()
        mock_wit_client = MagicMock()
        mock_get_ado_connection.return_value = mock_conn_instance
        mock_conn_instance.clients.get_work_item_tracking_client.return_value = mock_wit_client
        mock_wit_client.query_by_wiql.side_effect = Exception("Query failed")

        with self.assertRaises(Exception) as context:
            get_ado_work_items._run(project_name="Test Project")
        self.assertIn("获取ADO工作项失败", str(context.exception))

    @patch.dict(os.environ, {
        'ADO_PAT': 'test_pat',
        'ADO_ORG_URL': 'https://dev.azure.com/testorg'
    })
    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_get_ado_work_items_with_area_import_error(self, mock_get_ado_connection):
        """测试获取ADO工作项(带Area过滤)时的导入错误"""
        from src.requirement_tracker.tools import get_ado_work_items_with_area

        with patch.dict('sys.modules', {
            'msrest.authentication': None,
            'azure.devops.connection': None,
            'azure.devops.v7_1.work_item_tracking.models': None
        }):
            with self.assertRaises(ImportError) as context:
                get_ado_work_items_with_area._run(project_name="Test Project", work_item_type="Feature")
            self.assertIn("Missing Azure DevOps dependencies", str(context.exception))

    @patch.dict(os.environ, {
        'ADO_PAT': 'test_pat',
        'ADO_ORG_URL': 'https://dev.azure.com/testorg'
    })
    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_get_ado_work_items_with_area_exception(self, mock_get_ado_connection):
        """测试获取ADO工作项(带Area过滤)时的异常"""
        from src.requirement_tracker.tools import get_ado_work_items_with_area

        # 模拟连接和客户端异常
        mock_conn_instance = MagicMock()
        mock_wit_client = MagicMock()
        mock_get_ado_connection.return_value = mock_conn_instance
        mock_conn_instance.clients.get_work_item_tracking_client.return_value = mock_wit_client
        mock_wit_client.query_by_wiql.side_effect = Exception("Query failed")

        with self.assertRaises(Exception) as context:
            get_ado_work_items_with_area._run(project_name="Test Project", work_item_type="Feature")
        self.assertIn("获取ADO工作项失败", str(context.exception))

    @patch.dict(os.environ, {
        'CONFLUENCE_URL': 'https://test.atlassian.net',
        'CONFLUENCE_USER': 'test@example.com',
        'CONFLUENCE_TOKEN': 'test_token',
        'CONFLUENCE_SPACE': 'TEST'
    })
    def test_get_confluence_spaces_exception(self):
        """测试获取Confluence空间时的异常"""
        from src.requirement_tracker.tools import get_confluence_spaces

        # 模拟Confluence实例和异常
        with patch('atlassian.Confluence') as mock_confluence_class:
            mock_confluence_instance = MagicMock()
            mock_confluence_class.return_value = mock_confluence_instance
            mock_confluence_instance.get_all_spaces.side_effect = Exception("Connection failed")

            with self.assertRaises(Exception) as context:
                get_confluence_spaces._run()
            self.assertIn("获取Confluence空间列表失败", str(context.exception))

    @patch.dict(os.environ, {
        'CONFLUENCE_URL': 'https://test.atlassian.net',
        'CONFLUENCE_USER': 'test@example.com',
        'CONFLUENCE_TOKEN': 'test_token',
        'CONFLUENCE_SPACE': 'TEST'
    })
    def test_get_confluence_pages_exception(self):
        """测试获取Confluence页面时的异常"""
        from src.requirement_tracker.tools import get_confluence_pages

        # 模拟Confluence实例和异常
        with patch('atlassian.Confluence') as mock_confluence_class:
            mock_confluence_instance = MagicMock()
            mock_confluence_class.return_value = mock_confluence_instance
            mock_confluence_instance.get_all_pages_from_space.side_effect = Exception("Connection failed")

            with self.assertRaises(Exception) as context:
                get_confluence_pages._run(space_key="TEST")
            self.assertIn("获取空间 TEST 的页面列表失败", str(context.exception))

    @patch.dict(os.environ, {
        'CONFLUENCE_URL': 'https://test.atlassian.net',
        'CONFLUENCE_USER': 'test@example.com',
        'CONFLUENCE_TOKEN': 'test_token',
        'CONFLUENCE_SPACE': 'TEST'
    })
    def test_create_confluence_page_exception(self):
        """测试创建Confluence页面时的异常"""
        from src.requirement_tracker.tools import create_confluence_page

        # 模拟Confluence实例和异常
        with patch('atlassian.Confluence') as mock_confluence_class:
            mock_confluence_instance = MagicMock()
            mock_confluence_class.return_value = mock_confluence_instance
            mock_confluence_instance.create_page.side_effect = Exception("Create failed")

            with self.assertRaises(Exception):
                create_confluence_page._run(title="Test", body_html="<p>Test</p>")

    @patch.dict(os.environ, {
        'CONFLUENCE_URL': 'https://test.atlassian.net',
        'CONFLUENCE_USER': 'test@example.com',
        'CONFLUENCE_TOKEN': 'test_token',
        'CONFLUENCE_SPACE': 'TEST'
    })
    def test_delete_confluence_page_exception(self):
        """测试删除Confluence页面时的异常"""
        from src.requirement_tracker.tools import delete_confluence_page

        # 模拟Confluence实例和异常
        with patch('atlassian.Confluence') as mock_confluence_class:
            mock_confluence_instance = MagicMock()
            mock_confluence_class.return_value = mock_confluence_instance
            mock_confluence_instance.remove_page.side_effect = Exception("Delete failed")

            with self.assertRaises(Exception):
                delete_confluence_page._run(page_id="12345")

    @patch.dict(os.environ, {
        'ADO_PAT': 'test_pat',
        'ADO_ORG_URL': 'https://dev.azure.com/testorg',
        'ADO_PROJECT': 'Test Project'
    })
    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_delete_ado_workitem_exception(self, mock_get_ado_connection):
        """测试删除ADO工作项时的异常"""
        from src.requirement_tracker.tools import delete_ado_workitem

        # 模拟连接和客户端异常
        mock_conn_instance = MagicMock()
        mock_wit_client = MagicMock()
        mock_get_ado_connection.return_value = mock_conn_instance
        mock_conn_instance.clients.get_work_item_tracking_client.return_value = mock_wit_client
        mock_wit_client.delete_work_item.side_effect = Exception("Delete failed")

        with self.assertRaises(Exception):
            delete_ado_workitem._run(workitem_id="12345")

    @patch.dict(os.environ, {
        'ADO_PAT': 'test_pat',
        'ADO_ORG_URL': 'https://dev.azure.com/testorg',
        'ADO_PROJECT': 'Test Project'
    })
    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_delete_ado_workitem_azure_exception(self, mock_get_ado_connection):
        """测试删除ADO工作项时的Azure异常，触发更新状态的备选路径"""
        from src.requirement_tracker.tools import delete_ado_workitem
        
        # 模拟连接和客户端
        mock_conn_instance = MagicMock()
        mock_wit_client = MagicMock()
        mock_get_ado_connection.return_value = mock_conn_instance
        mock_conn_instance.clients.get_work_item_tracking_client.return_value = mock_wit_client
        
        # 首次删除抛出异常，触发备选路径
        mock_wit_client.delete_work_item.side_effect = Exception("Delete not allowed")
        
        # 备选路径中的更新操作也抛出异常
        mock_wit_client.update_work_item.side_effect = Exception("Update failed")

        with self.assertRaises(Exception):
            delete_ado_workitem._run(workitem_id="12345")

    def test_format_doc_with_special_characters(self):
        """测试格式化文档工具处理特殊字符"""
        from src.requirement_tracker.tools import format_doc

        result = format_doc._run(
            problem="Test problem with <html> tags",
            goal="Test goal with & special characters",
            artifacts="Test artifacts",
            criteria="Test criteria",
            risks="Test risks"
        )
        
        self.assertIn("Test problem with <html> tags", result)
        # format_doc工具只处理problem字段，所以只检查problem部分


if __name__ == '__main__':
    unittest.main()