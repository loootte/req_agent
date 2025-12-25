"""
Azure DevOps (ADO) 浏览器模块
用于在Web界面中显示ADO项目和工作项信息
"""
import os
import streamlit as st
from azure.devops.v7_1.work_item_tracking.models import Wiql
from openai import project

from .tools import get_ado_connection  # 导入通用的ADO连接函数


def get_projects():
    """获取所有ADO项目，直接使用Azure DevOps SDK"""
    try:
        connection = get_ado_connection()
    except Exception as e:
        st.error(str(e))
        add_log(str(e), "ERROR")
        return []
    
    try:
        core_client = connection.clients.get_core_client()
        projects = core_client.get_projects()
        project_names = [project.name for project in projects]
        add_log(f"成功获取 {len(project_names)} 个ADO项目", "INFO")
        return project_names
    except Exception as e:
        st.error(f"获取项目列表失败: {str(e)}")
        add_log(f"获取项目列表失败: {str(e)}", "ERROR")
        return []


def get_areas(project_name):
    """获取指定项目的所有Area，直接使用Azure DevOps SDK"""
    try:
        connection = get_ado_connection()
    except Exception as e:
        st.error(str(e))
        add_log(str(e), "ERROR")
        return []
    
    try:
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
            all_areas = []
            if hasattr(area_root, 'children') and area_root.children:
                for child in area_root.children:
                    all_areas.extend(extract_areas(child))
            elif area_root.name:  # 如果没有子节点，返回根节点本身
                all_areas.append({
                    'name': area_root.name,
                    'path': area_root.name,
                    'id': area_root.id
                })
            
            # 提取Area路径列表
            areas = [area['path'] for area in all_areas]
            
            add_log(f"成功获取项目 {project_name} 的 {len(areas)} 个Area", "INFO")
            return sorted(areas)
        except Exception as e:
            print(f"获取 Area Path 失败: {str(e)}")
            return []
    except Exception as e:
        st.error(f"获取Area列表失败: {str(e)}")
        add_log(f"获取Area列表失败: {str(e)}", "ERROR")
        return []


def get_work_items(project_name, work_item_type="Feature", area_path=None):
    """获取指定项目的工作项，支持Area过滤，直接使用Azure DevOps SDK"""
    try:
        connection = get_ado_connection()
    except Exception as e:
        st.error(str(e))
        add_log(str(e), "ERROR")
        return []
    
    try:
        wit_client = connection.clients.get_work_item_tracking_client()
        
        # 构建查询条件
        where_clause = f"[System.TeamProject] = '{project_name.replace("'", "''")}' AND [System.WorkItemType] = '{work_item_type.replace("'", "''")}'"
        
        # 如果指定了Area，则添加Area过滤条件
        if area_path:
            where_clause += f" AND [System.AreaPath] = '{project_name}\\{area_path.replace("'", "''")}'"
        
        # 查询工作项的WIQL查询
        wiql_query = Wiql(
            query=f"""
            SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType], [System.AssignedTo], [System.AreaPath], [System.Description]
            FROM WorkItems
            WHERE {where_clause}
            ORDER BY [System.Id] DESC
            """
        )
        
        # 添加调试日志
        area_info = f", Area='{area_path}'" if area_path else ""
        add_log(f"执行WIQL查询: 项目='{project_name}'{area_info}, 类型='{work_item_type}'", "INFO")
        add_log(f"完整查询语句: {wiql_query.query}", "DEBUG")
        
        # 执行查询
        query_result = wit_client.query_by_wiql(wiql=wiql_query)
        work_items = []
        
        if query_result.work_items:
            add_log(f"查询返回 {len(query_result.work_items)} 个工作项", "INFO")
            # 获取详细的工作项信息
            work_item_ids = [item.id for item in query_result.work_items]
            if work_item_ids:
                add_log(f"工作项ID列表: {work_item_ids[:10]}{'...' if len(work_item_ids) > 10 else ''}", "DEBUG")  # 只显示前10个ID
                
                # 分批获取工作项详情，避免404错误（ADO API对批量请求有限制）
                batch_size = 200  # ADO API推荐的批量大小
                for i in range(0, len(work_item_ids), batch_size):
                    batch_ids = work_item_ids[i:i + batch_size]
                    add_log(f"获取批次 {i//batch_size + 1}: {len(batch_ids)} 个工作项", "INFO")
                    
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
        else:
            add_log("查询返回0个工作项", "WARNING")
        
        add_log(f"成功获取 {len(work_items)} 个工作项", "SUCCESS")
        return work_items
    except Exception as e:
        st.error(f"获取工作项失败: {str(e)}")
        add_log(f"获取工作项失败: {str(e)}", "ERROR")
        import traceback
        add_log(f"详细错误信息: {traceback.format_exc()}", "ERROR")
        return []


