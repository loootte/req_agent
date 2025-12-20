# RequirementTracker

欢迎使用 RequirementTracker 项目，这是一个基于 [crewAI](https://crewai.com) 构建的多智能体AI系统。该系统能够自动将非正式的需求描述转换为结构化的需求文档，并以专业的格式输出。

## 功能特点

- 将自然语言形式的需求描述转换为结构化需求文档
- 以英文生成需求分析师的输出结果
- 以带 Markdown 格式的文本形式输出最终文档
- 提供命令行界面和Web界面两种交互方式
- 模拟显示将要创建的 Azure DevOps 工作项 ID 和 Confluence 页面链接

## 安装说明

确保您的系统已安装 Python >=3.10 <3.14。本项目使用 [UV](https://docs.astral.sh/uv/) 进行依赖管理。

首先，如果您尚未安装 uv，请运行：

```bash
pip install uv
```

接下来，导航到项目目录并安装依赖项：

```bash
crewai install
```

或者使用 uv 直接安装：

```bash
uv pip install -r pyproject.toml
```

## 环境配置

在使用前，需要配置相关环境变量。请在项目根目录下的 `.env` 文件中添加以下配置：

```env
# 阿里云通义千问 API 密钥
DASHSCOPE_API_KEY=your-dashscope-api-key

# Confluence 配置
CONFLUENCE_URL=https://your-company.atlassian.net
CONFLUENCE_TOKEN=your-confluence-api-token
CONFLUENCE_SPACE=YOUR_SPACE_KEY
CONFLUENCE_PARENT_ID=optional-parent-page-id

# Azure DevOps 配置
ADO_ORG_URL=https://dev.azure.com/your-organization
ADO_PAT=your-personal-access-token
ADO_PROJECT=YourProjectName
```

## 使用方法

RequirementTracker 提供了两种使用方式：命令行界面和Web界面。

### 命令行界面

要启动 RequirementTracker 命令行界面并开始处理需求，请在项目根目录下运行：

```bash
python src/main.py
```

程序启动后，按照提示输入您的需求描述，系统将自动为您：
1. 分析需求并生成结构化文档（以英文输出）
2. 以带 Markdown 格式的文本形式输出最终文档
3. 模拟显示将要创建的 Azure DevOps 工作项 ID 和 Confluence 页面链接

### Web界面

要启动 RequirementTracker Web 界面，请在项目根目录下运行：

```bash
streamlit run src/requirement_tracker/webapp.py
```

在浏览器中打开提供的地址，即可通过图形界面输入需求并查看结果。

## 项目结构

```
src/
├── requirement_tracker/
│   ├── agents.py      # 定义智能体角色和能力
│   ├── tasks.py       # 定义任务流程
│   ├── tools.py       # 实现具体工具函数
│   ├── crew.py        # 组装智能体团队
│   └── webapp.py      # Web应用界面
└── main.py            # 命令行程序入口点
```

## 智能体介绍

### 需求分析师
负责将用户输入的非正式需求文本解析为标准化的结构化需求文档，包括问题陈述、目标、交付物、验收标准以及风险评估等内容。该分析师以英文输出结果。

### 文档格式化与展示者
负责将结构化需求文档格式化为专业的 Markdown 格式文本，并模拟显示将要创建的外部系统工作项和页面链接。

## 支持与反馈

如有任何问题或建议，请通过以下渠道联系我们：
- 访问 [crewAI 官方文档](https://docs.crewai.com)
- 提交问题到我们的 [GitHub 仓库](https://github.com/joaomdmoura/crewai)
- [加入 Discord 社区](https://discord.com/invite/X4JWnZnxPb)
