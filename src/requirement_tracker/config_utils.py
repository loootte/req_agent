import json
from dotenv import dotenv_values
import os
from pathlib import Path
from typing import Dict, List

DEFAULT_ENV_PATH = Path(__file__).parent.parent.parent / ".env"
FALLBACK_ENCODINGS = ['gbk', 'latin-1']


def _read_file_content(path: Path, encoding: str = 'utf-8') -> str:
    """读取文件内容，支持指定编码"""
    with open(path, 'r', encoding=encoding) as f:
        return f.read()


def _rewrite_file_utf8(path: Path, content: str) -> None:
    """重写文件为 utf-8"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def _parse_existing_vars(lines: List[str]) -> Dict[str, str]:
    """从 lines 解析 vars"""
    vars_dict = {}
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            vars_dict[key] = value
    return vars_dict


def load_env_vars(env_path: Path = DEFAULT_ENV_PATH) -> Dict[str, str]:
    """加载环境变量"""
    if not env_path.exists():
        return {}
    try:
        return dotenv_values(env_path)
    except UnicodeDecodeError:
        for enc in FALLBACK_ENCODINGS:
            try:
                content = _read_file_content(env_path, enc)
                _rewrite_file_utf8(env_path, content)
                return dotenv_values(env_path)
            except:
                pass
        return {}


def save_env_vars(configs: Dict[str, str], env_path: Path = DEFAULT_ENV_PATH) -> None:
    """保存环境变量到.env文件，只更新configs中指定的变量"""
    # 读取现有的文件内容
    if env_path.exists():
        # 读取原始文件内容，以保留格式和注释
        for enc in FALLBACK_ENCODINGS + ['utf-8']:
            try:
                with open(env_path, 'r', encoding=enc) as f:
                    lines = f.readlines()
                break
            except UnicodeDecodeError:
                continue
    else:
        lines = []
    
    # 解析现有变量，但保留原始行
    existing_vars = _parse_existing_vars(lines)
    
    # 更新要保存的配置
    existing_vars.update(configs)
    
    # 写入文件（始终使用UTF-8编码），只更新指定的变量
    with open(env_path, 'w', encoding='utf-8') as f:
        # 遍历原始行，更新指定的变量
        for line in lines:
            line_stripped = line.strip()
            if line_stripped and not line_stripped.startswith('#') and '=' in line_stripped:
                key = line_stripped.split('=', 1)[0]
                if key in configs:
                    value = configs[key]
                    if value is not None:
                        # 特殊处理LLM_CONFIG，确保它在一行内并且正确转义
                        if key == "LLM_CONFIG":
                            escaped_value = json.dumps(json.loads(value), ensure_ascii=False)
                            f.write(f'{key}={escaped_value}\n')
                        # 处理包含特殊字符的值
                        elif ' ' in str(value) or '\n' in str(value) or '#' in str(value) or '=' in str(value):
                            # 转义引号
                            escaped_value = str(value).replace('"', '\\"')
                            f.write(f'{key}="{escaped_value}"\n')
                        else:
                            f.write(f'{key}={value}\n')
                    else:
                        f.write(f'{key}=\n')
                else:
                    f.write(line)  # 保留原始行
            else:
                f.write(line)  # 保留注释和空行
        
        # 添加新变量（如果存在但原文件中没有）
        for key, value in configs.items():
            if key not in [line.split('=', 1)[0] if '=' in line and not line.strip().startswith('#') else None 
                         for line in lines if line.strip()]:
                if value is not None:
                    # 特殊处理LLM_CONFIG，确保它在一行内并且正确转义
                    if key == "LLM_CONFIG":
                        escaped_value = json.dumps(json.loads(value), ensure_ascii=False)
                        f.write(f'{key}={escaped_value}\n')
                    # 处理包含特殊字符的值
                    elif ' ' in str(value) or '\n' in str(value) or '#' in str(value) or '=' in str(value):
                        # 转义引号
                        escaped_value = str(value).replace('"', '\\"')
                        f.write(f'{key}="{escaped_value}"\n')
                    else:
                        f.write(f'{key}={value}\n')
                else:
                    f.write(f'{key}=\n')


def load_custom_llms() -> Dict[str, dict]:
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

    # 如果没有LLM_CONFIG或解析失败，从旧格式加载
    custom_llms = {}
    for key in env_vars:
        if key.startswith("LLM_CONFIG_"):
            model_key = key[len("LLM_CONFIG_"):].lower()
            try:
                custom_llms[model_key] = json.loads(env_vars[key])
            except json.JSONDecodeError:
                pass

    # 如果仍然没有模型配置，则初始化默认配置
    if not custom_llms:
        custom_llms = get_default_llms()

    return custom_llms


def save_custom_llms(custom_llms: Dict[str, dict]) -> None:
    """保存自定义LLM配置"""
    # 转换为列表格式
    llm_list = []
    for key, config in custom_llms.items():
        config["key"] = key
        llm_list.append(config)

    # 保存为单个JSON环境变量
    save_env_vars({"LLM_CONFIG": json.dumps(llm_list, ensure_ascii=False)})


def get_default_llms() -> Dict[str, dict]:
    """获取默认LLM配置"""
    return {
        "qwen": {
            "key": "qwen",
            "name": "通义千问 (Qwen)",
            "model": "qwen-max",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "api_key": "",
            "provider": "openai",
            "editable": False
        },
        "azure": {
            "key": "azure",
            "name": "Azure OpenAI (Microsoft Copilot基础)",
            "model": "azure/gpt-4",
            "base_url": "",
            "api_key": "",
            "provider": "azure",
            "editable": False
        },
        "grok": {
            "key": "grok",
            "name": "Grok (xAI)",
            "model": "grok-beta",
            "base_url": "https://api.x.ai/v1",
            "api_key": "",
            "provider": "openai",
            "editable": False
        }
    }


def initialize_default_llms_in_env() -> Dict[str, dict]:
    """初始化默认LLM到环境变量中（如果不存在）"""
    # 只有在LLM_CONFIG变量不存在时才初始化
    custom_llms = load_custom_llms()

    # 如果没有模型配置，则初始化默认配置
    if not custom_llms:
        default_llms = get_default_llms()
        save_custom_llms(default_llms)
        return default_llms

    return custom_llms