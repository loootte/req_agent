# src/requirement_tracker/crew.py
from crewai import Crew, Task, LLM
import os
import json
from dotenv import load_dotenv, dotenv_values
from pathlib import Path
from typing import Dict, Any, Optional

# 加载环境变量
load_dotenv()

from .agents import create_analyzer, create_publisher
from .tasks import generation_task, create_feature  # 如果你也拆了tasks.py

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

def _get_qwen_llm(env_vars: Dict[str, str]) -> LLM:
    """隔离 qwen LLM 配置"""
    return LLM(
        model=env_vars.get("QWEN_MODEL_NAME", "qwen-max"),
        base_url=env_vars.get("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        api_key=env_vars.get("DASHSCOPE_API_KEY"),
        provider="openai"
    )

def _get_grok_llm(env_vars: Dict[str, str]) -> LLM:
    """隔离 grok LLM 配置"""
    return LLM(
        model=env_vars.get("GROK_MODEL_NAME", "grok-beta"),
        base_url=env_vars.get("GROK_BASE_URL", "https://api.x.ai/v1"),
        api_key=env_vars.get("GROK_API_KEY"),
        provider="openai"
    )

def get_llm(model_type: Optional[str] = None, env_vars: Optional[Dict[str, str]] = None) -> Any:
    """
    根据指定的模型类型返回相应的LLM实例
    
    Args:
        model_type (str): 模型类型，可以是预定义模型(qwen, grok)或自定义模型标识符
        env_vars (dict): 环境变量字典，用于测试时mock
    
    Returns:
        LLM: 配置好的LLM实例
    """
    # 如果没有提供env_vars，则从环境中获取
    if env_vars is None:
        env_vars = {
            "DASHSCOPE_API_KEY": os.getenv("DASHSCOPE_API_KEY"),
            "QWEN_MODEL_NAME": os.getenv("QWEN_MODEL_NAME", "qwen-max"),
            "QWEN_BASE_URL": os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            "GROK_API_KEY": os.getenv("GROK_API_KEY"),
            "GROK_MODEL_NAME": os.getenv("GROK_MODEL_NAME", "grok-beta"),
            "GROK_BASE_URL": os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")
        }
    
    # 如果没有提供model_type，则从环境变量中获取
    if not model_type:
        model_type = os.getenv("SELECTED_MODEL", "qwen")
    
    # 加载自定义LLM配置（包括默认模型）
    custom_llms = load_custom_llms()
    
    # 检查是否为自定义模型（包括默认模型）
    if model_type in custom_llms:
        custom_llm = custom_llms[model_type]
        
        # 对于默认模型，使用环境变量中的API密钥
        api_key = custom_llm["api_key"]
        if model_type == "qwen":
            api_key = env_vars.get("DASHSCOPE_API_KEY", api_key)
        elif model_type == "grok":
            api_key = env_vars.get("GROK_API_KEY", api_key)
        
        # 对于Azure模型，特殊处理模型名称
        model = custom_llm["model"]
        if model_type == "azure":
            deployment_name = env_vars.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
            model = f"azure/{deployment_name}"
        
        # 对于Azure模型，还需要base_url
        base_url = custom_llm["base_url"]
        if model_type == "azure":
            base_url = env_vars.get("AZURE_OPENAI_ENDPOINT", base_url)
        
        return LLM(
            model=model,
            base_url=base_url,
            api_key=api_key,
            provider=custom_llm["provider"]
        )
    
    # 处理预定义模型
    if model_type == "qwen":
        return _get_qwen_llm(env_vars)
    elif model_type == "grok":
        return _get_grok_llm(env_vars)
    
    # 如果找不到配置，默认使用Qwen
    return _get_qwen_llm(env_vars)

def create_crew(selected_model: str, env_vars: Optional[Dict[str, str]] = None) -> Crew:
    """
    创建Crew实例
    
    Args:
        selected_model (str): 选择的模型类型
        env_vars (dict): 环境变量字典，用于测试时mock
    
    Returns:
        Crew: 配置好的Crew实例
    """
    llm = get_llm(selected_model, env_vars)
    analyzer = create_analyzer(llm)
    publisher = create_publisher(llm)
    
    # 直接创建任务实例，而不是复制
    from .tasks import task1_description, task1_expected_output, task2_description, task2_expected_output
    
    task1_instance = create_task1_instance(task1_description, task1_expected_output, analyzer)
    task2_instance = create_task2_instance(task2_description, task2_expected_output, publisher)
    
    return Crew(
        agents=[analyzer, publisher],
        tasks=[task1_instance, task2_instance],
        verbose=True
    )

def create_task1_instance(description, expected_output, agent):
    """创建任务1实例，用于测试目的"""
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent
    )

def create_task2_instance(description, expected_output, agent):
    """创建任务2实例，用于测试目的"""
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent
    )

def run_crew(input_text: str, model_type: str = "qwen", env_vars: Optional[Dict[str, str]] = None) -> str:
    """
    运行Crew任务
    
    Args:
        input_text (str): 输入文本
        model_type (str): 模型类型
        env_vars (dict): 环境变量字典，用于测试时mock
    
    Returns:
        str: 运行结果
    """
    try:
        crew = create_crew(model_type, env_vars)
        result = crew.kickoff(inputs={"input_text": input_text})
        return str(result)  # 返回值，便于测试
    except Exception as e:
        return f"Error: {str(e)}"  # 覆盖异常