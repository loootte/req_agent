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

    @patch('src.requirement_tracker.crew.requirement_crew')
    def test_requirement_document_generation(self, mock_crew):
        """Test that requirement documents can be generated properly"""
        # Mock the crew and its kickoff method
        mock_crew.kickoff.return_value = "Generated requirement document in English with proper structure"
        
        # Run the crew with a sample input
        result = run_crew("Create a user login feature with email and password", "qwen")
        
        # Assertions
        self.assertEqual(result, "Generated requirement document in English with proper structure")
        mock_crew.kickoff.assert_called_once_with(inputs={"input_text": "Create a user login feature with email and password"})

    @patch('src.requirement_tracker.crew.requirement_crew')
    def test_analyzer_with_empty_input(self, mock_crew):
        """Test handling of empty input string"""
        # Mock the crew and its kickoff method
        mock_crew.kickoff.return_value = "Error: Empty or invalid input"
        
        # Run the crew with an empty input
        result = run_crew("", "qwen")
        
        # Assertions
        self.assertEqual(result, "Error: Empty or invalid input")
        mock_crew.kickoff.assert_called_once_with(inputs={"input_text": ""})


if __name__ == '__main__':
    unittest.main()