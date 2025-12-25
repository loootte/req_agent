import os
import pytest
from unittest.mock import patch, MagicMock, Mock
from crewai.tools import BaseTool as Tool, tool


class TestGetAdoConnection:
    """测试ADO连接函数"""
    
    def test_get_ado_connection_success(self):
        """测试成功获取ADO连接"""
        # 临时创建一个函数来测试，避免模块级环境变量的影响
        def temp_get_ado_connection():
            try:
                from msrest.authentication import BasicAuthentication
                from azure.devops.connection import Connection
            except ImportError as e:
                raise ImportError(
                    "Missing Azure DevOps dependencies"
                ) from e

            # 使用临时环境变量
            ado_org_url = "https://dev.azure.com/testorg"
            ado_pat = "test_pat"
            
            if not ado_pat or not ado_org_url:
                raise Exception("ADO配置不完整，请检查环境变量ADO_ORG_URL和ADO_PAT")

            credentials = BasicAuthentication('', ado_pat)
            connection = Connection(base_url=ado_org_url, creds=credentials)
            return connection
        
        # 模拟认证和连接
        with patch('msrest.authentication.BasicAuthentication') as mock_auth, \
             patch('azure.devops.connection.Connection') as mock_connection:
            
            mock_auth_instance = Mock()
            mock_auth.return_value = mock_auth_instance
            
            mock_connection_instance = Mock()
            mock_connection.return_value = mock_connection_instance
            
            # 执行函数
            result = temp_get_ado_connection()
            
            # 验证认证和连接被调用
            mock_auth.assert_called_once_with('', 'test_pat')
            mock_connection.assert_called_once_with(base_url='https://dev.azure.com/testorg', creds=mock_auth_instance)
            assert result == mock_connection_instance
    
    def test_get_ado_connection_missing_env_vars(self):
        """测试缺少环境变量时的行为"""
        # 临时创建一个函数来测试，避免模块级环境变量的影响
        def temp_get_ado_connection():
            try:
                from msrest.authentication import BasicAuthentication
                from azure.devops.connection import Connection
            except ImportError as e:
                raise ImportError(
                    "Missing Azure DevOps dependencies"
                ) from e

            # 使用临时环境变量
            ado_org_url = os.getenv("ADO_ORG_URL")
            ado_pat = os.getenv("ADO_PAT")
            
            if not ado_pat or not ado_org_url:
                raise Exception("ADO配置不完整，请检查环境变量ADO_ORG_URL和ADO_PAT")

            credentials = BasicAuthentication('', ado_pat)
            connection = Connection(base_url=ado_org_url, creds=credentials)
            return connection
        
        # 临时清除环境变量进行测试
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception, match="ADO配置不完整"):
                temp_get_ado_connection()
    
    def test_get_ado_connection_import_error(self):
        """测试ADO连接函数的导入错误"""
        # 创建一个临时函数来测试导入错误
        def temp_get_ado_connection():
            try:
                from msrest.authentication import BasicAuthentication
                from azure.devops.connection import Connection
            except ImportError as e:
                raise ImportError(
                    "Missing Azure DevOps dependencies"
                ) from e

            ado_pat = "test_pat"
            ado_org_url = "https://dev.azure.com/testorg"
            
            if not ado_pat or not ado_org_url:
                raise Exception("ADO配置不完整，请检查环境变量ADO_ORG_URL和ADO_PAT")

            credentials = BasicAuthentication('', ado_pat)
            connection = Connection(base_url=ado_org_url, creds=credentials)
            return connection
        
        with patch.dict('sys.modules', {
            'msrest.authentication': None,
            'azure.devops.connection': None
        }):
            with pytest.raises(ImportError, match="Missing Azure DevOps dependencies"):
                temp_get_ado_connection()


