import streamlit as st
from dotenv import load_dotenv
import os
import sys

# 加载环境变量
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.requirement_tracker.crew import requirement_crew

def main():
    st.set_page_config(
        page_title="Requirement Tracker",
        page_icon="📋",
        layout="wide"
    )

    st.title("📋 Requirement Tracker")
    st.markdown("""
    这是一个基于AI的自动化需求跟踪系统。请输入您的需求描述，
    系统将自动生成结构化文档、创建Azure DevOps工作项并发布到Confluence。
    """)

    # 从环境变量获取配置状态
    required_vars = [
        "DASHSCOPE_API_KEY"
    ]
    
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
                with st.spinner("正在处理您的需求，请稍候..."):
                    try:
                        # 启动 Crew，传入输入文字
                        result = requirement_crew.kickoff(inputs={"input_text": user_input.strip()})
                        
                        st.success("✅ 需求处理完成!")
                        
                        # 显示结果
                        st.header("📄 处理结果")
                        st.text_area("输出结果:", value=str(result), height=300)
                        
                    except Exception as e:
                        st.error(f"处理过程中出现错误: {str(e)}")
                        st.info("请检查工具配置（API Key、权限、网络）或查看详细日志。")
    
    with col2:
        if st.button("🧹 清空输入", use_container_width=True):
            st.experimental_rerun()

    # 使用说明
    st.header("ℹ️ 使用说明")
    st.markdown("""
    1. 在上方文本框中输入您的需求描述
    2. 点击"处理需求"按钮开始处理
    3. 等待系统完成处理（可能需要一些时间）
    4. 查看处理结果，包括生成的文档链接和工作项ID
    
    > 注意: 确保已在 `.env` 文件中正确配置所有必需的环境变量
    """)

if __name__ == "__main__":
    main()