import streamlit as st
from dotenv import load_dotenv, dotenv_values
import os
import sys
import json
from pathlib import Path

# 加载环境变量
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.requirement_tracker.crew import run_crew

# 导入重构后的配置函数
from src.requirement_tracker.config_utils import load_env_vars, load_custom_llms

def main():
    st.set_page_config(
        page_title="Requirement Tracker",
        page_icon="📋",
        layout="wide"
    )

    # 初始化日志
    if 'log_messages' not in st.session_state:
        st.session_state.log_messages = []

    # 添加日志函数
    def add_log(message, level="INFO"):
        timestamp = st.runtime.get_instance().get_timestamp() if hasattr(st.runtime, 'get_instance') else "时间戳"
        log_entry = f"[{timestamp}] {level}: {message}"
        st.session_state.log_messages.append(log_entry)
        # 只保留最近100条日志
        if len(st.session_state.log_messages) > 100:
            st.session_state.log_messages = st.session_state.log_messages[-100:]

    # 从文件加载CSS样式
    css_path = Path(__file__).parent / "static" / "styles.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # 如果CSS文件不存在，使用内联样式作为备选
        st.markdown("""
        <style>
        #logs-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 200px;
            background-color: #f0f2f6;
            border-top: 2px solid #808080;
            z-index: 999;
            overflow-y: auto;
            padding: 10px;
            font-family: monospace;
            font-size: 12px;
        }
        
        #logs-content {
            height: calc(100% - 30px);
            overflow-y: auto;
        }
        
        .log-entry {
            margin: 2px 0;
            padding: 2px 5px;
            border-radius: 3px;
        }
        
        .log-info { background-color: #e8f4fd; }
        .log-success { background-color: #e6f4ea; }
        .log-warning { background-color: #fef7e0; }
        .log-error { background-color: #fce8e6; }
        
        .toggle-logs {
            position: absolute;
            top: 5px;
            right: 10px;
            cursor: pointer;
            background: #0e1117;
            color: white;
            border: none;
            border-radius: 3px;
            padding: 2px 8px;
            font-size: 12px;
        }
        
        .logs-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #0e1117;
            color: white;
            padding: 5px 10px;
            border-radius: 5px 5px 0 0;
            margin-bottom: 5px;
        }
        
        .clear-logs {
            cursor: pointer;
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 3px;
            padding: 2px 8px;
            font-size: 12px;
        }
        </style>
        """, unsafe_allow_html=True)

    # 创建导航栏
    st.sidebar.title("🎯 导航")
    page = st.sidebar.radio(
        "选择页面:",
        ["🏠 主页", "⚙️ LLM 配置", "📊 ADO 浏览器"]
    )
    
    if page == "🏠 主页":
        show_main_page()
    elif page == "⚙️ LLM 配置":
        # 导入配置页面模块
        from src.requirement_tracker.config import show_config_page
        show_config_page()
    elif page == "📊 ADO 浏览器":
        # 导入ADO浏览器页面模块
        from src.requirement_tracker.ado_browser import show_ado_browser
        show_ado_browser()

    # 固定在底部的日志窗口
    if 'show_logs' not in st.session_state:
        st.session_state.show_logs = True

    if st.session_state.show_logs:
        # 日志窗口的HTML
        with st.container():
            st.markdown('<div id="logs-container">', unsafe_allow_html=True)
            
            # 日志窗口头部
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown('<div class="logs-header">📋 跟踪日志</div>', unsafe_allow_html=True)
            with col2:
                if st.button("❌", key="close_logs", help="隐藏日志窗口"):
                    st.session_state.show_logs = False
            with col3:
                if st.button("🗑️", key="clear_logs", help="清空日志"):
                    st.session_state.log_messages = []
            
            # 日志内容
            with st.container():
                st.markdown('<div id="logs-content">', unsafe_allow_html=True)
                if st.session_state.log_messages:
                    for log in st.session_state.log_messages:
                        # 根据日志级别设置样式
                        if "ERROR" in log:
                            st.markdown(f'<div class="log-entry log-error">{log}</div>', unsafe_allow_html=True)
                        elif "WARNING" in log:
                            st.markdown(f'<div class="log-entry log-warning">{log}</div>', unsafe_allow_html=True)
                        elif "SUCCESS" in log:
                            st.markdown(f'<div class="log-entry log-success">{log}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="log-entry log-info">{log}</div>', unsafe_allow_html=True)
                else:
                    st.text("暂无日志信息...")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

