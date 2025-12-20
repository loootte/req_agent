import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
import json

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.requirement_tracker.config import save_custom_llms, load_custom_llms, get_default_llms


class TestLLMConfig(unittest.TestCase):
    """Test LLM configuration management"""

    def setUp(self):
        """Set up test fixtures"""
        self.default_llms = get_default_llms()
        self.custom_llm = {
            "test_model": {
                "key": "test_model",
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

    @patch('src.requirement_tracker.config.dotenv_values')
    @patch('builtins.open', new_callable=mock_open)
    def test_add_llm_configuration(self, mock_file, mock_dotenv_values):
        """Test adding a new LLM configuration"""
        # Setup mock for dotenv_values to return empty dict (no existing config)
        mock_dotenv_values.return_value = {}
        
        # Save custom LLMs
        save_custom_llms(self.test_llm_config)
        
        # Check that file was written
        mock_file.assert_called()
        handle = mock_file()
        handle.write.assert_called()
        
        # Verify the written content contains our test model
        written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
        self.assertIn('test_model', written_content)
        self.assertIn('Test Model', written_content)
        self.assertIn('test-api-key', written_content)

    @patch('src.requirement_tracker.config.dotenv_values')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_llm_configuration_with_added_model(self, mock_file, mock_dotenv_values):
        """Test loading LLM configuration after adding a model"""
        # Create a mock LLM_CONFIG JSON string
        llm_config_json = json.dumps(list(self.test_llm_config.values()), ensure_ascii=False)
        
        # Setup mock to return our test configuration
        mock_dotenv_values.return_value = {
            "LLM_CONFIG": llm_config_json
        }
        
        # Load custom LLMs
        loaded_llms = load_custom_llms()
        
        # Assertions
        self.assertIn('test_model', loaded_llms)
        self.assertEqual(loaded_llms['test_model']['name'], 'Test Model')
        self.assertEqual(loaded_llms['test_model']['api_key'], 'test-api-key')
        self.assertTrue(loaded_llms['test_model']['editable'])

    @patch('src.requirement_tracker.config.dotenv_values')
    @patch('builtins.open', new_callable=mock_open)
    def test_modify_llm_configuration(self, mock_file, mock_dotenv_values):
        """Test modifying an existing LLM configuration"""
        # Initial configuration with a model to modify
        initial_config = self.test_llm_config.copy()
        modified_config = initial_config.copy()
        modified_config["test_model"]["name"] = "Modified Test Model"
        modified_config["test_model"]["api_key"] = "modified-api-key"
        
        # Setup mock for dotenv_values to return initial config
        llm_config_json = json.dumps(list(initial_config.values()), ensure_ascii=False)
        mock_dotenv_values.return_value = {
            "LLM_CONFIG": llm_config_json
        }
        
        # Save modified configuration
        save_custom_llms(modified_config)
        
        # Check that file was written with modified content
        mock_file.assert_called()
        handle = mock_file()
        handle.write.assert_called()
        
        # Verify the written content contains modified values
        written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
        self.assertIn('Modified Test Model', written_content)
        self.assertIn('modified-api-key', written_content)

    @patch('src.requirement_tracker.config.dotenv_values')
    @patch('builtins.open', new_callable=mock_open)
    def test_delete_llm_configuration(self, mock_file, mock_dotenv_values):
        """Test deleting an LLM configuration"""
        # Start with our test configuration
        initial_config = self.test_llm_config.copy()
        
        # Setup mock for dotenv_values to return initial config
        llm_config_json = json.dumps(list(initial_config.values()), ensure_ascii=False)
        mock_dotenv_values.return_value = {
            "LLM_CONFIG": llm_config_json
        }
        
        # Now "delete" the custom model by only saving default models
        save_custom_llms(self.default_llms)
        
        # Check that file was written
        mock_file.assert_called()
        handle = mock_file()
        handle.write.assert_called()
        
        # Verify the written content does not contain the deleted model
        written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
        self.assertNotIn('test_model', written_content)
        self.assertNotIn('Test Model', written_content)


if __name__ == '__main__':
    unittest.main()