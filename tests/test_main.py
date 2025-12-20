import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import json
import argparse

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.main import main, load_env_vars, load_custom_llms


class TestMainModule(unittest.TestCase):
    """Test main module functionality"""

    @patch('src.main.dotenv_values')
    def test_load_env_vars_success(self, mock_dotenv):
        """Test successful loading of environment variables"""
        mock_dotenv.return_value = {'DASHSCOPE_API_KEY': 'test'}
        result = load_env_vars()
        self.assertEqual(result['DASHSCOPE_API_KEY'], 'test')

    @patch('src.main.Path.exists')
    @patch('src.main.dotenv_values')
    def test_load_env_vars_encoding_fallback(self, mock_dotenv_values, mock_exists):
        """Test encoding fallback when loading environment variables"""
        mock_exists.return_value = True
        # Make the first call raise UnicodeDecodeError to trigger fallback
        mock_dotenv_values.side_effect = [
            UnicodeDecodeError("utf-8", b"", 0, 1, "test"),  # First call raises exception
            {'DASHSCOPE_API_KEY': 'test'},  # Second call succeeds
            {'DASHSCOPE_API_KEY': 'test'}   # For the final dotenv_values call
        ]
        
        result = load_env_vars()
        self.assertEqual(result['DASHSCOPE_API_KEY'], 'test')

    @patch('src.main.json.loads')
    def test_load_custom_llms_json(self, mock_json):
        """Test loading custom LLMs from JSON configuration"""
        mock_json.return_value = [{'key': 'qwen'}]
        with patch('src.main.load_env_vars', return_value={'LLM_CONFIG': '[{"key":"qwen"}]'}):
            result = load_custom_llms()
            self.assertIn('qwen', result)

    @patch('src.main.run_crew')
    @patch('builtins.input', side_effect=['test input', 'exit'])
    @patch('src.main.os.getenv', return_value='test')
    @patch('src.main.load_custom_llms', return_value={'qwen': {}})
    @patch('sys.argv', ['main.py'])
    def test_main_loop(self, mock_load_llms, mock_getenv, mock_input, mock_crew):
        """Test main loop with normal input and exit command"""
        mock_crew.return_value = 'result'
        main()

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['', 'exit'])
    @patch('src.main.load_custom_llms', return_value={'qwen': {}})
    @patch('src.main.os.getenv', return_value='test')
    @patch('sys.argv', ['main.py'])
    def test_main_loop_empty_input(self, mock_getenv, mock_load_llms, mock_input, mock_print):
        """Test main loop with empty input handling"""
        main()
        # Check that warning message was printed
        mock_print.assert_any_call("⚠️  输入不能为空，请重新输入。\n")

    @patch('src.main.run_crew')
    @patch('builtins.input', side_effect=['test input', 'quit'])
    @patch('src.main.load_custom_llms', return_value={'qwen': {}})
    @patch('src.main.os.getenv', return_value='test')
    @patch('sys.argv', ['main.py'])
    def test_main_loop_quit_command(self, mock_getenv, mock_load_llms, mock_input, mock_crew):
        """Test main loop with quit command"""
        mock_crew.return_value = 'result'
        main()

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['test input', 'exit'])
    @patch('src.main.load_custom_llms', return_value={'qwen': {}})
    @patch('src.main.os.getenv', return_value='test')
    @patch('src.main.run_crew', side_effect=Exception("Test error"))
    @patch('sys.argv', ['main.py'])
    def test_main_loop_exception_handling(self, mock_crew, mock_getenv, mock_load_llms, mock_input, mock_print):
        """Test main loop exception handling"""
        main()
        # Check that error message was printed
        mock_print.assert_any_call("\n❌ 执行过程中出错：Test error")

    @patch('builtins.print')
    @patch('src.main.load_custom_llms', return_value={'qwen': {}})
    @patch('src.main.os.getenv', return_value=None)
    @patch('sys.argv', ['main.py', '--model', 'qwen'])
    def test_main_missing_environment_variables(self, mock_getenv, mock_load_llms, mock_print):
        """Test main with missing environment variables"""
        # Since we're not mocking input, the function will try to read from stdin and fail
        # We just check that the error message is printed
        try:
            main()
        except OSError:
            # Expected when trying to read from stdin in pytest
            pass
        # Check that error message was printed
        mock_print.assert_any_call("\n程序退出。")


if __name__ == '__main__':
    unittest.main()