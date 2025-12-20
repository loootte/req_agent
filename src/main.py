# main.py
import os
import argparse
from dotenv import load_dotenv
from src.requirement_tracker.crew import requirement_crew, run_crew  # ← 请根据你的包名修改，例如 src.requirement_crew.crew

# 如果你把 crew 定义为一个函数返回 Crew，也可以用下面方式
# from src.your_crew.crew import create_requirement_crew

# 加载 .env 文件中的环境变量（强烈推荐，所有密钥都放这里）
"""
.env 格式
# 阿里云通义千问
DASHSCOPE_API_KEY=sk-your-real-key-here

# Azure OpenAI (Microsoft Copilot基础)
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# xAI Grok
GROK_API_KEY=your-xai-api-key

# Confluence
CONFLUENCE_URL=https://your-company.atlassian.net
CONFLUENCE_TOKEN=your-confluence-api-token
CONFLUENCE_SPACE=REQ                  # 空间 Key
CONFLUENCE_PARENT_ID=12345678        # 可选：父页面 ID

# Azure DevOps（如果用 ADO）
ADO_ORG_URL=https://dev.azure.com/your-org
ADO_PAT=your-personal-access-token
ADO_PROJECT=YourProjectName

# Jira（如果用 Jira 代替 ADO）
# JIRA_URL=https://your-company.atlassian.net
# JIRA_TOKEN=your-jira-api-token
# JIRA_PROJECT=PROJ
"""
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description='需求文档自动化系统')
    parser.add_argument('--model', choices=['qwen', 'azure', 'grok'], default='qwen', 
                       help='选择使用的AI模型: qwen(通义千问)、azure(Azure OpenAI) 或 grok(xAI)')
    args = parser.parse_args()
    
    model_type = args.model
    
    # 检查所选模型的必要环境变量
    if model_type == "qwen":
        required_model_vars = ["DASHSCOPE_API_KEY"]
        model_name = "通义千问(Qwen)"
    elif model_type == "azure":
        required_model_vars = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"]
        model_name = "Azure OpenAI (Microsoft Copilot基础)"
    elif model_type == "grok":
        required_model_vars = ["GROK_API_KEY"]
        model_name = "Grok (xAI)"
    else:
        required_model_vars = []
        model_name = "未知模型"
        
    missing_model_vars = [var for var in required_model_vars if not os.getenv(var)]
    if missing_model_vars:
        print(f"❌ 缺少 {model_name} 所需的环境变量，请在 .env 文件中配置：")
        for var in missing_model_vars:
            print(f"   - {var}")
        print("\n程序退出。")
        return

    print(f"🚀 需求文档自动化 Crew 已就绪！(使用 {model_name})")
    print("输入你想要整理的需求描述（随意文字），我将自动生成结构化文档、创建工作项并发布到 Confluence。")
    print("输入 'exit' 或 'quit' 退出程序。\n")

    while True:
        user_input = input("📝 请粘贴需求描述：\n").strip()

        if user_input.lower() in ["exit", "quit", "q"]:
            print("👋 再见！")
            break

        if not user_input:
            print("⚠️  输入不能为空，请重新输入。\n")
            continue

        print(f"\n🤖 Crew 开始工作(使用 {model_name})，请稍等...\n")

        try:
            # 启动 Crew，传入输入文字和模型类型
            result = run_crew(user_input, model_type)

            print("\n=== 🎉 完成！===\n")
            print(result)
            print("\n" + "-"*60 + "\n")

        except Exception as e:
            print(f"\n❌ 执行过程中出错：{str(e)}")
            print("请检查工具配置（API Key、权限、网络）或查看详细日志。\n")

if __name__ == "__main__":
    # 可选：在这里可以做一些启动前检查
    main()