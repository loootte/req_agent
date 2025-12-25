"""
Azure DevOps (ADO) 浏览器模块
用于在Web界面中显示ADO项目和工作项信息
"""
import os
import streamlit as st


def show_ado_browser():
    """显示ADO浏览器界面"""
    st.title("Azure DevOps 浏览器")
    
    # 从tools模块导入函数
    try:
        from src.requirement_tracker.tools import get_ado_projects, get_ado_work_items
    except ImportError as e:
        st.error(f"无法导入ADO工具: {str(e)}")
        st.info("请确保已安装azure-devops依赖: pip install azure-devops")
        return
    
    # 获取项目列表
    with st.spinner("正在获取项目列表..."):
        try:
            projects = get_ado_projects()
        except Exception as e:
            st.error(f"获取项目列表失败: {str(e)}")
            return
    
    if not projects:
        st.warning("未找到任何ADO项目，或连接失败")
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
                try:
                    work_items = get_ado_work_items(selected_project, selected_type)
                except Exception as e:
                    st.error(f"获取工作项失败: {str(e)}")
                    return
            
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
        else:
            st.info(f"选择项目 {selected_project} 并点击'获取工作项'按钮来查看{selected_type}工作项")