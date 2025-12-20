import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.requirement_tracker.webapp import show_main_page, load_env_vars, load_custom_llms


class TestWebApp(unittest.TestCase):

    @patch('streamlit.title')
    @patch('streamlit.markdown')
    @patch('streamlit.info')
    @patch('streamlit.header')
    @patch('streamlit.radio')
    @patch('streamlit.text_area')
    @patch('streamlit.columns')
    @patch('streamlit.button')
    @patch('streamlit.warning')
    @patch('streamlit.error')
    @patch('streamlit.success')
    @patch('streamlit.spinner')
    @patch('os.getenv')
    @patch('src.requirement_tracker.webapp.load_env_vars')
    @patch('src.requirement_tracker.webapp.load_custom_llms')
    @patch('src.requirement_tracker.webapp.run_crew')
    def test_show_main_page_valid_input(self, mock_run_crew, mock_load_custom_llms, mock_load_env_vars,
                                       mock_getenv, mock_st_spinner, mock_st_success, mock_st_error,
                                       mock_st_warning, mock_st_button, mock_st_columns, mock_st_text_area,
                                       mock_st_radio, mock_st_header, mock_st_info, mock_st_markdown,
                                       mock_st_title):
        """Test main page with valid input"""
        # Setup mocks
        mock_load_env_vars.return_value = {"SELECTED_MODEL": "qwen"}
        mock_load_custom_llms.return_value = {
            "qwen": {
                "key": "qwen",
                "name": "通义千问(Qwen)",
                "model": "qwen-max",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "api_key": "",
                "provider": "openai",
                "editable": False
            }
        }
        mock_getenv.return_value = "test-api-key"
        mock_st_text_area.return_value = "Test user requirement"
        mock_st_radio.return_value = "qwen"
        mock_st_button.return_value = True
        mock_st_columns.return_value = (MagicMock(), MagicMock())
        mock_run_crew.return_value = "Test result"

        # Call the function
        show_main_page()

        # Verify that the main components were called
        mock_st_title.assert_called_once()
        mock_st_markdown.assert_called()
        mock_st_info.assert_called()
        mock_st_header.assert_called()
        mock_st_radio.assert_called()
        mock_st_text_area.assert_called()
        mock_st_button.assert_called()
        mock_run_crew.assert_called_once_with("Test user requirement", "qwen")
        mock_st_success.assert_called()

    @patch('streamlit.title')
    @patch('streamlit.markdown')
    @patch('streamlit.info')
    @patch('streamlit.header')
    @patch('streamlit.radio')
    @patch('streamlit.text_area')
    @patch('streamlit.columns')
    @patch('streamlit.button')
    @patch('streamlit.warning')
    @patch('streamlit.error')
    @patch('os.getenv')
    @patch('src.requirement_tracker.webapp.load_env_vars')
    @patch('src.requirement_tracker.webapp.load_custom_llms')
    def test_show_main_page_missing_env_vars(self, mock_load_custom_llms, mock_load_env_vars,
                                           mock_getenv, mock_st_error, mock_st_warning, mock_st_button,
                                           mock_st_columns, mock_st_text_area, mock_st_radio,
                                           mock_st_header, mock_st_info, mock_st_markdown, mock_st_title):
        """Test main page with missing environment variables"""
        # Setup mocks
        mock_load_env_vars.return_value = {"SELECTED_MODEL": "qwen"}
        mock_load_custom_llms.return_value = {
            "qwen": {
                "key": "qwen",
                "name": "通义千问(Qwen)",
                "model": "qwen-max",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "api_key": "",
                "provider": "openai",
                "editable": False
            }
        }
        mock_getenv.return_value = None  # Missing API key
        mock_st_text_area.return_value = "Test user requirement"
        mock_st_radio.return_value = "qwen"
        mock_st_button.return_value = True
        mock_st_columns.return_value = (MagicMock(), MagicMock())

        # Call the function
        show_main_page()

        # Verify that warnings were shown for missing env vars
        mock_st_warning.assert_called()

    @patch('streamlit.title')
    @patch('streamlit.markdown')
    @patch('streamlit.info')
    @patch('streamlit.header')
    @patch('streamlit.radio')
    @patch('streamlit.text_area')
    @patch('streamlit.columns')
    @patch('streamlit.button')
    @patch('streamlit.warning')
    @patch('streamlit.error')
    @patch('os.getenv')
    @patch('src.requirement_tracker.webapp.load_env_vars')
    @patch('src.requirement_tracker.webapp.load_custom_llms')
    def test_show_main_page_empty_input(self, mock_load_custom_llms, mock_load_env_vars,
                                       mock_getenv, mock_st_error, mock_st_warning, mock_st_button,
                                       mock_st_columns, mock_st_text_area, mock_st_radio,
                                       mock_st_header, mock_st_info, mock_st_markdown, mock_st_title):
        """Test main page with empty input"""
        # Setup mocks
        mock_load_env_vars.return_value = {"SELECTED_MODEL": "qwen"}
        mock_load_custom_llms.return_value = {
            "qwen": {
                "key": "qwen",
                "name": "通义千问(Qwen)",
                "model": "qwen-max",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "api_key": "",
                "provider": "openai",
                "editable": False
            }
        }
        mock_getenv.return_value = "test-api-key"
        mock_st_text_area.return_value = ""  # Empty input
        mock_st_radio.return_value = "qwen"
        mock_st_button.return_value = True
        mock_st_columns.return_value = (MagicMock(), MagicMock())

        # Call the function
        show_main_page()

        # Verify that error was shown for empty input
        mock_st_error.assert_called_with("请输入需求描述")

    @patch('streamlit.title')
    @patch('streamlit.markdown')
    @patch('streamlit.info')
    @patch('streamlit.header')
    @patch('streamlit.radio')
    @patch('streamlit.text_area')
    @patch('streamlit.columns')
    @patch('streamlit.button')
    @patch('streamlit.warning')
    @patch('streamlit.error')
    @patch('streamlit.success')
    @patch('streamlit.spinner')
    @patch('os.getenv')
    @patch('src.requirement_tracker.webapp.load_env_vars')
    @patch('src.requirement_tracker.webapp.load_custom_llms')
    @patch('src.requirement_tracker.webapp.run_crew')
    def test_show_main_page_run_crew_exception(self, mock_run_crew, mock_load_custom_llms, mock_load_env_vars,
                                             mock_getenv, mock_st_spinner, mock_st_success, mock_st_error,
                                             mock_st_warning, mock_st_button, mock_st_columns,
                                             mock_st_text_area, mock_st_radio, mock_st_header,
                                             mock_st_info, mock_st_markdown, mock_st_title):
        """Test main page when run_crew throws an exception"""
        # Setup mocks
        mock_load_env_vars.return_value = {"SELECTED_MODEL": "qwen"}
        mock_load_custom_llms.return_value = {
            "qwen": {
                "key": "qwen",
                "name": "通义千问(Qwen)",
                "model": "qwen-max",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "api_key": "",
                "provider": "openai",
                "editable": False
            }
        }
        mock_getenv.return_value = "test-api-key"
        mock_st_text_area.return_value = "Test user requirement"
        mock_st_radio.return_value = "qwen"
        mock_st_button.return_value = True
        mock_st_columns.return_value = (MagicMock(), MagicMock())
        mock_run_crew.side_effect = Exception("Test exception")

        # Call the function
        show_main_page()

        # Verify that error was shown for exception
        mock_st_error.assert_called()


if __name__ == '__main__':
    unittest.main()