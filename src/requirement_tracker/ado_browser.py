"""
Azure DevOps (ADO) 浏览器模块
用于在Web界面中显示ADO项目和工作项信息
"""
import os
import streamlit as st
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_1.work_item_tracking.models import Wiql


def get_ado_connection():
    """获取ADO连接"""
    ado_org_url = os.getenv("ADO_ORG_URL")
    ado_pat = os.getenv("ADO_PAT")
    
    if not ado_org_url or not ado_pat:
        st.error("ADO配置不完整，请检查环境变量ADO_ORG_URL和ADO_PAT")
        add_log("ADO配置不完整，请检查环境变量ADO_ORG_URL和ADO_PAT", "ERROR")
        return None
    
    try:
        credentials = BasicAuthentication('', ado_pat)
        connection = Connection(base_url=ado_org_url, creds=credentials)
        add_log("ADO连接成功建立", "INFO")
        return connection
    except Exception as e:
        st.error(f"ADO连接失败: {str(e)}")
        add_log(f"ADO连接失败: {str(e)}", "ERROR")
        return None


def get_projects():
    """获取所有ADO项目"""
    connection = get_ado_connection()
    if not connection:
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


def get_work_items(project_name, work_item_type="Feature"):
    """获取指定项目的工作项"""
    connection = get_ado_connection()
    if not connection:
        return []
    
    try:
        wit_client = connection.clients.get_work_item_tracking_client()
        
        # 查询工作项的WIQL查询
        # 对项目名称和工作项类型进行适当的转义处理
        escaped_project_name = project_name.replace("'", "''")
        escaped_work_item_type = work_item_type.replace("'", "''")
        
        wiql_query = Wiql(
            query=f"""
            SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType], [System.AssignedTo], [System.Description]
            FROM WorkItems
            WHERE [System.TeamProject] = '{escaped_project_name}'
            AND [System.WorkItemType] = '{escaped_work_item_type}'
            ORDER BY [System.Id] DESC
            """
        )
        
        # 添加调试日志
        add_log(f"执行WIQL查询: 项目='{escaped_project_name}', 类型='{escaped_work_item_type}'", "INFO")
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
        # 选择工作项类型
        work_item_types = ["Feature", "User Story", "Task", "Bug"]
        selected_type = st.selectbox("选择工作项类型", work_item_types)
        
        # 显示工作项
        if st.button("获取工作项"):
            with st.spinner(f"正在获取 {selected_project} 项目中的{selected_type}工作项..."):
                work_items = get_work_items(selected_project, selected_type)
            
            if work_items:
                st.subheader(f"项目 {selected_project} 中的{selected_type}工作项 ({len(work_items)} 个)")
                
                # 显示工作项表格
                for item in work_items:
                    with st.expander(f"#{item['id']} - {item['title']}"):
                        st.write(f"**ID:** {item['id']}")
                        st.write(f"**标题:** {item['title']}")
                        st.write(f"**类型:** {item['type']}")
                        st.write(f"**状态:** {item['state']}")
                        st.write(f"**负责人:** {item['assigned_to']}")
                        
                        if item['description'] and item['description'] != 'N/A':
                            st.write(f"**描述:** {item['description']}")
            else:
                st.info("该项目中没有找到相应类型的工作项")
                add_log(f"项目 {selected_project} 中没有找到 {selected_type} 类型的工作项", "INFO")
        else:
            st.info(f"选择项目 {selected_project} 并点击'获取工作项'按钮来查看{selected_type}工作项")