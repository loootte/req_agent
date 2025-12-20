import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.requirement_tracker.webapp import load_custom_llms
from src.requirement_tracker.config_utils import get_default_llms


class TestWebInterface(unittest.TestCase):
    """Test web interface functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.default_llms = get_default_llms()
        self.custom_llm = {
            "test": {
                "key": "test",
                "name": "Test Model",
                "model": "test-model",
                "base_url": "https://api.test.com/v1",
                "api_key": "test-api-key",
                "provider": "openai",
                "editable": True
            }
        }
        
        self.test_llm_config = {
            **self.default_llms,
            **self.custom_llm
        }

    @patch('src.requirement_tracker.config_utils.load_env_vars')
    def test_main_page_model_selection(self, mock_load_env_vars):
        """Test that models are available for selection on main page"""
        # Create a mock LLM_CONFIG JSON string
        llm_config_json = json.dumps(list(self.test_llm_config.values()), ensure_ascii=False)
        
        # Setup mock to return our test configuration
        mock_load_env_vars.return_value = {
            "LLM_CONFIG": llm_config_json
        }
        
        # Load custom LLMs (this is what the web app does)
        loaded_llms = load_custom_llms()
        
        # Assertions
        # Check that default models are present
        self.assertIn('qwen', loaded_llms)
        self.assertIn('azure', loaded_llms)
        self.assertIn('grok', loaded_llms)
        
        # Check that custom model is present
        self.assertIn('test', loaded_llms)
        self.assertEqual(loaded_llms['test']['name'], 'Test Model')
        
        # Check that all models have required fields
        for key, model in loaded_llms.items():
            self.assertIn('key', model)
            self.assertIn('name', model)
            self.assertIn('model', model)
            self.assertIn('provider', model)

    @patch('src.requirement_tracker.config_utils.load_env_vars')
    def test_model_selection_dropdown_options(self, mock_load_env_vars):
        """Test that model selection dropdown includes all available models"""
        # Create a mock LLM_CONFIG JSON string
        llm_config_json = json.dumps(list(self.test_llm_config.values()), ensure_ascii=False)
        
        # Setup mock to return our test configuration
        mock_load_env_vars.return_value = {
            "LLM_CONFIG": llm_config_json
        }
        
        # Load custom LLMs
        loaded_llms = load_custom_llms()
        
        # Get model options (keys) and display names (values)
        model_keys = list(loaded_llms.keys())
        model_display_names = [model['name'] for model in loaded_llms.values()]
        
        # Assertions
        self.assertIn('qwen', model_keys)
        self.assertIn('azure', model_keys)
        self.assertIn('grok', model_keys)
        self.assertIn('test', model_keys)
        
        self.assertIn('通义千问 (Qwen)', model_display_names)
        self.assertIn('Azure OpenAI (Microsoft Copilot基础)', model_display_names)
        self.assertIn('Grok (xAI)', model_display_names)
        self.assertIn('Test Model', model_display_names)

    @patch('src.requirement_tracker.config_utils.load_env_vars')
    def test_main_page_with_no_env_config(self, mock_load_env_vars):
        """Test main page behavior when no environment configuration exists"""
        # Setup mocks
        mock_load_env_vars.return_value = {}
        
        # Load custom LLMs - should fall back to defaults
        loaded_llms = load_custom_llms()
        
        # Assertions - should contain default models
        self.assertIn('qwen', loaded_llms)
        self.assertIn('azure', loaded_llms)
        self.assertIn('grok', loaded_llms)


if __name__ == '__main__':
    unittest.main()