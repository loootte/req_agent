"""
端到端集成测试：测试通过agent从文本创建ADO workitem和Confluence Page的过程
使用.env中的真实配置，测试完成后删除测试数据
"""
import unittest
import os
from pathlib import Path
import sys

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.requirement_tracker.crew import run_crew
from src.requirement_tracker.tools import (
    create_ado_feature, 
    create_confluence_page, 
    get_ado_connection,
    get_confluence_spaces,
    get_ado_projects,
    delete_ado_workitem,
    delete_confluence_page
)
from dotenv import load_dotenv

# 标记此测试为端到端测试，以排除在常规pipeline测试之外
import pytest
pytestmark = pytest.mark.e2e

class TestE2EADOConfluenceIntegration(unittest.TestCase):
    """端到端集成测试：验证从文本到ADO工作项和Confluence页面的完整流程"""

    @classmethod
    def setUpClass(cls):
        """在所有测试开始前加载环境变量"""
        load_dotenv()
        
        # 验证必要的环境变量
        required_vars = [
            'DASHSCOPE_API_KEY',
            'CONFLUENCE_URL',
            'CONFLUENCE_USER',
            'CONFLUENCE_TOKEN',
            'CONFLUENCE_SPACE',
            'ADO_ORG_URL',
            'ADO_PAT',
            'ADO_PROJECT'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise EnvironmentError(f"缺少必要的环境变量: {missing_vars}")

    def setUp(self):
        """设置测试环境"""
        # 设置模型类型
        os.environ['SELECTED_MODEL'] = 'qwen'
        
        # 存储要清理的测试数据ID
        self.test_ado_workitem_ids = []
        self.test_confluence_page_ids = []

    def test_e2e_create_ado_feature_and_confluence_page(self):
        """端到端测试：创建ADO工作项和Confluence页面"""
        # 验证连接
        try:
            # 尝试获取ADO连接
            connection_result = get_ado_connection._run() if hasattr(get_ado_connection, '_run') else get_ado_connection()
            # 尝试获取Confluence空间
            spaces_result = get_confluence_spaces._run() if hasattr(get_confluence_spaces, '_run') else get_confluence_spaces()
            self.assertGreater(len(spaces_result), 0, "无法获取Confluence空间")
        except Exception as e:
            self.skipTest(f"连接验证失败: {e}")

        # 测试输入
        test_input = "创建一个自动化需求分析工具，用于分析用户需求并生成文档"
        
        # 运行端到端流程
        result = run_crew(test_input, "qwen")
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertNotIn("Error", result)

    def test_create_ado_feature_integration(self):
        """集成测试：直接创建ADO工作项"""
        try:
            # 验证ADO连接
            connection_result = get_ado_connection._run() if hasattr(get_ado_connection, '_run') else get_ado_connection()
            core_client = connection_result.clients.get_core_client()
            projects = core_client.get_projects()
            project_found = any(p.name == os.getenv('ADO_PROJECT') for p in projects)
            if not project_found:
                self.skipTest("指定的ADO项目不存在")
        except Exception as e:
            self.skipTest(f"ADO连接失败: {e}")
        
        # 创建测试ADO工作项 - 使用Tool对象的_run方法
        summary = "E2E测试工作项 - 请勿删除"
        description = "这是一个端到端测试创建的工作项，测试完成后将被删除"
        problem_statement = "需要进行端到端集成测试"
        acceptance_criteria = "工作项应成功创建并包含所有必要字段"
        
        workitem_id = create_ado_feature._run(
            summary=summary,
            description=description,
            problem_statement=problem_statement,
            acceptance_criteria=acceptance_criteria
        )
        
        # 记录ID以便清理
        self.test_ado_workitem_ids.append(workitem_id)
        
        # 验证工作项ID
        self.assertTrue(workitem_id.isdigit(), f"返回的工作项ID无效: {workitem_id}")
        
        # 验证工作项确实存在
        from src.requirement_tracker.tools import get_ado_work_items
        work_items = get_ado_work_items._run(project_name=os.getenv('ADO_PROJECT'), work_item_type='Feature')
        found_workitem = any(item['id'] == int(workitem_id) for item in work_items)
        self.assertTrue(found_workitem, f"工作项 {workitem_id} 在创建后未找到")

    def test_create_confluence_page_integration(self):
        """集成测试：直接创建Confluence页面"""
        try:
            # 验证Confluence连接
            spaces_result = get_confluence_spaces._run() if hasattr(get_confluence_spaces, '_run') else get_confluence_spaces()
            space_key = os.getenv('CONFLUENCE_SPACE')
            space_found = any(s['key'] == space_key for s in spaces_result)
            if not space_found:
                self.skipTest(f"Confluence空间 {space_key} 不存在")
        except Exception as e:
            self.skipTest(f"Confluence连接失败: {e}")
        
        # 创建测试Confluence页面 - 使用Tool对象的_run方法
        title = "E2E测试页面 - 请勿删除"
        body_html = """
        <h1>端到端测试页面</h1>
        <p>这是一个端到端测试创建的页面，测试完成后将被删除</p>
        <p>测试内容：验证Confluence页面创建功能</p>
        """
        
        page_id = create_confluence_page._run(title=title, body_html=body_html)
        
        # 记录ID以便清理
        self.test_confluence_page_ids.append(page_id)
        
        # 验证页面ID
        self.assertTrue(page_id.isdigit(), f"返回的页面ID无效: {page_id}")
        
        # 验证页面确实存在
        from src.requirement_tracker.tools import get_confluence_page_content
        page_content = get_confluence_page_content._run(page_id=page_id)
        self.assertIsNotNone(page_content, f"页面 {page_id} 在创建后未找到")

    @unittest.skip("跳过完整端到端测试，因为需要真实API调用和数据清理功能")
    def test_full_e2e_workflow(self):
        """完整端到端工作流测试（需要真实API调用）"""
        # 这个测试需要完整的工作流实现和数据清理功能
        test_input = "开发一个需求跟踪系统，包含需求分析、任务分配和进度跟踪功能"
        
        result = run_crew(test_input, "qwen")
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertNotIn("Error", result)

    def tearDown(self):
        """清理测试数据"""
        # 清理创建的ADO工作项
        for workitem_id in self.test_ado_workitem_ids:
            try:
                result = delete_ado_workitem._run(workitem_id=workitem_id)
                print(f"已清理ADO工作项 {workitem_id}: {result}")
            except Exception as e:
                print(f"清理ADO工作项 {workitem_id} 失败: {e}")
        
        # 清理创建的Confluence页面
        for page_id in self.test_confluence_page_ids:
            try:
                result = delete_confluence_page._run(page_id=page_id)
                print(f"已清理Confluence页面 {page_id}: {result}")
            except Exception as e:
                print(f"清理Confluence页面 {page_id} 失败: {e}")
        
        print(f"测试完成，尝试清理了 {len(self.test_ado_workitem_ids)} 个ADO工作项和 {len(self.test_confluence_page_ids)} 个Confluence页面")

    @classmethod
    def tearDownClass(cls):
        """在所有测试结束后执行清理"""
        print("所有端到端测试完成")


if __name__ == '__main__':
    unittest.main()