class TestCreateAdoFeature:
    """测试创建ADO Feature工具函数"""
    
    def test_create_ado_feature_tool_properties(self):
        """测试create_ado_feature工具的属性"""
        from src.requirement_tracker.tools import create_ado_feature
        assert hasattr(create_ado_feature, 'run')
        assert create_ado_feature.name == "Create ADO Feature"
    
    @patch.dict(os.environ, {
        "ADO_ORG_URL": "https://dev.azure.com/testorg",
        "ADO_PAT": "test_pat",
        "ADO_PROJECT": "test_project",
        "ADO_FEATURE_TYPE": "Feature"
    })
    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_create_ado_feature_success(self, mock_get_ado_connection):
        """测试成功创建ADO Feature"""
        from src.requirement_tracker.tools import create_ado_feature
        # 模拟连接和客户端
        mock_conn_instance = Mock()
        mock_wit_client = Mock()
        mock_get_ado_connection.return_value = mock_conn_instance
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

            # 使用临时连接函数避免依赖get_ado_connection
            credentials = BasicAuthentication('', os.getenv("ADO_PAT"))
            connection = Connection(base_url=os.getenv("ADO_ORG_URL"), creds=credentials)
            wit_client = connection.clients.get_work_item_tracking_client()

            patch = [
                JsonPatchOperation(op="add", path="/fields/System.Title", value=summary),
                JsonPatchOperation(op="add", path="/fields/System.Description", value=description),
            ]
            work_item = wit_client.create_work_item(document=patch, project=os.getenv("ADO_PROJECT"), type=os.getenv("ADO_FEATURE_TYPE", "Feature"))
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
        from src.requirement_tracker.tools import get_ado_projects
        assert hasattr(get_ado_projects, 'run')
        assert get_ado_projects.name == "Get ADO Projects"
    
    @patch.dict(os.environ, {
        "ADO_ORG_URL": "https://dev.azure.com/testorg",
        "ADO_PAT": "test_pat"
    })
    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_get_ado_projects_success(self, mock_get_ado_connection):
        """测试成功获取ADO项目列表"""
        from src.requirement_tracker.tools import get_ado_projects
        # 模拟连接和客户端
        mock_conn_instance = Mock()
        mock_core_client = Mock()
        mock_get_ado_connection.return_value = mock_conn_instance
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
    
    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_get_ado_projects_exception(self, mock_get_ado_connection):
        """测试获取ADO项目时发生异常"""
        from src.requirement_tracker.tools import get_ado_projects
        mock_conn_instance = Mock()
        mock_get_ado_connection.return_value = mock_conn_instance
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
                # 使用临时连接函数避免依赖get_ado_connection
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
        from src.requirement_tracker.tools import get_ado_work_items
        assert hasattr(get_ado_work_items, 'run')
        assert get_ado_work_items.name == "Get ADO Work Items"
    
    @patch.dict(os.environ, {
        "ADO_ORG_URL": "https://dev.azure.com/testorg",
        "ADO_PAT": "test_pat"
    })
    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_get_ado_work_items_success(self, mock_get_ado_connection):
        """测试成功获取ADO工作项"""
        from src.requirement_tracker.tools import get_ado_work_items
        # 模拟连接和客户端
        mock_conn_instance = Mock()
        mock_wit_client = Mock()
        mock_get_ado_connection.return_value = mock_conn_instance
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
    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_get_ado_work_items_no_results(self, mock_get_ado_connection):
        """测试没有找到工作项的情况"""
        from src.requirement_tracker.tools import get_ado_work_items
        # 模拟连接和客户端
        mock_conn_instance = Mock()
        mock_wit_client = Mock()
        mock_get_ado_connection.return_value = mock_conn_instance
        mock_conn_instance.clients.get_work_item_tracking_client.return_value = mock_wit_client
        
        # 模拟空查询结果
        mock_query_result = Mock()
        mock_query_result.work_items = []
        mock_wit_client.query_by_wiql.return_value = mock_query_result
        
        # 执行工具
        result = get_ado_work_items.run(project_name="Test Project", work_item_type="Feature")
        
        # 验证结果为空列表
        assert result == []
    
    @patch.dict(os.environ, {
        "ADO_ORG_URL": "https://dev.azure.com/testorg",
        "ADO_PAT": "test_pat"
    })
    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_get_ado_work_items_batch_processing(self, mock_get_ado_connection):
        """测试批量处理大量工作项的情况"""
        from src.requirement_tracker.tools import get_ado_work_items
        # 模拟连接和客户端
        mock_conn_instance = Mock()
        mock_wit_client = Mock()
        mock_get_ado_connection.return_value = mock_conn_instance
        mock_conn_instance.clients.get_work_item_tracking_client.return_value = mock_wit_client
        
        # 模拟大量工作项（超过批量大小）
        work_items = []
        for i in range(300):  # 创建300个工作项，超过200的批量大小
            mock_work_item = Mock()
            mock_work_item.id = 1000 + i
            work_items.append(mock_work_item)
        
        mock_query_result = Mock()
        mock_query_result.work_items = work_items
        mock_wit_client.query_by_wiql.return_value = mock_query_result
        
        # 模拟批量获取工作项详情
        batch1_items = []
        for i in range(200):  # 第一批
            mock_item = Mock()
            mock_item.id = 1000 + i
            mock_item.fields = {
                'System.Title': f'Test Title {i}',
                'System.WorkItemType': 'Feature',
                'System.State': 'Active',
                'System.AssignedTo': {'displayName': 'Test User'},
                'System.Description': f'Test Description {i}'
            }
            batch1_items.append(mock_item)
        
        batch2_items = []
        for i in range(200, 300):  # 第二批
            mock_item = Mock()
            mock_item.id = 1000 + i
            mock_item.fields = {
                'System.Title': f'Test Title {i}',
                'System.WorkItemType': 'Feature',
                'System.State': 'Active',
                'System.AssignedTo': {'displayName': 'Test User'},
                'System.Description': f'Test Description {i}'
            }
            batch2_items.append(mock_item)
        
        mock_wit_client.get_work_items.side_effect = [batch1_items, batch2_items]
        
        # 执行工具
        result = get_ado_work_items.run(project_name="Test Project", work_item_type="Feature")
        
        # 验证结果
        assert len(result) == 300
        mock_wit_client.get_work_items.assert_called()


