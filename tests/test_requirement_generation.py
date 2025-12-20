import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.requirement_tracker.crew import run_crew


class TestRequirementGeneration(unittest.TestCase):
    """Test requirement document generation"""

    @patch('src.requirement_tracker.crew.create_crew')
    def test_requirement_document_generation(self, mock_create_crew):
        """Test that requirement documents can be generated properly"""
        # Mock the crew and its kickoff method
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = "Generated requirement document in English with proper structure"
        mock_create_crew.return_value = mock_crew_instance
        
        # Run the crew with a sample input
        result = run_crew("Create a user login feature with email and password", "qwen")
        
        # Assertions
        self.assertIn("Generated requirement document in English with proper structure", result)
        mock_create_crew.assert_called_once_with("qwen", None)

    @patch('src.requirement_tracker.crew.create_crew')
    def test_analyzer_with_empty_input(self, mock_create_crew):
        """Test handling of empty input string"""
        # Mock the crew and its kickoff method
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = ""
        mock_create_crew.return_value = mock_crew_instance
        
        # Run the crew with an empty input
        result = run_crew("", "qwen")
        
        # Assertions
        self.assertIsInstance(result, str)
        mock_create_crew.assert_called_once_with("qwen", None)


if __name__ == '__main__':
    unittest.main()