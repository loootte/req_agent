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

from src.requirement_tracker.crew import requirement_crew, run_crew

def load_env_vars():
    """加载环境变量"""
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        try:
            return dotenv_values(env_path)
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码
            try:
                # 尝试使用gbk编码（常见于中文Windows系统）
                with open(env_path, 'r', encoding='gbk') as f:
                    content = f.read()
                # 将内容写回为UTF-8编码
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                # 重新加载
                return dotenv_values(env_path)
            except:
                # 最后尝试使用latin-1编码
                with open(env_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                # 将内容写回为UTF-8编码
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                # 重新加载
                return dotenv_values(env_path)
    return {}

def load_custom_llms():
    """加载自定义LLM配置"""
    env_vars = load_env_vars()
    
    # 从LLM_CONFIG环境变量加载所有模型配置
    if "LLM_CONFIG" in env_vars:
        try:
            llm_list = json.loads(env_vars["LLM_CONFIG"])
            return {llm["key"]: llm for llm in llm_list}
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"LLM_CONFIG内容: {env_vars['LLM_CONFIG']}")
            pass
    


def main():
    st.set_page_config(
        page_title="Requirement Tracker",
        page_icon="📋",
        layout="wide"
    )

    # 创建导航栏
    st.sidebar.title("🎯 导航")
    page = st.sidebar.radio(
        "选择页面:",
        ["🏠 主页", "⚙️ LLM 配置"]
    )
    
    if page == "🏠 主页":
        show_main_page()
    elif page == "⚙️ LLM 配置":
        # 导入配置页面模块
        from src.requirement_tracker.config import show_config_page
        show_config_page()

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