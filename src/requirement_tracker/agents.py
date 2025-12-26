# src/your_crew/agents.py
from crewai import Agent
from .tools import (
    create_ado_feature,
    create_confluence_page,
    update_confluence_title,
    # 如果你还有其他工具，如 create_jira_feature，可一并导入
)

def create_analyzer(llm):
    """
    需求分析师 Agent：负责将用户输入的随意文字整理成结构化的需求文档
    """
    return Agent(
        role="Senior Requirements Analyst",
        goal="""
        Extract core information from user-provided requirement descriptions in any form and organize them into a standard requirement document format, including the following fixed sections:
        - Problem Statement
        - Requirement/Goal
        - Artifacts (such as pages, interfaces, reports, etc.)
        - Acceptance Criteria (using Gherkin format: Given/When/Then preferred)
        - Dependency/Risk/Impact to current process
        The output must be strictly valid JSON format for subsequent Agent usage.
        """,
        backstory="""
        You are a product manager with over 10 years of experience who has been responsible for writing complex enterprise system requirements at large companies.
        You are proficient in best practices for requirements engineering and excel at extracting clear, actionable requirements from vague user descriptions.
        You are familiar with agile development processes and understand the importance of acceptance criteria for development and testing, always writing AC in clear, verifiable language.
        You are sensitive to business risks and process impacts, proactively identifying potential dependencies and risk points.
        Your output is rigorous and meticulous, never adding irrelevant content.
        """,
        llm=llm,
        allow_delegation=False,  # 分析任务不需要委托
        verbose=True
    )


def create_publisher(llm):
    """
    工作项与文档发布者 Agent：负责创建 ADO/Jira 工作项、发布 Confluence 页面并更新标题
    """
    return Agent(
        role="Documentation Formatter & Presenter",
        goal="""
        Transform structured requirement information into well-formatted markdown documentation and create actual work items and documents in external systems:
        1. Take the structured JSON from the previous task
        2. Parse the JSON to extract summary, problem, goal, and criteria
        3. Format it into a clean, professional markdown document with proper headings and structure
        4. Create actual ADO work item with the extracted information (title from summary, description from goal, problem statement from problem, acceptance criteria from criteria)， return the workitem ID
        5. Create actual Confluence page with the formatted content title: "BR <workitem ID> <summary>"
        6. Return the created work item ID and Confluence page link
        
        The output should be pure markdown text, not JSON. Use appropriate markdown headers (#, ##, ###), bullet points, and formatting.
        """,
        backstory="""
        You are a technical documentation specialist who excels at transforming structured technical information into beautifully formatted documents.
        You understand the importance of presenting information clearly and professionally, using appropriate formatting, spacing, and organization.
        You have direct access to Azure DevOps and Confluence APIs and can create actual work items and documentation pages.
        You provide real identifiers and links from the created items, ensuring proper integration with enterprise systems.
        You are capable of parsing JSON data to extract the necessary fields for creating work items.
        """,
        tools=[create_ado_feature, create_confluence_page, update_confluence_title],  # 使用实际工具来创建工作项和文档
        llm=llm,
        allow_delegation=False,  # Publishing tasks don't need delegation either
        verbose=True
    )