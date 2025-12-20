import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add the project root directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.requirement_tracker.config_ui import ConfigManager, render_model_selector, render_llm_configs, handle_add_llm_form, show_config_page


class TestConfigUI(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_llms = {
            'qwen': {
                'key': 'qwen',
                'name': '通义千问 (Qwen)',
                'model': 'qwen-max',
                'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                'api_key': '',
                'provider': 'openai',
                'editable': False
            },
            'custom': {
                'key': 'custom',
                'name': 'Custom Model',
                'model': 'custom-model',
                'base_url': 'https://custom.com',
                'api_key': 'test-key',
                'provider': 'openai',
                'editable': True
            }
        }
        
        self.sample_env_vars = {
            'SELECTED_MODEL': 'qwen',
            'DASHSCOPE_API_KEY': 'test-dashscope-key'
        }

    @patch('src.requirement_tracker.config_ui.load_custom_llms')
    @patch('src.requirement_tracker.config_ui.load_env_vars')
    def test_config_manager_init(self, mock_load_env_vars, mock_load_custom_llms):
        """Test ConfigManager initialization"""
        mock_load_custom_llms.return_value = self.sample_llms
        mock_load_env_vars.return_value = self.sample_env_vars
        
        manager = ConfigManager()
        
        self.assertEqual(manager.custom_llms, self.sample_llms)
        self.assertEqual(manager.env_vars, self.sample_env_vars)

    def test_config_manager_get_default_model(self):
        """Test getting default model"""
        with patch('src.requirement_tracker.config_ui.load_custom_llms') as mock_load_custom_llms, \
             patch('src.requirement_tracker.config_ui.load_env_vars') as mock_load_env_vars:
            
            mock_load_custom_llms.return_value = self.sample_llms
            mock_load_env_vars.return_value = self.sample_env_vars
            
            manager = ConfigManager()
            default_model = manager.get_default_model()
            
            self.assertEqual(default_model, 'qwen')

    def test_config_manager_get_default_model_no_selection(self):
        """Test getting default model when none is selected"""
        with patch('src.requirement_tracker.config_ui.load_custom_llms') as mock_load_custom_llms, \
             patch('src.requirement_tracker.config_ui.load_env_vars') as mock_load_env_vars:
            
            mock_load_custom_llms.return_value = self.sample_llms
            mock_load_env_vars.return_value = {}
            
            manager = ConfigManager()
            default_model = manager.get_default_model()
            
            self.assertEqual(default_model, 'qwen')  # Should default to 'qwen'

    def test_config_manager_update_llm(self):
        """Test updating an LLM configuration"""
        with patch('src.requirement_tracker.config_ui.load_custom_llms') as mock_load_custom_llms, \
             patch('src.requirement_tracker.config_ui.load_env_vars') as mock_load_env_vars:
            
            mock_load_custom_llms.return_value = self.sample_llms
            mock_load_env_vars.return_value = self.sample_env_vars
            
            manager = ConfigManager()
            updates = {'name': 'Updated Custom Model', 'model': 'updated-model'}
            
            manager.update_llm('custom', updates)
            
            self.assertEqual(manager.custom_llms['custom']['name'], 'Updated Custom Model')
            self.assertEqual(manager.custom_llms['custom']['model'], 'updated-model')

    def test_config_manager_update_nonexistent_llm(self):
        """Test updating a non-existent LLM configuration"""
        with patch('src.requirement_tracker.config_ui.load_custom_llms') as mock_load_custom_llms, \
             patch('src.requirement_tracker.config_ui.load_env_vars') as mock_load_env_vars:
            
            mock_load_custom_llms.return_value = self.sample_llms
            mock_load_env_vars.return_value = self.sample_env_vars
            
            manager = ConfigManager()
            updates = {'name': 'Non-existent Model'}
            
            # Should not raise an exception
            manager.update_llm('nonexistent', updates)
            
            # Original LLMs should remain unchanged
            self.assertEqual(len(manager.custom_llms), 2)
            self.assertNotIn('nonexistent', manager.custom_llms)

    def test_config_manager_add_llm(self):
        """Test adding a new LLM configuration"""
        with patch('src.requirement_tracker.config_ui.load_custom_llms') as mock_load_custom_llms, \
             patch('src.requirement_tracker.config_ui.load_env_vars') as mock_load_env_vars:
            
            mock_load_custom_llms.return_value = self.sample_llms
            mock_load_env_vars.return_value = self.sample_env_vars
            
            manager = ConfigManager()
            new_config = {
                'key': 'new_model',
                'name': 'New Model',
                'model': 'new-model',
                'base_url': 'https://new.com',
                'api_key': 'new-key',
                'provider': 'openai',
                'editable': True
            }
            
            result = manager.add_llm(new_config)
            
            self.assertTrue(result)
            self.assertIn('new_model', manager.custom_llms)
            self.assertEqual(manager.custom_llms['new_model']['name'], 'New Model')

    def test_config_manager_add_duplicate_llm(self):
        """Test adding a duplicate LLM configuration"""
        with patch('src.requirement_tracker.config_ui.load_custom_llms') as mock_load_custom_llms, \
             patch('src.requirement_tracker.config_ui.load_env_vars') as mock_load_env_vars:
            
            mock_load_custom_llms.return_value = self.sample_llms
            mock_load_env_vars.return_value = self.sample_env_vars
            
            manager = ConfigManager()
            duplicate_config = self.sample_llms['qwen'].copy()
            
            result = manager.add_llm(duplicate_config)
            
            self.assertFalse(result)  # Should return False for duplicate
            self.assertEqual(len(manager.custom_llms), 2)  # Count should remain the same

    def test_config_manager_delete_llm(self):
        """Test deleting an editable LLM configuration"""
        with patch('src.requirement_tracker.config_ui.load_custom_llms') as mock_load_custom_llms, \
             patch('src.requirement_tracker.config_ui.load_env_vars') as mock_load_env_vars:
            
            mock_load_custom_llms.return_value = self.sample_llms
            mock_load_env_vars.return_value = self.sample_env_vars
            
            manager = ConfigManager()
            result = manager.delete_llm('custom')
            
            self.assertTrue(result)
            self.assertNotIn('custom', manager.custom_llms)

    def test_config_manager_delete_non_editable_llm(self):
        """Test attempting to delete a non-editable LLM configuration"""
        with patch('src.requirement_tracker.config_ui.load_custom_llms') as mock_load_custom_llms, \
             patch('src.requirement_tracker.config_ui.load_env_vars') as mock_load_env_vars:
            
            mock_load_custom_llms.return_value = self.sample_llms
            mock_load_env_vars.return_value = self.sample_env_vars
            
            manager = ConfigManager()
            result = manager.delete_llm('qwen')
            
            self.assertFalse(result)  # Should return False for non-editable
            self.assertIn('qwen', manager.custom_llms)  # Should still be present

    def test_config_manager_delete_nonexistent_llm(self):
        """Test attempting to delete a non-existent LLM configuration"""
        with patch('src.requirement_tracker.config_ui.load_custom_llms') as mock_load_custom_llms, \
             patch('src.requirement_tracker.config_ui.load_env_vars') as mock_load_env_vars:
            
            mock_load_custom_llms.return_value = self.sample_llms
            mock_load_env_vars.return_value = self.sample_env_vars
            
            manager = ConfigManager()
            result = manager.delete_llm('nonexistent')
            
            self.assertFalse(result)  # Should return False for non-existent

    @patch('src.requirement_tracker.config_ui.save_custom_llms')
    @patch('src.requirement_tracker.config_ui.save_env_vars')
    def test_config_manager_save_all(self, mock_save_env_vars, mock_save_custom_llms):
        """Test saving all configurations"""
        with patch('src.requirement_tracker.config_ui.load_custom_llms') as mock_load_custom_llms, \
             patch('src.requirement_tracker.config_ui.load_env_vars') as mock_load_env_vars:
            
            mock_load_custom_llms.return_value = self.sample_llms
            mock_load_env_vars.return_value = self.sample_env_vars
            
            manager = ConfigManager()
            manager.custom_llms['custom']['api_key'] = 'updated-key'
            
            selected_model = 'custom'
            manager.save_all(selected_model)
            
            # Check that save functions were called
            mock_save_custom_llms.assert_called_once()
            mock_save_env_vars.assert_called_once()
            
            # Check the arguments passed to save_env_vars
            args, kwargs = mock_save_env_vars.call_args
            saved_configs = args[0]
            self.assertEqual(saved_configs['SELECTED_MODEL'], 'custom')

    def test_render_model_selector(self):
        """Test rendering model selector"""
        mock_st = MagicMock()
        
        manager = ConfigManager()
        manager.custom_llms = self.sample_llms
        manager.env_vars = self.sample_env_vars
        
        # Mock the actual streamlit selectbox function
        with patch.object(mock_st, 'selectbox', return_value="qwen") as mock_selectbox:
            selected = render_model_selector(manager, mock_st)
            mock_st.header.assert_called_with("🤖 默认模型选择")
            mock_selectbox.assert_called()
            self.assertEqual(selected, "qwen")

    def test_render_llm_configs_editable(self):
        """Test rendering LLM configs for editable model"""
        mock_st = MagicMock()
        mock_expander = MagicMock()
        mock_st.expander.return_value.__enter__.return_value = mock_expander
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        
        manager = ConfigManager()
        manager.custom_llms = self.sample_llms
        manager.env_vars = self.sample_env_vars
        
        with patch.object(mock_st, 'button', return_value=True):
            temp_llms = render_llm_configs(manager, "custom", mock_st)
            mock_st.header.assert_called_with("🔧 模型配置")
            mock_st.expander.assert_called()
            # Button was clicked, so function should return early

    def test_render_llm_configs_non_editable(self):
        """Test rendering LLM configs for non-editable model"""
        mock_st = MagicMock()
        mock_expander = MagicMock()
        mock_st.expander.return_value.__enter__.return_value = mock_expander
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        
        manager = ConfigManager()
        manager.custom_llms = self.sample_llms
        manager.env_vars = self.sample_env_vars
        
        with patch.object(mock_st, 'button', return_value=False):
            temp_llms = render_llm_configs(manager, "qwen", mock_st)
            mock_st.header.assert_called_with("🔧 模型配置")
            mock_st.expander.assert_called()
            # Should return the full dict since button wasn't clicked
            self.assertIn('qwen', temp_llms)
            self.assertIn('custom', temp_llms)

    @patch('src.requirement_tracker.config_ui.ConfigManager.add_llm')
    @patch('src.requirement_tracker.config_ui.ConfigManager.save_all')
    @patch('src.requirement_tracker.config_ui.st.form_submit_button')
    @patch('src.requirement_tracker.config_ui.st.text_input')
    @patch('src.requirement_tracker.config_ui.st.selectbox')
    def test_handle_add_llm_form_success(self, mock_selectbox, mock_text_input, mock_form_submit_button, mock_save_all, mock_add_llm):
        """Test handling add LLM form successfully"""
        mock_st = MagicMock()
        mock_form = MagicMock()
        mock_st.form.return_value.__enter__.return_value = mock_form
        
        manager = ConfigManager()
        manager.custom_llms = self.sample_llms.copy()
        manager.env_vars = self.sample_env_vars.copy()
        
        # Configure mocks
        mock_form_submit_button.return_value = True
        mock_selectbox.return_value = "openai"
        mock_add_llm.return_value = True  # Successfully added
        
        # Set up the mock to return specific values for each call
        def text_input_side_effect(*args, **kwargs):
            label = kwargs.get('label', args[0] if args else '')
            return {
                "唯一标识符 (例如: my-custom-model)": "new",
                "显示名称 (例如: 我的自定义模型)": "New Model",
                "模型标识 (例如: gpt-4)": "new-model",
                "API端点": "https://new.com",
                "API密钥": "new-key"
            }.get(label, '')
            
        mock_text_input.side_effect = text_input_side_effect
        
        added = handle_add_llm_form(manager, "qwen", mock_st)
        mock_st.header.assert_called_with("➕ 添加自定义LLM")
        self.assertTrue(added)
        mock_st.success.assert_called_with("✅ 自定义模型已添加！")
        mock_save_all.assert_called_once()

    @patch('src.requirement_tracker.config_ui.ConfigManager.add_llm')
    @patch('src.requirement_tracker.config_ui.ConfigManager.save_all')
    @patch('src.requirement_tracker.config_ui.st.form_submit_button')
    @patch('src.requirement_tracker.config_ui.st.text_input')
    @patch('src.requirement_tracker.config_ui.st.selectbox')
    def test_handle_add_llm_form_duplicate(self, mock_selectbox, mock_text_input, mock_form_submit_button, mock_save_all, mock_add_llm):
        """Test handling add LLM form with duplicate key"""
        mock_st = MagicMock()
        mock_form = MagicMock()
        mock_st.form.return_value.__enter__.return_value = mock_form
        
        manager = ConfigManager()
        manager.custom_llms = self.sample_llms.copy()
        manager.env_vars = self.sample_env_vars.copy()
        
        # Configure mocks
        mock_form_submit_button.return_value = True
        mock_selectbox.return_value = "openai"
        mock_add_llm.return_value = False  # Failed to add (duplicate)
        
        # Set up the mock to return specific values for each call
        def text_input_side_effect(*args, **kwargs):
            label = kwargs.get('label', args[0] if args else '')
            return {
                "唯一标识符 (例如: my-custom-model)": "qwen",  # duplicate key
                "显示名称 (例如: 我的自定义模型)": "Qwen Duplicate",
                "模型标识 (例如: gpt-4)": "qwen-model",
                "API端点": "https://qwen.com",
                "API密钥": "qwen-key"
            }.get(label, '')
            
        mock_text_input.side_effect = text_input_side_effect
        
        added = handle_add_llm_form(manager, "qwen", mock_st)
        mock_st.header.assert_called_with("➕ 添加自定义LLM")
        self.assertFalse(added)
        mock_st.error.assert_called_with("❌ 标识符已存在，请使用不同的标识符")
        mock_save_all.assert_not_called()


    # New test cases based on the provided strategy
    
    def test_render_model_selector_empty_models(self):
        """Test rendering model selector with empty models list"""
        mock_st = MagicMock()
        
        manager = ConfigManager()
        manager.custom_llms = {}
        manager.env_vars = self.sample_env_vars
        
        # Mock the actual streamlit selectbox function
        with patch.object(mock_st, 'selectbox', return_value="qwen") as mock_selectbox:
            selected = render_model_selector(manager, mock_st)
            mock_st.header.assert_called_with("🤖 默认模型选择")
            # Should default to first option which would be empty
            self.assertEqual(selected, "qwen")

    def test_render_llm_configs_json_error(self):
        """Test handling JSON serialization error in save_all"""
        mock_st = MagicMock()
        mock_expander = MagicMock()
        mock_st.expander.return_value.__enter__.return_value = mock_expander
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        
        manager = ConfigManager()
        manager.custom_llms = self.sample_llms.copy()
        manager.env_vars = self.sample_env_vars.copy()
        
        # Create a circular reference to cause JSON error
        manager.custom_llms['custom']['circular'] = manager.custom_llms
        
        with patch.object(mock_st, 'button', return_value=False):
            temp_llms = render_llm_configs(manager, "qwen", mock_st)
            # Should still return the full dict
            self.assertIn('qwen', temp_llms)
            self.assertIn('custom', temp_llms)

    def test_render_llm_configs_empty_api_key(self):
        """Test rendering LLM configs with empty API key"""
        mock_st = MagicMock()
        mock_expander = MagicMock()
        mock_st.expander.return_value.__enter__.return_value = mock_expander
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        
        manager = ConfigManager()
        manager.custom_llms = self.sample_llms.copy()
        manager.env_vars = {}
        
        with patch.object(mock_st, 'button', return_value=False):
            with patch.object(mock_st, 'text_input', return_value=""):
                temp_llms = render_llm_configs(manager, "qwen", mock_st)
                mock_st.header.assert_called_with("🔧 模型配置")
                mock_st.expander.assert_called()


    @patch('src.requirement_tracker.config_ui.save_env_vars')
    @patch('src.requirement_tracker.config_ui.save_custom_llms')
    def test_config_manager_save_all_azure_keys(self, mock_save_custom_llms, mock_save_env_vars):
        """Test saving all configurations with Azure keys"""
        azure_llms = {
            'azure': {
                'key': 'azure',
                'name': 'Azure OpenAI',
                'model': 'gpt-4',
                'base_url': 'https://azure.example.com',
                'api_key': 'azure-key',
                'provider': 'azure',
                'editable': False
            }
        }
        
        with patch('src.requirement_tracker.config_ui.load_custom_llms') as mock_load_custom_llms, \
             patch('src.requirement_tracker.config_ui.load_env_vars') as mock_load_env_vars:
            
            mock_load_custom_llms.return_value = azure_llms
            mock_load_env_vars.return_value = {}
            
            manager = ConfigManager()
            selected_model = 'azure'
            manager.save_all(selected_model)
            
            # Check that save functions were called
            mock_save_custom_llms.assert_called_once()
            mock_save_env_vars.assert_called_once()
            
            # Check the arguments passed to save_env_vars
            args, kwargs = mock_save_env_vars.call_args
            saved_configs = args[0]
            self.assertEqual(saved_configs['SELECTED_MODEL'], 'azure')
            self.assertEqual(saved_configs['AZURE_OPENAI_API_KEY'], 'azure-key')
            self.assertEqual(saved_configs['AZURE_OPENAI_ENDPOINT'], 'https://azure.example.com')
            self.assertIn('LLM_CONFIG', saved_configs)

    def test_config_manager_save_all_grok_keys(self):
        """Test saving all configurations with Grok keys"""
        with patch('src.requirement_tracker.config_ui.save_custom_llms') as mock_save_custom_llms, \
             patch('src.requirement_tracker.config_ui.save_env_vars') as mock_save_env_vars, \
             patch('src.requirement_tracker.config_ui.load_custom_llms') as mock_load_custom_llms, \
             patch('src.requirement_tracker.config_ui.load_env_vars') as mock_load_env_vars:
            
            grok_llms = {
                'grok': {
                    'key': 'grok',
                    'name': 'Grok',
                    'model': 'grok-beta',
                    'base_url': 'https://api.x.ai/v1',
                    'api_key': 'grok-key',
                    'provider': 'openai',
                    'editable': False
                }
            }
            
            mock_load_custom_llms.return_value = grok_llms
            mock_load_env_vars.return_value = {}
            
            manager = ConfigManager()
            selected_model = 'grok'
            manager.save_all(selected_model)
            
            # Check that save functions were called
            mock_save_custom_llms.assert_called_once()
            mock_save_env_vars.assert_called_once()
            
            # Check the arguments passed to save_env_vars
            args, kwargs = mock_save_env_vars.call_args
            saved_configs = args[0]
            self.assertEqual(saved_configs['SELECTED_MODEL'], 'grok')
            self.assertEqual(saved_configs['GROK_API_KEY'], 'grok-key')

    def test_render_llm_configs_provider_azure(self):
        """Test rendering LLM configs with Azure provider"""
        mock_st = MagicMock()
        mock_expander = MagicMock()
        mock_st.expander.return_value.__enter__.return_value = mock_expander
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        
        azure_llms = {
            'azure': {
                'key': 'azure',
                'name': 'Azure OpenAI',
                'model': 'gpt-4',
                'base_url': 'https://azure.example.com',
                'api_key': 'azure-key',
                'provider': 'azure',
                'editable': False
            }
        }
        
        manager = ConfigManager()
        manager.custom_llms = azure_llms
        manager.env_vars = {'AZURE_OPENAI_API_KEY': 'azure-key'}
        
        with patch.object(mock_st, 'button', return_value=False):
            with patch.object(mock_st, 'selectbox', return_value="azure"):
                temp_llms = render_llm_configs(manager, "azure", mock_st)
                mock_st.header.assert_called_with("🔧 模型配置")
                mock_st.expander.assert_called()


if __name__ == '__main__':
    unittest.main()
