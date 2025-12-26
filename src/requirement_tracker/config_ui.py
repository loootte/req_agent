import streamlit as st  # 保持，但 mock 时替换
import json
from typing import Dict, Any
from .config_utils import (
    load_env_vars, 
    save_env_vars, 
    load_custom_llms, 
    save_custom_llms, 
    get_default_llms,
    initialize_default_llms_in_env
)


class ConfigManager:
    # ... 原类不变，覆盖已 100%
    def __init__(self):
        self.custom_llms = load_custom_llms()
        self.env_vars = load_env_vars()

    def get_default_model(self) -> str:
        return self.env_vars.get("SELECTED_MODEL", "qwen")

    def update_llm(self, key: str, updates: Dict[str, Any]) -> None:
        if key in self.custom_llms:
            self.custom_llms[key].update(updates)

    def add_llm(self, new_config: Dict[str, Any]) -> bool:
        key = new_config["key"]
        if key not in self.custom_llms:
            self.custom_llms[key] = new_config
            return True
        return False

    def delete_llm(self, key: str) -> bool:
        if key in self.custom_llms and self.custom_llms.get(key, {}).get("editable", True):
            del self.custom_llms[key]
            return True
        return False

    def save_all(self, selected_model: str) -> None:
        # 确保默认模型始终包含在配置中
        default_llms = get_default_llms()
        merged_llms = default_llms.copy()
        merged_llms.update(self.custom_llms)
        
        configs_to_save = {
            "SELECTED_MODEL": selected_model,
        }
        
        # 保存默认模型的API密钥到各自的标准环境变量
        for key, llm_config in merged_llms.items():
            if key == "qwen":
                qwen_key = llm_config.get("api_key", "")
                if qwen_key:
                    configs_to_save["DASHSCOPE_API_KEY"] = qwen_key
                    
            elif key == "azure":
                azure_key = llm_config.get("api_key", "")
                azure_url = llm_config.get("base_url", "")
                if azure_key:
                    configs_to_save["AZURE_OPENAI_API_KEY"] = azure_key
                if azure_url:
                    configs_to_save["AZURE_OPENAI_ENDPOINT"] = azure_url
                # 部署名需要特殊处理，这里假设默认为gpt-4
                configs_to_save["AZURE_OPENAI_DEPLOYMENT_NAME"] = "gpt-4"
                    
            elif key == "grok":
                grok_key = llm_config.get("api_key", "")
                if grok_key:
                    configs_to_save["GROK_API_KEY"] = grok_key
        
        # 保存自定义LLM配置到LLM_CONFIG环境变量（包含API密钥）
        llm_list = []
        for key, config in merged_llms.items():
            config["key"] = key
            llm_list.append(config)
        configs_to_save["LLM_CONFIG"] = json.dumps(llm_list, ensure_ascii=False)
        
        save_env_vars(configs_to_save)


def render_model_selector(manager: ConfigManager, st=st) -> str:
    """纯 UI: 渲染默认模型选择，返回 selected_model"""  # 新函数，覆盖 lines 55-62
    st.header("🤖 默认模型选择")
    current_model = manager.get_default_model()
    options = list(manager.custom_llms.keys())
    index = options.index(current_model) if current_model in options else 0
    return st.selectbox(
        "选择默认模型:",
        options=options,
        format_func=lambda x: manager.custom_llms[x]["name"],
        index=index
    )


def render_llm_configs(manager: ConfigManager, selected_model: str, st=st) -> Dict:
    """纯 UI: 渲染所有 LLM expander，返回 temp_custom_llms"""  # 覆盖 lines 80-234 的循环
    st.header("🔧 模型配置")
    temp_custom_llms = manager.custom_llms.copy()
    for key, llm_config in manager.custom_llms.items():
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
                    api_key_value = manager.env_vars.get("DASHSCOPE_API_KEY", llm_config.get("api_key", ""))
                elif key == "azure":
                    api_key_value = manager.env_vars.get("AZURE_OPENAI_API_KEY", llm_config.get("api_key", ""))
                elif key == "grok":
                    api_key_value = manager.env_vars.get("GROK_API_KEY", llm_config.get("api_key", ""))
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
                        if manager.delete_llm(key):
                            # 立即保存更改
                            manager.save_all(selected_model)
                            st.success("✅ 模型已删除！")
                            return temp_custom_llms  # 早返回，便于测试删除路径
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
                
    return temp_custom_llms


def handle_add_llm_form(manager: ConfigManager, selected_model: str, st=st) -> bool:
    """纯 UI: 渲染添加表单，返回是否添加成功"""  # 覆盖 lines 80-234 的 form 部分
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
                new_config = {
                    "key": new_key,
                    "name": new_name,
                    "model": new_model,
                    "base_url": new_base_url,
                    "api_key": new_api_key,
                    "provider": new_provider,
                    "editable": True
                }
                
                # 检查标识符是否已存在
                if not manager.add_llm(new_config):
                    st.error("❌ 标识符已存在，请使用不同的标识符")
                    return False
                else:
                    # 立即保存更改
                    manager.save_all(selected_model)
                    st.success("✅ 自定义模型已添加！")
                    return True
            else:
                st.error("❌ 请填写所有字段")
                return False
    return False


def show_config_page(st=st):
    st.set_page_config(
        page_title="LLM 配置",
        page_icon="⚙️",
        layout="wide"
    )

    st.title("⚙️ LLM 模型配置")

    # 初始化配置管理器
    manager = ConfigManager()
    
    # 如果没有模型配置，初始化默认配置
    if not manager.custom_llms:
        manager.custom_llms = initialize_default_llms_in_env()
    
    selected_model = render_model_selector(manager, st)
    st.markdown("---")
    temp_custom_llms = render_llm_configs(manager, selected_model, st)
    added = handle_add_llm_form(manager, selected_model, st)
    if added:
        st.rerun()
    st.markdown("---")
    
    # 保存配置按钮
    if st.button("💾 保存配置", type="primary"):
        try:
            manager.save_all(selected_model)
            st.success("✅ 配置已保存成功！")
        except Exception as e:
            st.error(f"❌ 保存配置时出错: {str(e)}")
    
    # 显示当前配置状态
    st.markdown("---")
    st.header("📊 当前配置状态")
    
    current_model_name = temp_custom_llms.get(selected_model, {}).get("name", "未知模型") if selected_model in temp_custom_llms else "未知模型"
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