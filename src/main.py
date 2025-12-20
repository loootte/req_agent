# main.py
import os
import argparse
import json
from dotenv import load_dotenv, dotenv_values
from pathlib import Path
from src.requirement_tracker.crew import run_crew  # ← 请根据你的包名修改，例如 src.requirement_crew.crew

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

# xAI Grok API 密钥
GROK_API_KEY=your-xai-api-key

# LLM模型配置
LLM_CONFIG=[{"key": "qwen", "name": "通义千问 (Qwen)", "model": "qwen-max", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "api_key": "", "provider": "openai", "editable": false}, {"key": "azure", "name": "Azure OpenAI (Microsoft Copilot基础)", "model": "azure/gpt-4", "base_url": "", "api_key": "", "provider": "azure", "editable": false}, {"key": "grok", "name": "Grok (xAI)", "model": "grok-beta", "base_url": "https://api.x.ai/v1", "api_key": "", "provider": "openai", "editable": false}]

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

def load_env_vars():
    """加载环境变量"""
    env_path = Path(__file__).parent.parent / ".env"
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
        except json.JSONDecodeError:
            pass
    
    # 如果没有LLM_CONFIG或解析失败，从旧格式加载
    custom_llms = {}
    for key in env_vars:
        if key.startswith("LLM_CONFIG_"):
            model_key = key[len("LLM_CONFIG_"):].lower()
            try:
                custom_llms[model_key] = json.loads(env_vars[key])
            except json.JSONDecodeError:
                pass
    
    return custom_llms

# 加载环境变量
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description='需求文档自动化系统')
    parser.add_argument('--model', default='qwen', 
                       help='选择使用的AI模型: qwen(通义千问)、azure(Azure OpenAI)、grok(xAI) 或自定义模型标识符')
    args = parser.parse_args()
    
    model_type = args.model
    custom_llms = load_custom_llms()
    
    # 检查所选模型的必要环境变量
    if model_type in custom_llms:
        llm_config = custom_llms[model_type]
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
            # 自定义模型
            required_model_vars = []
            model_name = f"自定义: {llm_config['name']}"
    else:
        required_model_vars = []
        model_name = f"未知模型 ({model_type})"
        
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