class TestGetAreaPaths:
    """测试获取ADO Area路径工具函数"""
    
    def test_get_area_paths_tool_properties(self):
        """测试get_area_paths工具的属性"""
        from src.requirement_tracker.tools import get_area_paths
        assert hasattr(get_area_paths, 'run')
        assert get_area_paths.name == "Get ADO Area Paths"
    
    @patch.dict(os.environ, {
        "ADO_ORG_URL": "https://dev.azure.com/testorg",
        "ADO_PAT": "test_pat"
    })
    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_get_area_paths_success(self, mock_get_ado_connection):
        """测试成功获取ADO Area路径"""
        from src.requirement_tracker.tools import get_area_paths
        # 模拟连接和客户端
        mock_conn_instance = Mock()
        mock_wit_client = Mock()
        mock_get_ado_connection.return_value = mock_conn_instance
        mock_conn_instance.clients.get_work_item_tracking_client.return_value = mock_wit_client
        
        # 模拟Area分类节点数据
        mock_area_root = Mock()
        mock_area_root.name = "RootArea"
        mock_area_root.id = "1"
        
        # 模拟子节点
        mock_child1 = Mock()
        mock_child1.name = "Child1"
        mock_child1.id = "2"
        mock_child2 = Mock()
        mock_child2.name = "Child2"
        mock_child2.id = "3"
        
        mock_child1.children = []
        mock_child2.children = []
        mock_area_root.children = [mock_child1, mock_child2]
        
        mock_wit_client.get_classification_node.return_value = mock_area_root
        
        # 执行工具
        result = get_area_paths.run(project_name="Test Project")
        
        # 验证结果
        assert len(result) > 0
        mock_wit_client.get_classification_node.assert_called_once_with(
            project="Test Project",
            structure_group='areas',
            depth=100
        )
    
    @patch.dict(os.environ, {
        "ADO_ORG_URL": "https://dev.azure.com/testorg",
        "ADO_PAT": "test_pat"
    })
    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_get_area_paths_no_children(self, mock_get_ado_connection):
        """测试没有子节点的情况"""
        from src.requirement_tracker.tools import get_area_paths
        # 模拟连接和客户端
        mock_conn_instance = Mock()
        mock_wit_client = Mock()
        mock_get_ado_connection.return_value = mock_conn_instance
        mock_conn_instance.clients.get_work_item_tracking_client.return_value = mock_wit_client
        
        # 模拟Area分类节点数据（没有子节点）
        mock_area_root = Mock()
        mock_area_root.name = "RootArea"
        mock_area_root.id = "1"
        mock_area_root.children = None  # 没有子节点
        
        mock_wit_client.get_classification_node.return_value = mock_area_root
        
        # 执行工具
        result = get_area_paths.run(project_name="Test Project")
        
        # 验证结果
        assert len(result) == 1  # 应该返回根节点本身
        assert result[0]['name'] == "RootArea"
        mock_wit_client.get_classification_node.assert_called_once_with(
            project="Test Project",
            structure_group='areas',
            depth=100
        )
    
    def test_get_area_paths_import_error(self):
        """测试缺少依赖时的导入错误"""
        # 创建一个临时函数来测试导入错误
        @tool("Test ADO Area Paths")
        def temp_get_area_paths(project_name: str) -> list:
            """获取指定项目的所有Area路径"""
            try:
                from msrest.authentication import BasicAuthentication
                from azure.devops.connection import Connection
            except ImportError as e:
                raise ImportError(
                    "Missing Azure DevOps dependencies for get_area_paths. Install with: pip install req_agent[azure]"
                ) from e

            try:
                # 使用临时连接函数避免依赖get_ado_connection
                credentials = BasicAuthentication('', os.getenv("ADO_PAT"))
                connection = Connection(base_url=os.getenv("ADO_ORG_URL"), creds=credentials)
                
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
        
        with patch.dict('sys.modules', {
            'msrest.authentication': None,
            'azure.devops.connection': None
        }):
            with pytest.raises(ImportError, match="Missing Azure DevOps dependencies"):
                temp_get_area_paths.run(project_name="Test Project")