def add_log(message, level="INFO"):
    """记录日志到全局日志系统"""
    # 添加时间戳
    from datetime import datetime
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {level}: {message}"
    
    # 将日志添加到会话状态
    if 'log_messages' not in st.session_state:
        st.session_state.log_messages = []
    
    st.session_state.log_messages.append(log_entry)
    
    # 只保留最近100条日志
    if len(st.session_state.log_messages) > 100:
        st.session_state.log_messages = st.session_state.log_messages[-100:]


def show_ado_browser():
    """显示ADO浏览器界面"""
    st.title("Azure DevOps 浏览器")
    
    # 检查是否安装了azure-devops依赖
    try:
        from azure.devops.connection import Connection
        from msrest.authentication import BasicAuthentication
    except ImportError:
        st.error("缺少azure-devops依赖")
        add_log("缺少azure-devops依赖", "ERROR")
        st.info("请安装依赖: pip install azure-devops")
        return
    
    # 获取项目列表
    with st.spinner("正在获取项目列表..."):
        projects = get_projects()
    
    if not projects:
        st.warning("未找到任何ADO项目，或连接失败")
        add_log("未找到任何ADO项目，或连接失败", "WARNING")
        return
    
    # 选择项目
    selected_project = st.selectbox("选择项目", projects)
    
    if selected_project:
        # 获取Area列表
        with st.spinner("正在获取Area列表..."):
            areas = get_areas(selected_project)
        
        # 选择Area（如果存在Area）
        if areas:
            area_options = ["全部"] + areas
            selected_area = st.selectbox("选择Area", area_options)
        else:
            selected_area = "全部"
            st.info("该项目没有找到Area信息")
        
        # 选择工作项类型
        work_item_types = ["Feature", "User Story", "Task", "Bug"]
        selected_type = st.selectbox("选择工作项类型", work_item_types)
        
        # 显示工作项
        if st.button("获取工作项"):
            # 如果选择的Area是"全部"，则不使用Area过滤
            area_filter = selected_area if selected_area != "全部" else None
            
            with st.spinner(f"正在获取 {selected_project} 项目中的{selected_type}工作项..."):
                work_items = get_work_items(selected_project, selected_type, area_filter)
            
            if work_items:
                # 构建标题，包括Area信息
                area_info = f" (Area: {selected_area})" if selected_area != "全部" else ""
                st.subheader(f"项目 {selected_project} 中的{selected_type}工作项{area_info} ({len(work_items)} 个)")
                
                # 显示工作项表格
                for item in work_items:
                    with st.expander(f"#{item['id']} - {item['title']}"):
                        st.write(f"**ID:** {item['id']}")
                        st.write(f"**标题:** {item['title']}")
                        st.write(f"**类型:** {item['type']}")
                        st.write(f"**状态:** {item['state']}")
                        st.write(f"**Area:** {item['area_path']}")
                        st.write(f"**负责人:** {item['assigned_to']}")
                        
                        if item['description'] and item['description'] != 'N/A':
                            st.write(f"**描述:** {item['description']}")
            else:
                st.info("该项目中没有找到相应类型的工作项")
                add_log(f"项目 {selected_project} 中没有找到 {selected_type} 类型的工作项", "INFO")
        else:
            st.info(f"选择项目 {selected_project} 和Area {selected_area}，然后点击'获取工作项'按钮来查看{selected_type}工作项")