# src/requirement_tracker/crew.py
from crewai import Crew, Task
from langchain_community.chat_models import ChatDashScope
import os
from .agents import create_analyzer, create_publisher
from .tasks import task1, task2  # 如果你也拆了tasks.py

# LLM配置
llm = ChatDashScope(
    model_name="qwen-max",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
)

# 创建Agent
analyzer = create_analyzer(llm)
publisher = create_publisher(llm)


# 组装Crew
requirement_crew = Crew(
    agents=[analyzer, publisher],
    tasks=[task1, task2],
    verbose=True
)

def run_crew(input_text: str):
    result = requirement_crew.kickoff(inputs={"input_text": input_text})
    return result