def show_main_page():
    st.title("📋 Requirement Tracker")
    st.markdown("""
    这是一个基于AI的自动化需求跟踪系统。请输入您的需求描述，
    系统将自动生成结构化文档。
    """)

    # 显示当前LLM配置
    configs = load_env_vars()
    custom_llms = load_custom_llms()
    
    current_model = configs.get("SELECTED_MODEL", "qwen")
    current_model_name = custom_llms.get(current_model, {}).get("name", "通义千问(Qwen)") if current_model in custom_llms else "通义千问(Qwen)"
    
    st.info(f"🤖 当前使用的AI模型: **{current_model_name}**")
    
    # 模型选择（覆盖默认选择）
    st.header("🔄 临时更换模型")
    model_option = st.radio(
        "请选择要使用的AI模型:",
        options=list(custom_llms.keys()),
        format_func=lambda x: custom_llms[x]["name"],
        index=list(custom_llms.keys()).index(current_model) if current_model in custom_llms else 0
    )
    
    # 从环境变量获取配置状态
    if model_option in custom_llms:
        llm_config = custom_llms[model_option]
        if model_option == "qwen":
            required_vars = ["DASHSCOPE_API_KEY"]
            model_name = "通义千问(Qwen)"
        elif model_option == "azure":
            required_vars = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"]
            model_name = "Azure OpenAI (Microsoft Copilot基础)"
        elif model_option == "grok":
            required_vars = ["GROK_API_KEY"]
            model_name = "Grok (xAI)"
        else:
            # 自定义模型
            required_vars = []
            model_name = f"自定义: {llm_config['name']}"
    else:
        required_vars = []
        model_name = "未知模型"
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        st.warning(f"缺少以下环境变量，请在 .env 文件中配置: {', '.join(missing_vars)}")
    
    # 用户输入区域
    st.header("📝 需求输入")
    user_input = st.text_area(
        "请输入您的需求描述:",
        height=200,
        placeholder="请在此处粘贴您的需求描述..."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 处理需求", type="primary", use_container_width=True):
            if not user_input.strip():
                st.error("请输入需求描述")
            elif missing_vars:
                st.error("请先配置所有必需的环境变量")
            else:
                with st.spinner(f"正在使用 {model_name} 处理您的需求，请稍候..."):
                    try:
                        # 启动 Crew，传入输入文字和模型类型
                        result = run_crew(user_input.strip(), model_option)
                        
                        st.success("✅ 需求处理完成!")
                        
                        # 显示结果
                        st.header("📄 处理结果")
                        st.text_area("输出结果:", value=str(result), height=300)
                        
                    except Exception as e:
                        st.error(f"处理过程中出现错误: {str(e)}")
                        st.info("请检查工具配置（API Key、权限、网络）或查看详细日志。")
    
    with col2:
        if st.button("🧹 清空输入", use_container_width=True):
            st.rerun()

    # 使用说明
    st.header("ℹ️ 使用说明")
    st.markdown("""
    1. 在上方选择要使用的AI模型
    2. 在文本框中输入您的需求描述
    3. 点击"处理需求"按钮开始处理
    4. 等待系统完成处理（可能需要一些时间）
    5. 查看处理结果
    
    > 💡 提示: 您可以在左侧边栏的「LLM 配置」页面中永久配置默认模型和API密钥
    """)

if __name__ == "__main__":
    main()