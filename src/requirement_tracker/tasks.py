# tasks
from crewai import Task
# from src.requirement_tracker.crew import analyzer

generation_task = Task(
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

create_feature = Task(
    description="""
    使用上一步JSON生成ADO的Feature，包含以下字段：
    - [System.Title]: "summary"的值
    - [System.Description]: "goal"的值
    - [Custom.Problem]: "problem"的値
    - [Custom.Acceptance]: "criteria"の値
    - [System.WorkItemType]: "Feature" 
    - [System.AreaPath]: "Move and Sell\\01. Move and Sell Portfolio\\Iron Ore Product Group\\Portside IMS"
    并返回创建的ID和link。
    """,
    expected_output="格式化的テキスト、構造された要件ドキュメントと実際のADOワークアイテムIDおよびConfluenceページリンク",
    # agent将在运行時通過crew.py設定
)

# 提供任务描述和预期输出的访问，以便在crew.py中创建新实例
task1_description = generation_task.description
task1_expected_output = generation_task.expected_output

task2_description = create_feature.description
task2_expected_output = create_feature.expected_output

# 导出变量，以便测试可以访问
__all__ = ['generation_task', 'create_feature', 'task1_description', 'task1_expected_output', 'task2_description', 'task2_expected_output']