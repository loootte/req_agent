import streamlit as st
from dotenv import dotenv_values
import os
from pathlib import Path
import json

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

def save_env_vars(configs):
    """保存环境变量到.env文件"""
    env_path = Path(__file__).parent.parent.parent / ".env"
    
    # 读取现有的环境变量
    existing_vars = {}
    if env_path.exists():
        try:
            existing_vars = dotenv_values(env_path)
        except UnicodeDecodeError:
            # 处理编码问题
            try:
                with open(env_path, 'r', encoding='gbk') as f:
                    lines = f.readlines()
                # 重建环境变量字典
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        existing_vars[key] = value
            except:
                try:
                    with open(env_path, 'r', encoding='latin-1') as f:
                        lines = f.readlines()
                    # 重建环境变量字典
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            existing_vars[key] = value
                except:
                    pass
    
    # 更新配置
    existing_vars.update(configs)
    
    # 写入文件（始终使用UTF-8编码）
    with open(env_path, 'w', encoding='utf-8') as f:
        for key, value in existing_vars.items():
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

def save_custom_llms(custom_llms):
    """保存自定义LLM配置"""
    # 转换为列表格式
    llm_list = []
    for key, config in custom_llms.items():
        config["key"] = key
        llm_list.append(config)
    
    # 保存为单个JSON环境变量
    save_env_vars({"LLM_CONFIG": json.dumps(llm_list, ensure_ascii=False)})

def get_default_llms():
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

def initialize_default_llms_in_env():
    """初始化默认LLM到环境变量中（如果不存在）"""
    # 只有在LLM_CONFIG变量不存在时才初始化
    custom_llms = load_custom_llms()
    
    # 如果没有模型配置，则初始化默认配置
    if not custom_llms:
        default_llms = get_default_llms()
        save_custom_llms(default_llms)
        return default_llms
    
    return custom_llms

