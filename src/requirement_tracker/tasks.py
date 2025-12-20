# tasks
from crewai import Task
from virtualenv.create import creator

from src.requirement_tracker.crew import analyzer

task1 = Task(
    description="""
    输入文字：{input_text}
    请输出JSON格式：
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
    agent=analyzer
)

task2 = Task(
    description="""
    使用上一步JSON：
    1. 用create_ado_feature工具创建Feature（summary + 所有章节作为description）
    2. 生成HTML文档
    3. 用create_confluence_page创建页面，标题先用summary
    4. 用update_confluence_title更新标题为 "BR {{feature_id}} {{summary}}"
    """,
    expected_output="最终Confluence页面链接和Feature ID",
    agent=creator
)