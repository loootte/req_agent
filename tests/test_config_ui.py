import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.requirement_tracker.config_ui import ConfigManager


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


if __name__ == '__main__':
    unittest.main()