def show_config_page():
    st.set_page_config(
        page_title="LLM 配置",
        page_icon="⚙️",
        layout="wide"
    )

    st.title("⚙️ LLM 模型配置")

    # 加载当前配置
    current_configs = load_env_vars()
    custom_llms = load_custom_llms()
    
    # 如果没有模型配置，初始化默认配置
    if not custom_llms:
        custom_llms = initialize_default_llms_in_env()
    
    # 模型选择
    st.header("🤖 默认模型选择")
    
    current_model = current_configs.get("SELECTED_MODEL", "qwen")
    selected_model = st.selectbox(
        "选择默认模型:",
        options=list(custom_llms.keys()),
        format_func=lambda x: custom_llms[x]["name"],
        index=list(custom_llms.keys()).index(current_model) if current_model in custom_llms else 0
    )
    
    st.markdown("---")
    
    # 所有模型配置区域
    st.header("🔧 模型配置")
    
    # 创建一个副本用于临时修改
    temp_custom_llms = custom_llms.copy()
    
    for key, llm_config in custom_llms.items():
        with st.expander(f"{'🔧' if llm_config.get('editable', True) else '🔒'} {llm_config['name']} ({key})", 
                         expanded=(selected_model == key)):
            
            col1, col2 = st.columns([4, 1])
            with col1:
                # 显示模型信息（使用临时变量存储更改）
                name = st.text_input("显示名称:", value=llm_config["name"], key=f"name_{key}", 
                                   disabled=not llm_config.get("editable", True))
                model = st.text_input("模型标识:", value=llm_config["model"], key=f"model_{key}", 
                                    disabled=not llm_config.get("editable", True))
                base_url = st.text_input("API端点:", value=llm_config["base_url"], key=f"url_{key}", 
                                       disabled=not llm_config.get("editable", True))
                
                # API密钥处理
                if key == "qwen":
                    api_key_value = current_configs.get("DASHSCOPE_API_KEY", llm_config.get("api_key", ""))
                elif key == "azure":
                    api_key_value = current_configs.get("AZURE_OPENAI_API_KEY", llm_config.get("api_key", ""))
                elif key == "grok":
                    api_key_value = current_configs.get("GROK_API_KEY", llm_config.get("api_key", ""))
                else:
                    api_key_value = llm_config.get("api_key", "")
                    
                api_key = st.text_input("API密钥:", value=api_key_value, type="password", key=f"key_{key}", 
                                      disabled=not llm_config.get("editable", True))
                provider = st.selectbox("提供商:", ["openai", "azure"], 
                                      index=0 if llm_config["provider"] == "openai" else 1, 
                                      key=f"provider_{key}", 
                                      disabled=not llm_config.get("editable", True))
            
            with col2:
                # 只有自定义模型可以删除
                if llm_config.get("editable", True):
                    if st.button("🗑️ 删除", key=f"delete_{key}"):
                        if key in temp_custom_llms:
                            del temp_custom_llms[key]
                            # 立即保存更改
                            save_custom_llms(temp_custom_llms)
                            st.success("✅ 模型已删除！")
                            st.rerun()
                else:
                    st.caption("系统默认模型")
                    
            # 更新临时配置（如果可编辑）
            if llm_config.get("editable", True):
                temp_custom_llms[key] = {
                    "key": key,
                    "name": name,
                    "model": model,
                    "base_url": base_url,
                    "api_key": api_key,
                    "provider": provider,
                    "editable": True
                }
            # 更新默认模型的API密钥（即使不可编辑也要更新内存中的值）
            else:
                temp_custom_llms[key] = llm_config.copy()
                temp_custom_llms[key]["api_key"] = api_key_value
    
    st.markdown("---")
    
    # 添加新自定义LLM
    st.header("➕ 添加自定义LLM")
    with st.form("new_custom_llm"):
        new_key = st.text_input("唯一标识符 (例如: my-custom-model)")
        new_name = st.text_input("显示名称 (例如: 我的自定义模型)")
        new_model = st.text_input("模型标识 (例如: gpt-4)")
        new_base_url = st.text_input("API端点")
        new_api_key = st.text_input("API密钥", type="password")
        new_provider = st.selectbox("提供商", ["openai", "azure"])
        
        if st.form_submit_button("➕ 添加自定义模型"):
            if new_key and new_name and new_model and new_base_url and new_api_key:
                # 检查标识符是否已存在
                if new_key in temp_custom_llms:
                    st.error("❌ 标识符已存在，请使用不同的标识符")
                else:
                    temp_custom_llms[new_key] = {
                        "key": new_key,
                        "name": new_name,
                        "model": new_model,
                        "base_url": new_base_url,
                        "api_key": new_api_key,
                        "provider": new_provider,
                        "editable": True
                    }
                    # 立即保存更改
                    save_custom_llms(temp_custom_llms)
                    st.success("✅ 自定义模型已添加！")
                    st.rerun()
            else:
                st.error("❌ 请填写所有字段")
    
    st.markdown("---")
    
    # 保存配置按钮
    if st.button("💾 保存配置", type="primary"):
        configs_to_save = {
            "SELECTED_MODEL": selected_model,
        }
        
        # 保存默认模型的API密钥到各自的标准环境变量
        for key, llm_config in temp_custom_llms.items():
            if key == "qwen":
                qwen_key = st.session_state.get(f"key_{key}", "")
                if qwen_key:
                    configs_to_save["DASHSCOPE_API_KEY"] = qwen_key
                    
            elif key == "azure":
                azure_key = st.session_state.get(f"key_{key}", "")
                azure_url = st.session_state.get(f"url_{key}", "")
                if azure_key:
                    configs_to_save["AZURE_OPENAI_API_KEY"] = azure_key
                if azure_url:
                    configs_to_save["AZURE_OPENAI_ENDPOINT"] = azure_url
                # 部署名需要特殊处理，这里假设默认为gpt-4
                configs_to_save["AZURE_OPENAI_DEPLOYMENT_NAME"] = "gpt-4"
                    
            elif key == "grok":
                grok_key = st.session_state.get(f"key_{key}", "")
                if grok_key:
                    configs_to_save["GROK_API_KEY"] = grok_key
        
        # 保存自定义LLM配置到LLM_CONFIG环境变量（包含API密钥）
        llm_list = []
        for key, config in temp_custom_llms.items():
            # 确保API密钥也被保存到LLM_CONFIG中
            if key == "qwen":
                config["api_key"] = st.session_state.get(f"key_{key}", "")
            elif key == "azure":
                config["api_key"] = st.session_state.get(f"key_{key}", "")
            elif key == "grok":
                config["api_key"] = st.session_state.get(f"key_{key}", "")
            
            config["key"] = key
            llm_list.append(config)
        configs_to_save["LLM_CONFIG"] = json.dumps(llm_list, ensure_ascii=False)
        
        try:
            save_env_vars(configs_to_save)
            st.success("✅ 配置已保存成功！")
        except Exception as e:
            st.error(f"❌ 保存配置时出错: {str(e)}")
    
    # 显示当前配置状态
    st.markdown("---")
    st.header("📊 当前配置状态")
    
    configs = load_env_vars()
    current_model_name = temp_custom_llms.get(current_model, {}).get("name", "未知模型") if current_model in temp_custom_llms else "未知模型"
    st.info(f"当前选择的模型: **{current_model_name}**")
    
    # 检查各模型配置状态
    default_llms = get_default_llms()
    default_count = len([k for k in temp_custom_llms.keys() if k in default_llms])
    custom_count = len([k for k in temp_custom_llms.keys() if k not in default_llms])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("默认模型", f"✅ {default_count} 个")
    with col2:
        st.metric("自定义模型", f"✅ {custom_count} 个" if custom_count > 0 else "❌ 0 个")

if __name__ == "__main__":
    show_config_page()