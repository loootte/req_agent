# src/requirement_tracker/crew.py
from crewai import Crew, Task, LLM
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from .agents import create_analyzer, create_publisher
from .tasks import task1, task2  # 如果你也拆了tasks.py

def get_llm(model_type="qwen"):
    """
    根据指定的模型类型返回相应的LLM实例
    
    Args:
        model_type (str): 模型类型，可选值："qwen"、"azure" 或 "grok"
    
    Returns:
        LLM: 配置好的LLM实例
    """
    if model_type == "qwen":
        # Qwen模型配置
        return LLM(
            model="qwen-max",  # 修复: 移除 dashscope/ 前缀
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            provider="openai"  # 通过LiteLLM适配
        )
    elif model_type == "azure":
        # Azure OpenAI模型配置 (Microsoft Copilot基础)
        return LLM(
            model=f"azure/{os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4')}",
            base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            provider="azure"
        )
    elif model_type == "grok":
        # Grok模型配置 (通过xAI API)
        return LLM(
            model="grok-beta",
            base_url="https://api.x.ai/v1",
            api_key=os.getenv("GROK_API_KEY"),
            provider="openai"  # Grok API 兼容 OpenAI 格式
        )
    else:
        # 默认使用Qwen
        return LLM(
            model="qwen-max",  # 修复: 移除 dashscope/ 前缀
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            provider="openai"
        )

# 默认LLM配置
llm = get_llm("qwen")

# 创建Agent
analyzer = create_analyzer(llm)
publisher = create_publisher(llm)

# 设置任务代理
task1.agent = analyzer
task2.agent = publisher

# 组装Crew
requirement_crew = Crew(
    agents=[analyzer, publisher],
    tasks=[task1, task2],
    verbose=True
)

def run_crew(input_text: str, model_type: str = "qwen"):
    # 根据模型类型重新配置crew
    current_llm = get_llm(model_type)
    
    # 更新agent的LLM
    analyzer.llm = current_llm
    publisher.llm = current_llm
    
    result = requirement_crew.kickoff(inputs={"input_text": input_text})
    return result