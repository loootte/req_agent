#!/usr/bin/env python
import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import all test modules
from tests.test_requirement_generation import TestRequirementGeneration
from tests.test_llm_config import TestLLMConfig
from tests.test_web_interface import TestWebInterface

if __name__ == '__main__':
    # Create a test suite combining all tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests to the test suite
    suite.addTests(loader.loadTestsFromTestCase(TestRequirementGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestLLMConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestWebInterface))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())