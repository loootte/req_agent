import pytest
from unittest.mock import patch, MagicMock
import os
import json

from src.requirement_tracker.crew import (
    load_env_vars, 
    load_custom_llms, 
    get_llm, 
    _get_qwen_llm, 
    _get_grok_llm,
    create_crew,
    run_crew
)

# 注意：由于Azure依赖项问题，暂时不测试Azure相关功能

@pytest.fixture
def mock_env():
    """提供测试用的环境变量"""
    return {
        'DASHSCOPE_API_KEY': 'test_qwen_key',
        'QWEN_MODEL_NAME': 'qwen-max',
        'QWEN_BASE_URL': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        'AZURE_OPENAI_API_KEY': 'test_azure_key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.azure.com',
        'AZURE_OPENAI_DEPLOYMENT_NAME': 'gpt-4',
        'GROK_API_KEY': 'test_grok_key',
        'GROK_MODEL_NAME': 'grok-beta',
        'GROK_BASE_URL': 'https://api.x.ai/v1',
        'SELECTED_MODEL': 'qwen'
    }

@pytest.fixture
def mock_custom_llms():
    """提供测试用的自定义LLM配置"""
    return {
        'custom_model': {
            'key': 'custom_model',
            'name': 'Custom Model',
            'model': 'custom-model',
            'base_url': 'https://custom.com',
            'api_key': 'custom-key',
            'provider': 'openai',
            'editable': True
        }
    }

def test_get_qwen_llm(mock_env):
    """测试获取Qwen LLM实例"""
    llm = _get_qwen_llm(mock_env)
    assert llm.model == 'qwen-max'
    assert llm.base_url == 'https://dashscope.aliyuncs.com/compatible-mode/v1'
    assert llm.api_key == 'test_qwen_key'
    assert llm.provider == 'openai'

def test_get_grok_llm(mock_env):
    """测试获取Grok LLM实例"""
    llm = _get_grok_llm(mock_env)
    assert llm.model == 'grok-beta'
    assert llm.base_url == 'https://api.x.ai/v1'
    assert llm.api_key == 'test_grok_key'
    assert llm.provider == 'openai'

def test_get_llm_default(mock_env):
    """测试获取默认LLM实例"""
    with patch('src.requirement_tracker.crew.load_custom_llms', return_value={}):
        llm = get_llm(env_vars=mock_env)
        assert llm.model == 'qwen-max'  # 应该返回Qwen模型

def test_get_llm_qwen(mock_env):
    """测试获取Qwen LLM实例"""
    with patch('src.requirement_tracker.crew.load_custom_llms', return_value={}):
        llm = get_llm('qwen', mock_env)
        assert llm.model == 'qwen-max'

def test_get_llm_grok(mock_env):
    """测试获取Grok LLM实例"""
    with patch('src.requirement_tracker.crew.load_custom_llms', return_value={}):
        llm = get_llm('grok', mock_env)
        assert llm.model == 'grok-beta'

def test_get_llm_custom(mock_env, mock_custom_llms):
    """测试获取自定义LLM实例"""
    with patch('src.requirement_tracker.crew.load_custom_llms', return_value=mock_custom_llms):
        llm = get_llm('custom_model', mock_env)
        assert llm.model == 'custom-model'

def test_get_llm_invalid():
    """测试获取无效模型类型"""
    with patch('src.requirement_tracker.crew.load_custom_llms', return_value={}):
        # Mock _get_qwen_llm to avoid actual LLM instantiation
        with patch('src.requirement_tracker.crew._get_qwen_llm') as mock_get_qwen:
            mock_llm = MagicMock()
            mock_get_qwen.return_value = mock_llm
            llm = get_llm('invalid_model')
            # 应该返回默认的Qwen模型
            assert llm == mock_llm

