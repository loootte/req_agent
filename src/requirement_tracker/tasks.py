# tasks
from crewai import Task
# from src.requirement_tracker.crew import analyzer

task1 = Task(
    description="""
    输入文字：{input_text}
    做出专业需求分析，添加必要的内容
    请用输出JSON格式：
    {{
        "summary": "简短标题",
        "problem": "Problem Statement内容",
        "goal": "Requirement/Goal内容",
        "artifacts": "Artifacts内容",
        "criteria": "Acceptance Criteria内容",
        "risks": "Dependency/Risk/Impact内容"
    }}
    """,
    expected_output="JSON字符串",
    # agent将在运行时通过crew.py设置
)

task2 = Task(
    description="""
    使用上一步JSON生成结构化英文需求文档，以markdown格式输出，包含以下章节：
    - Problem Statement
    - Requirement/Goal
    - Artifacts
    - Acceptance Criteria
    - Dependency/Risk/Impact to current process
    
    同时模拟显示将要创建的ADO工作项ID和Confluence页面链接（但不实际创建）。
    """,
    expected_output="格式化的markdown文本，包含结构化需求文档和模拟的ADO工作项ID及Confluence页面链接",
    # agent将在运行时通过crew.py设置
)

# 提供任务描述和预期输出的访问，以便在crew.py中创建新实例
task1_description = task1.description
task1_expected_output = task1.expected_output

task2_description = task2.description
task2_expected_output = task2.expected_output