import pytest
from src.requirement_tracker.tools import format_doc


class TestFormatDoc:
    """测试格式化需求文档工具函数"""
    
    def test_format_doc_tool_properties(self):
        """测试format_doc工具的属性"""
        assert hasattr(format_doc, 'run')
        assert format_doc.name == "Format Requirement Document"
    
    def test_format_doc_success(self):
        """测试成功格式化需求文档"""
        result = format_doc.run(
            problem="Test Problem",
            goal="Test Goal", 
            artifacts="Test Artifacts",
            criteria="Test Criteria",
            risks="Test Risks"
        )
        
        # 验证结果包含问题陈述
        assert "Test Problem" in result
        assert "<h1>Problem Statement</h1>" in result