class TestGetAdoWorkItemsWithArea:
    """测试获取ADO工作项（支持Area过滤）工具函数"""
    
    def test_get_ado_work_items_with_area_tool_properties(self):
        """测试get_ado_work_items_with_area工具的属性"""
        from src.requirement_tracker.tools import get_ado_work_items_with_area
        assert hasattr(get_ado_work_items_with_area, 'run')
        assert get_ado_work_items_with_area.name == "Get ADO Work Items with Area Filter"
    
    @patch.dict(os.environ, {
        "ADO_ORG_URL": "https://dev.azure.com/testorg",
        "ADO_PAT": "test_pat"
    })
    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_get_ado_work_items_with_area_success(self, mock_get_ado_connection):
        """测试成功获取ADO工作项（带Area过滤）"""
        from src.requirement_tracker.tools import get_ado_work_items_with_area
        # 模拟连接和客户端
        mock_conn_instance = Mock()
        mock_wit_client = Mock()
        mock_get_ado_connection.return_value = mock_conn_instance
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
            'System.AreaPath': 'TestArea',
            'System.AssignedTo': {'displayName': 'Test User'},
            'System.Description': 'Test Description'
        }
        
        mock_wit_client.query_by_wiql.return_value = mock_query_result
        mock_wit_client.get_work_items.return_value = [mock_item_detail]
        
        # 执行工具
        result = get_ado_work_items_with_area.run(
            project_name="Test Project", 
            work_item_type="Feature",
            area_path="TestArea"
        )
        
        # 验证结果
        assert len(result) == 1
        assert result[0]['id'] == 101
        assert result[0]['title'] == 'Test Title'
        assert result[0]['area_path'] == 'TestArea'
    
    @patch.dict(os.environ, {
        "ADO_ORG_URL": "https://dev.azure.com/testorg",
        "ADO_PAT": "test_pat"
    })
    @patch('src.requirement_tracker.tools.get_ado_connection')
    def test_get_ado_work_items_with_area_no_area_filter(self, mock_get_ado_connection):
        """测试没有Area过滤的获取ADO工作项"""
        from src.requirement_tracker.tools import get_ado_work_items_with_area
        # 模拟连接和客户端
        mock_conn_instance = Mock()
        mock_wit_client = Mock()
        mock_get_ado_connection.return_value = mock_conn_instance
        mock_conn_instance.clients.get_work_item_tracking_client.return_value = mock_wit_client
        
        # 模拟查询结果
        mock_query_result = Mock()
        mock_work_item1 = Mock()
        mock_query_result.work_items = [mock_work_item1]
        
        # 模拟工作项详情
        mock_item_detail = Mock()
        mock_item_detail.id = 101
        mock_item_detail.fields = {
            'System.Title': 'Test Title',
            'System.WorkItemType': 'Feature',
            'System.State': 'Active',
            'System.AreaPath': 'TestArea',
            'System.AssignedTo': {'displayName': 'Test User'},
            'System.Description': 'Test Description'
        }
        
        mock_wit_client.query_by_wiql.return_value = mock_query_result
        mock_wit_client.get_work_items.return_value = [mock_item_detail]
        
        # 执行工具，不指定Area过滤
        result = get_ado_work_items_with_area.run(
            project_name="Test Project", 
            work_item_type="Feature"
        )
        
        # 验证结果
        assert len(result) == 1
        assert result[0]['id'] == 101
        assert result[0]['title'] == 'Test Title'
    
    def test_get_ado_work_items_with_area_import_error(self):
        """测试缺少依赖时的导入错误"""
        # 创建一个临时函数来测试导入错误
        @tool("Test ADO Work Items with Area Filter")
        def temp_get_ado_work_items_with_area(project_name: str, work_item_type: str = "Feature", area_path: str = None) -> list:
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
                # 使用临时连接函数避免依赖get_ado_connection
                credentials = BasicAuthentication('', os.getenv("ADO_PAT"))
                connection = Connection(base_url=os.getenv("ADO_ORG_URL"), creds=credentials)
                wit_client = connection.clients.get_work_item_tracking_client()
                
                # 构建查询条件
                where_clause = f"[System.TeamProject] = '{project_name.replace("'", "''")}' AND [System.WorkItemType] = '{work_item_type.replace("'", "''")}'"
                
                # 如果指定了Area，则添加Area过滤条件
                if area_path:
                    escaped_area_path = area_path.replace("'", "''")
                    where_clause += f" AND [System.AreaPath] = '{escaped_area_path}'"
                
                # 查询工作项的WIQL查询
                query_str = f"""
                    SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType], [System.AssignedTo], [System.AreaPath], [System.Description]
                    FROM WorkItems
                    WHERE {where_clause}
                    ORDER BY [System.Id] DESC
                    """
                wiql_query = Wiql(
                    query=query_str
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
                raise Exception(f"获取ADO工作项失败: {str(e)}")
        
        with patch.dict('sys.modules', {
            'msrest.authentication': None,
            'azure.devops.connection': None
        }):
            with pytest.raises(ImportError, match="Missing Azure DevOps dependencies"):
                temp_get_ado_work_items_with_area.run(
                    project_name="Test Project",
                    work_item_type="Feature",
                    area_path="TestArea"
                )