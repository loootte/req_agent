# src/requirement_tracker/crew.py
from crewai import Crew, Task, LLM
import os
import json
from dotenv import load_dotenv, dotenv_values
from pathlib import Path

# 加载环境变量
load_dotenv()

from .agents import create_analyzer, create_publisher
from .tasks import task1, task2  # 如果你也拆了tasks.py

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

def get_llm(model_type="qwen"):
    """
    根据指定的模型类型返回相应的LLM实例
    
    Args:
        model_type (str): 模型类型，可以是预定义模型(qwen, azure, grok)或自定义模型标识符
    
    Returns:
        LLM: 配置好的LLM实例
    """
    # 加载自定义LLM配置（包括默认模型）
    custom_llms = load_custom_llms()
    
    # 检查是否为自定义模型（包括默认模型）
    if model_type in custom_llms:
        custom_llm = custom_llms[model_type]
        
        # 对于默认模型，使用环境变量中的API密钥
        api_key = custom_llm["api_key"]
        if model_type == "qwen":
            api_key = os.getenv("DASHSCOPE_API_KEY", api_key)
        elif model_type == "azure":
            api_key = os.getenv("AZURE_OPENAI_API_KEY", api_key)
        elif model_type == "grok":
            api_key = os.getenv("GROK_API_KEY", api_key)
        
        # 对于Azure模型，特殊处理模型名称
        model = custom_llm["model"]
        if model_type == "azure":
            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
            model = f"azure/{deployment_name}"
        
        # 对于Azure模型，还需要base_url
        base_url = custom_llm["base_url"]
        if model_type == "azure":
            base_url = os.getenv("AZURE_OPENAI_ENDPOINT", base_url)
        
        return LLM(
            model=model,
            base_url=base_url,
            api_key=api_key,
            provider=custom_llm["provider"]
        )
    
    # 如果找不到配置，默认使用Qwen
    return LLM(
        model="qwen-max",
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