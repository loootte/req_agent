"""
测试ADO工具函数的更新版本
包含对边缘情况的测试，验证系统能否优雅处理错误
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.requirement_tracker.tools import create_ado_feature


class TestAADOToolsUpdated(unittest.TestCase):
    """测试更新后的ADO工具函数"""

    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_create_ado_feature_success(self, mock_get_connection):
        """测试创建ADO Feature成功的情况"""
        # 模拟连接和客户端
        mock_connection = MagicMock()
        mock_wit_client = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.clients.get_work_item_tracking_client.return_value = mock_wit_client
        
        # 模拟工作项创建结果
        mock_work_item = MagicMock()
        mock_work_item.id = 12345
        mock_wit_client.create_work_item.return_value = mock_work_item

        # 测试调用 - 对于Tool对象，需要使用._run方法或直接调用
        result = create_ado_feature._run(
            summary="Test Summary",
            description="Test Description",
            problem_statement="Test Problem",
            acceptance_criteria="Test Criteria"
        )

        # 验证结果
        self.assertEqual(result, "12345")
        
        # 验证调用参数
        mock_wit_client.create_work_item.assert_called_once()
        args, kwargs = mock_wit_client.create_work_item.call_args
        if args:
            document = args[0]  # patch operations
            # 验证字段设置
            field_paths = [op.path for op in document]
            self.assertIn("/fields/System.Title", field_paths)
            self.assertIn("/fields/System.Description", field_paths)
            self.assertIn("/fields/Custom.Problem", field_paths)
            self.assertIn("/fields/Custom.Acceptance", field_paths)
            self.assertIn("/fields/System.WorkItemType", field_paths)
            self.assertIn("/fields/System.AreaPath", field_paths)

    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_create_ado_feature_with_empty_problem_statement(self, mock_get_connection):
        """测试problem_statement为空时的情况"""
        # 模拟连接和客户端
        mock_connection = MagicMock()
        mock_wit_client = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.clients.get_work_item_tracking_client.return_value = mock_wit_client
        
        # 模拟工作项创建结果
        mock_work_item = MagicMock()
        mock_work_item.id = 12345
        mock_wit_client.create_work_item.return_value = mock_work_item

        # 测试调用，problem_statement为空
        result = create_ado_feature._run(
            summary="Test Summary",
            description="Test Description",
            problem_statement="",
            acceptance_criteria="Test Criteria"
        )

        # 验证结果
        self.assertEqual(result, "12345")
        
        # 验证调用参数
        mock_wit_client.create_work_item.assert_called_once()
        args, kwargs = mock_wit_client.create_work_item.call_args
        if args:
            document = args[0]  # patch operations
            # 验证字段设置 - 应该有Title, Description, Acceptance, WorkItemType, AreaPath
            # 但不应该有Problem字段，因为problem_statement为空
            field_paths = [op.path for op in document]
            self.assertIn("/fields/System.Title", field_paths)
            self.assertIn("/fields/System.Description", field_paths)
            self.assertIn("/fields/Custom.Acceptance", field_paths)
            self.assertIn("/fields/System.WorkItemType", field_paths)
            self.assertIn("/fields/System.AreaPath", field_paths)
            # 不应该包含Problem字段，因为problem_statement为空
            self.assertNotIn("/fields/Custom.Problem", field_paths)

    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_create_ado_feature_with_empty_acceptance_criteria(self, mock_get_connection):
        """测试acceptance_criteria为空时的情况"""
        # 模拟连接和客户端
        mock_connection = MagicMock()
        mock_wit_client = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.clients.get_work_item_tracking_client.return_value = mock_wit_client
        
        # 模拟工作项创建结果
        mock_work_item = MagicMock()
        mock_work_item.id = 12345
        mock_wit_client.create_work_item.return_value = mock_work_item

        # 测试调用，acceptance_criteria为空
        result = create_ado_feature._run(
            summary="Test Summary",
            description="Test Description",
            problem_statement="Test Problem",
            acceptance_criteria=""
        )

        # 验证结果
        self.assertEqual(result, "12345")
        
        # 验证调用参数
        mock_wit_client.create_work_item.assert_called_once()
        args, kwargs = mock_wit_client.create_work_item.call_args
        if args:
            document = args[0]  # patch operations
            # 验证字段设置 - 应该有Title, Description, Problem, WorkItemType, AreaPath
            # 但不应该有Acceptance字段，因为acceptance_criteria为空
            field_paths = [op.path for op in document]
            self.assertIn("/fields/System.Title", field_paths)
            self.assertIn("/fields/System.Description", field_paths)
            self.assertIn("/fields/Custom.Problem", field_paths)
            self.assertIn("/fields/System.WorkItemType", field_paths)
            self.assertIn("/fields/System.AreaPath", field_paths)
            # 不应该包含Acceptance字段，因为acceptance_criteria为空
            self.assertNotIn("/fields/Custom.Acceptance", field_paths)

    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_create_ado_feature_with_empty_description(self, mock_get_connection):
        """测试description为空时的情况"""
        # 模拟连接和客户端
        mock_connection = MagicMock()
        mock_wit_client = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.clients.get_work_item_tracking_client.return_value = mock_wit_client
        
        # 模拟工作项创建结果
        mock_work_item = MagicMock()
        mock_work_item.id = 12345
        mock_wit_client.create_work_item.return_value = mock_work_item

        # 测试调用，description为空
        result = create_ado_feature._run(
            summary="Test Summary",
            description="",
            problem_statement="Test Problem",
            acceptance_criteria="Test Criteria"
        )

        # 验证结果
        self.assertEqual(result, "12345")
        
        # 验证调用参数
        mock_wit_client.create_work_item.assert_called_once()
        args, kwargs = mock_wit_client.create_work_item.call_args
        if args:
            document = args[0]  # patch operations
            # 验证字段设置 - 应该有Title, Problem, Acceptance, WorkItemType, AreaPath
            # 但不应该有Description字段，因为description为空
            field_paths = [op.path for op in document]
            self.assertIn("/fields/System.Title", field_paths)
            self.assertIn("/fields/Custom.Problem", field_paths)
            self.assertIn("/fields/Custom.Acceptance", field_paths)
            self.assertIn("/fields/System.WorkItemType", field_paths)
            self.assertIn("/fields/System.AreaPath", field_paths)
            # 不应该包含Description字段，因为description为空
            self.assertNotIn("/fields/System.Description", field_paths)

    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_create_ado_feature_all_empty_optional_fields(self, mock_get_connection):
        """测试所有可选字段都为空时的情况"""
        # 模拟连接和客户端
        mock_connection = MagicMock()
        mock_wit_client = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.clients.get_work_item_tracking_client.return_value = mock_wit_client
        
        # 模拟工作项创建结果
        mock_work_item = MagicMock()
        mock_work_item.id = 12345
        mock_wit_client.create_work_item.return_value = mock_work_item

        # 测试调用，所有可选字段都为空
        result = create_ado_feature._run(
            summary="Test Summary",
            description="",
            problem_statement="",
            acceptance_criteria=""
        )

        # 验证结果
        self.assertEqual(result, "12345")
        
        # 验证调用参数
        mock_wit_client.create_work_item.assert_called_once()
        args, kwargs = mock_wit_client.create_work_item.call_args
        if args:
            document = args[0]  # patch operations
            # 验证字段设置 - 应该只有Title, WorkItemType, AreaPath
            field_paths = [op.path for op in document]
            self.assertIn("/fields/System.Title", field_paths)
            self.assertIn("/fields/System.WorkItemType", field_paths)
            self.assertIn("/fields/System.AreaPath", field_paths)
            # 不应该包含其他可选字段
            self.assertNotIn("/fields/System.Description", field_paths)
            self.assertNotIn("/fields/Custom.Problem", field_paths)
            self.assertNotIn("/fields/Custom.Acceptance", field_paths)

    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_create_ado_feature_import_error(self, mock_get_connection):
        """测试导入依赖失败时的情况"""
        # 模拟连接和客户端
        mock_connection = MagicMock()
        mock_wit_client = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.clients.get_work_item_tracking_client.return_value = mock_wit_client
        
        # 模拟导入错误 - 在函数内部导入时发生错误
        with patch('src.requirement_tracker.tools.get_ado_connection') as mock_get_conn:
            mock_get_conn.side_effect = ImportError("Missing dependencies")
            
            with self.assertRaises(ImportError):
                create_ado_feature._run(
                    summary="Test Summary",
                    description="Test Description",
                    problem_statement="Test Problem",
                    acceptance_criteria="Test Criteria"
                )

    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_create_ado_feature_connection_error(self, mock_get_connection):
        """测试连接失败时的情况"""
        # 模拟连接失败
        mock_get_connection.side_effect = Exception("Connection failed")
        
        with self.assertRaises(Exception):
            create_ado_feature._run(
                summary="Test Summary",
                description="Test Description",
                problem_statement="Test Problem",
                acceptance_criteria="Test Criteria"
            )


if __name__ == '__main__':
    unittest.main()