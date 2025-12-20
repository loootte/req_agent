# main.py
import os
from dotenv import load_dotenv
from src.requirement_tracker.crew import requirement_crew  # ← 请根据你的包名修改，例如 src.requirement_crew.crew

# 如果你把 crew 定义为一个函数返回 Crew，也可以用下面方式
# from src.your_crew.crew import create_requirement_crew

# 加载 .env 文件中的环境变量（强烈推荐，所有密钥都放这里）
"""
.env 格式
# 阿里云通义千问
DASHSCOPE_API_KEY=sk-your-real-key-here

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
    print("🚀 需求文档自动化 Crew 已就绪！")
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

        print("\n🤖 Crew 开始工作，请稍等...\n")

        try:
            # 启动 Crew，传入输入文字
            result = requirement_crew.kickoff(inputs={"input_text": user_input})

            print("\n=== 🎉 完成！===\n")
            print(result)
            print("\n" + "-"*60 + "\n")

        except Exception as e:
            print(f"\n❌ 执行过程中出错：{str(e)}")
            print("请检查工具配置（API Key、权限、网络）或查看详细日志。\n")

if __name__ == "__main__":
    # 可选：在这里可以做一些启动前检查
    required_env_vars = [
        "DASHSCOPE_API_KEY",
        "CONFLUENCE_URL", "CONFLUENCE_TOKEN", "CONFLUENCE_SPACE",
        # ADO 或 Jira 任选其一
        # "ADO_ORG_URL", "ADO_PAT", "ADO_PROJECT",
        # "JIRA_URL", "JIRA_TOKEN", "JIRA_PROJECT",
    ]
    missing = [var for var in required_env_vars if not os.getenv(var)]
    if missing:
        print("❌ 缺少以下环境变量，请在 .env 文件中配置：")
        for var in missing:
            print(f"   - {var}")
        print("\n程序退出。")
    else:
        main()