@patch('src.requirement_tracker.crew.create_task1_instance')
@patch('src.requirement_tracker.crew.create_task2_instance')
@patch('src.requirement_tracker.crew.Crew')
@patch('src.requirement_tracker.crew.create_publisher')
@patch('src.requirement_tracker.crew.create_analyzer')
def test_create_crew(mock_create_analyzer, mock_create_publisher, mock_crew_class, mock_create_task2_instance, mock_create_task1_instance, mock_env):
    """测试创建Crew实例"""
    # 设置mock返回值
    mock_analyzer = MagicMock()
    mock_publisher = MagicMock()
    mock_task1_instance = MagicMock()
    mock_task2_instance = MagicMock()
    mock_crew_instance = MagicMock()
    
    mock_create_analyzer.return_value = mock_analyzer
    mock_create_publisher.return_value = mock_publisher
    mock_create_task1_instance.return_value = mock_task1_instance
    mock_create_task2_instance.return_value = mock_task2_instance
    mock_crew_class.return_value = mock_crew_instance

    # 创建crew
    crew = create_crew('qwen', mock_env)
    
    # 验证调用
    mock_create_analyzer.assert_called_once()
    mock_create_publisher.assert_called_once()
    mock_create_task1_instance.assert_called_once()
    mock_create_task2_instance.assert_called_once()
    mock_crew_class.assert_called_once()
    
    # 验证传递给Crew的参数
    args, kwargs = mock_crew_class.call_args
    assert kwargs.get('verbose') is True
    assert len(args) == 0  # 所有参数都应该是关键字参数
    assert 'agents' in kwargs
    assert 'tasks' in kwargs
    
    # 验证返回的crew
    assert crew == mock_crew_instance

@patch('src.requirement_tracker.crew.Crew')
@patch('src.requirement_tracker.crew.create_publisher')
@patch('src.requirement_tracker.crew.create_analyzer')
@patch('src.requirement_tracker.crew.create_task2_instance')
@patch('src.requirement_tracker.crew.create_task1_instance')
def test_run_crew_success(mock_create_task1_instance, mock_create_task2_instance, mock_create_analyzer, mock_create_publisher, mock_crew_class, mock_env):
    """测试成功运行Crew"""
    # 设置mock返回值
    mock_analyzer = MagicMock()
    mock_publisher = MagicMock()
    mock_task1_instance = MagicMock()
    mock_task2_instance = MagicMock()
    mock_crew_instance = MagicMock()
    
    mock_create_analyzer.return_value = mock_analyzer
    mock_create_publisher.return_value = mock_publisher
    mock_create_task1_instance.return_value = mock_task1_instance
    mock_create_task2_instance.return_value = mock_task2_instance
    mock_crew_class.return_value = mock_crew_instance
    mock_crew_instance.kickoff.return_value = "Test result"
    
    result = run_crew("test demand", "qwen", mock_env)
    assert "Test result" in result

def test_run_crew_error(mock_env):
    """测试运行Crew时发生错误"""
    with patch('src.requirement_tracker.crew.get_llm') as mock_get_llm:
        mock_get_llm.side_effect = Exception("Test error")
        result = run_crew("test demand", "qwen", mock_env)
        assert "Error" in result
        assert "Test error" in result

# 添加额外的测试用例以提高覆盖率

def test_load_env_vars_file_not_exists():
    """测试环境变量文件不存在的情况"""
    with patch('src.requirement_tracker.crew.Path.exists', return_value=False):
        result = load_env_vars()
        assert result == {}

@patch('src.requirement_tracker.crew.dotenv_values')
def test_load_env_vars_unicode_error_then_success(mock_dotenv_values):
    """测试环境变量文件Unicode解码错误然后成功的场景"""
    # 模拟第一次调用抛出UnicodeDecodeError，第二次调用成功
    mock_dotenv_values.side_effect = [UnicodeDecodeError('utf-8', b'', 0, 1, 'reason'), {'TEST_KEY': 'test_value'}]
    
    with patch('src.requirement_tracker.crew.Path.exists', return_value=True):
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = 'content'
            result = load_env_vars()
            assert result == {'TEST_KEY': 'test_value'}

def test_load_custom_llms_with_valid_config(mock_env):
    """测试加载自定义LLM配置"""
    with patch('src.requirement_tracker.crew.load_env_vars', return_value={
        'LLM_CONFIG': '[{"key": "test_model", "model": "test-model", "base_url": "https://test.com", "api_key": "test-key", "provider": "openai"}]'
    }):
        result = load_custom_llms()
        assert 'test_model' in result
        assert result['test_model']['model'] == 'test-model'

def test_load_custom_llms_with_invalid_config(mock_env):
    """测试加载无效的自定义LLM配置"""
    with patch('src.requirement_tracker.crew.load_env_vars', return_value={
        'LLM_CONFIG': 'invalid_json'
    }):
        result = load_custom_llms()
        assert result == {}  # 应该返回空字典

def test_load_custom_llms_with_legacy_format(mock_env):
    """测试使用旧格式加载自定义LLM配置"""
    with patch('src.requirement_tracker.crew.load_env_vars', return_value={
        'LLM_CONFIG_TEST': '{"model": "test-model", "base_url": "https://test.com", "api_key": "test-key", "provider": "openai"}'
    }):
        result = load_custom_llms()
        assert 'test' in result
        assert result['test']['model'] == 'test-model'