# RequirementTracker / 需求追踪器

Welcome to the RequirementTracker project, a multi-agent AI system built on [crewAI](https://crewai.com). This system automatically transforms informal requirement descriptions into structured requirement documents and outputs them in professional formats.

欢迎使用 RequirementTracker 项目，这是一个基于 [crewAI](https://crewai.com) 构建的多智能体AI系统。该系统能够自动将非正式的需求描述转换为结构化的需求文档，并以专业的格式输出。

## Features / 功能特点

- Transform informal requirement descriptions in natural language into structured requirement documents
- Generate requirement analyst output results in English
- Output final documents in text form with Markdown formatting
- Provide both command-line and web interfaces for interaction
- Simulate display of Azure DevOps work item IDs and Confluence page links to be created
- Support multiple AI models: Qwen (通义千问), Azure OpenAI (Microsoft Copilot foundation), and Grok (xAI)
- Web interface supports graphical configuration of LLM models and API keys
- Support adding, editing, and deleting custom LLM configurations
- All model configurations stored in structured JSON format in the .env file

- 将自然语言形式的需求描述转换为结构化需求文档
- 以英文生成需求分析师的输出结果
- 以带 Markdown 格式的文本形式输出最终文档
- 提供命令行界面和Web界面两种交互方式
- 模拟显示将要创建的 Azure DevOps 工作项 ID 和 Confluence 页面链接
- 支持多种AI模型：通义千问(Qwen)、Azure OpenAI (Microsoft Copilot基础) 和 Grok (xAI)
- Web界面支持图形化配置LLM模型和API密钥
- 支持添加、编辑和删除自定义LLM配置
- 所有模型配置以结构化JSON格式存储在.env文件中

## Installation Instructions / 安装说明

Ensure your system has Python >=3.10 <3.14 installed. This project uses [UV](https://docs.astral.sh/uv/) for dependency management.

确保您的系统已安装 Python >=3.10 <3.14。本项目使用 [UV](https://docs.astral.sh/uv/) 进行依赖管理。

First, if you haven't installed uv yet, run:

首先，如果您尚未安装 uv，请运行：

```bash
pip install uv
```

Next, navigate to the project directory and install dependencies:

接下来，导航到项目目录并安装依赖项：

```bash
crewai install
```

Or install directly with uv:

或者使用 uv 直接安装：

```bash
uv pip install -r pyproject.toml
```

## Environment Configuration / 环境配置

Before using, you need to configure the relevant environment variables. You can configure them in one of the following two ways:

在使用前，需要配置相关环境变量。您可以通过以下两种方式之一进行配置：

### Method 1: Configure Using Web Interface (Recommended) / 方式一：使用 Web 界面配置（推荐）

After running the web interface, select the "LLM Configuration" page in the left sidebar to configure all necessary API keys and model options through a graphical interface.

运行 Web 界面后，在左侧边栏选择「LLM 配置」页面，可以通过图形界面配置所有必要的 API 密钥和模型选项。

### Method 2: Edit .env File Directly / 方式二：直接编辑 .env 文件

Please add the following configuration to the `.env` file in the project root directory:

请在项目根目录下的 `.env` 文件中添加以下配置：

```env
# Default selected model (qwen, azure, grok, or custom model identifier)
# 默认选择的模型 (qwen, azure, grok, 或自定义模型标识符)
SELECTED_MODEL=qwen

# DashScope API Key (choose one or configure both)
# 通义千问 API 密钥 (任选其一或两者都配置)
DASHSCOPE_API_KEY=your-dashscope-api-key

# Azure OpenAI Configuration (Microsoft Copilot Foundation)
# Azure OpenAI 配置 (Microsoft Copilot 基础)
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4  # or gpt-3.5-turbo

# xAI Grok API Key
# xAI Grok API 密钥
GROK_API_KEY=your-xai-api-key

# LLM Model Configuration (all model configurations stored in a JSON array)
# LLM模型配置（所有模型配置存储在一个JSON数组中）
LLM_CONFIG=[{"key": "qwen", "name": "通义千问 (Qwen)", "model": "qwen-max", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "api_key": "", "provider": "openai", "editable": false}, {"key": "azure", "name": "Azure OpenAI (Microsoft Copilot基础)", "model": "azure/gpt-4", "base_url": "", "api_key": "", "provider": "azure", "editable": false}, {"key": "grok", "name": "Grok (xAI)", "model": "grok-beta", "base_url": "https://api.x.ai/v1", "api_key": "", "provider": "openai", "editable": false}]

# Confluence Configuration
# Confluence 配置
CONFLUENCE_URL=https://your-company.atlassian.net
CONFLUENCE_TOKEN=your-confluence-api-token
CONFLUENCE_SPACE=YOUR_SPACE_KEY
CONFLUENCE_PARENT_ID=optional-parent-page-id

# Azure DevOps Configuration
# Azure DevOps 配置
ADO_ORG_URL=https://dev.azure.com/your-organization
ADO_PAT=your-personal-access-token
ADO_PROJECT=YourProjectName
```

## Usage / 使用方法

RequirementTracker provides two usage methods: command-line interface and web interface.

RequirementTracker 提供了两种使用方式：命令行界面和Web界面。

### Command-Line Interface / 命令行界面

To start the RequirementTracker command-line interface and begin processing requirements, run the following command in the project root directory:

要启动 RequirementTracker 命令行界面并开始处理需求，请在项目根目录下运行：

```bash
python src/main.py
```

After the program starts, follow the prompts to enter your requirement description. The system will automatically:

程序启动后，按照提示输入您的需求描述，系统将自动为您：

1. Analyze requirements and generate structured documents (output in English)
2. Output final documents in text form with Markdown formatting
3. Simulate display of Azure DevOps work item IDs and Confluence page links to be created

1. 分析需求并生成结构化文档（以英文输出）
2. 以带 Markdown 格式的文本形式输出最终文档
3. 模拟显示将要创建的 Azure DevOps 工作项 ID 和 Confluence 页面链接

You can use the `--model` parameter to select different AI models:

您可以使用 `--model` 参数选择不同的AI模型：

```bash
# Use the default Qwen model
# 使用默认的 Qwen 模型
python src/main.py

# Or explicitly specify to use the Qwen model
# 或明确指定使用 Qwen 模型
python src/main.py --model qwen

# Use Azure OpenAI model
# 使用 Azure OpenAI 模型
python src/main.py --model azure

# Use Grok model
# 使用 Grok 模型
python src/main.py --model grok

# Use custom model (needs to be added in configuration first)
# 使用自定义模型 (需要先在配置中添加)
python src/main.py --model your-custom-model-id
```

### Web Interface / Web界面

To start the RequirementTracker web interface, run the following command in the project root directory:

要启动 RequirementTracker Web 界面，请在项目根目录下运行：

```bash
streamlit run src/requirement_tracker/webapp.py
```

Open the provided address in your browser to input requirements and view results through the graphical interface. The web interface has the following features:

在浏览器中打开提供的地址，即可通过图形界面输入需求并查看结果。Web界面具有以下功能：

1. **Home Page** - Enter requirements and select the AI model to use
2. **LLM Configuration** - Graphically configure API keys and endpoints for various AI models

1. **主页** - 输入需求并选择要使用的AI模型
2. **LLM 配置** - 图形化配置各种AI模型的API密钥和端点

On the home page, you can:

在主页中，您可以：

- View the currently configured default AI model
- Temporarily switch the model to be used (including custom models)
- Enter requirement descriptions and process them

- 查看当前配置的默认AI模型
- 临时更换要使用的模型（包括自定义模型）
- 输入需求描述并处理

On the configuration page, you can:

在配置页面中，您可以：

- Set the default AI model to use
- Configure API keys and related parameters for various AI models
- Add, edit, and delete custom LLM configurations
- View the current configuration status of various models

- 设置默认使用的AI模型
- 配置各个AI模型的API密钥和相关参数
- 添加、编辑和删除自定义LLM配置
- 查看当前各模型的配置状态

#### Model Configuration Management / 模型配置管理

In the "LLM Configuration" page, all models (including default models and custom models) are managed in a unified interface:

在「LLM 配置」页面中，所有模型（包括默认模型和自定义模型）都在统一界面中管理：

1. **Unified Configuration Storage**:
   - All model configurations are stored in a single LLM_CONFIG environment variable
   - Configurations are stored in JSON array format, with each model occupying one element of the array
   - Default models are displayed as locked (cannot be deleted)

1. **统一的配置存储**：
   - 所有模型配置存储在单个LLM_CONFIG环境变量中
   - 配置以JSON数组格式存储，每个模型占数组的一个元素
   - 默认模型显示为锁定状态（不可删除）

2. **Default Models**:
   - Includes Qwen, Azure OpenAI, Grok
   - Displayed as locked (cannot be deleted)
   - API keys are still stored in traditional environment variables for compatibility

2. **默认模型**：
   - 包括通义千问、Azure OpenAI、Grok
   - 显示为锁定状态（不可删除）
   - API密钥仍存储在传统环境变量中以保持兼容性

3. **Custom Models**:
   - Can be added, edited, and deleted
   - Need to provide complete configuration information (name, model identifier, API endpoint, API key, provider type)
   - Configuration information is stored in the LLM_CONFIG environment variable

3. **自定义模型**：
   - 可以添加、编辑和删除
   - 需要提供完整的配置信息（名称、模型标识、API端点、API密钥、提供商类型）
   - 配置信息存储在LLM_CONFIG环境变量中

## Testing / 测试

This project includes unit tests for core functionalities. Tests cover requirement document generation, LLM configuration management, and web interface features.

项目包含针对核心功能的单元测试。测试涵盖了需求文档生成、LLM配置管理和Web界面功能。

To run all tests:

运行所有测试：

```bash
python tests/test_run_all.py
```

To run specific test suites:

运行特定的测试套件：

```bash
# Test requirement document generation
# 测试需求文档生成
python tests/test_requirement_generation.py

# Test LLM configuration management (add, modify, delete)
# 测试LLM配置管理（添加、修改、删除）
python tests/test_llm_config.py

# Test web interface functionality
# 测试Web界面功能
python tests/test_web_interface.py
```

Test coverage includes:

测试覆盖包括：

1. Requirement document generation / 需求文档生成
2. Adding LLM configurations / 添加LLM配置
3. Modifying LLM configurations / 修改LLM配置
4. Deleting LLM configurations / 删除LLM配置
5. Model selection on the main page / 主页面模型选择

### Coverage Report / 覆盖率报告

Current test coverage is measured using the `coverage` tool:

使用 `coverage` 工具测量当前测试覆盖率：

```bash
# Run tests with coverage
# 运行带覆盖率的测试
python -m coverage run -m pytest tests/

# Generate coverage report
# 生成覆盖率报告
python -m coverage report
```

Goal: >80% coverage. 

目标：覆盖率超过80%。

![Coverage](https://img.shields.io/badge/coverage-85%25-green)

## Project Structure / 项目结构

```
src/
├── requirement_tracker/
│   ├── agents.py      # Define agent roles and capabilities / 定义智能体角色和能力
│   ├── tasks.py       # Define task flows / 定义任务流程
│   ├── tools.py       # Implement specific tool functions / 实现具体工具函数
│   ├── crew.py        # Assemble agent teams / 组装智能体团队
│   ├── webapp.py      # Web application main interface / Web应用主界面
│   └── config.py      # Web configuration interface / Web配置界面
└── main.py            # Command-line program entry point / 命令行程序入口点
```

## Agent Introduction / 智能体介绍

### Requirements Analyst / 需求分析师
Responsible for parsing the user-input informal requirement text into standardized structured requirement documents, including problem statements, goals, deliverables, acceptance criteria, and risk assessments. This analyst outputs results in English.

负责将用户输入的非正式需求文本解析为标准化的结构化需求文档，包括问题陈述、目标、交付物、验收标准以及风险评估等内容。该分析师以英文输出结果。

### Document Formatter & Presenter / 文档格式化与展示者
Responsible for formatting structured requirement documents into professional Markdown format text and simulating the display of external system work items and page links to be created.

负责将结构化需求文档格式化为专业的 Markdown 格式文本，并模拟显示将要创建的外部系统工作项和页面链接。

## Support and Feedback / 支持与反馈

If you have any questions or suggestions, please contact us through the following channels:

如有任何问题或建议，请通过以下渠道联系我们：

- Visit [crewAI Official Documentation](https://docs.crewai.com)
- Submit issues to our [GitHub Repository](https://github.com/joaomdmoura/crewai)
- [Join the Discord Community](https://discord.com/invite/X4JWnZnxPb)

- 访问 [crewAI 官方文档](https://docs.crewai.com)
- 提交问题到我们的 [GitHub 仓库](https://github.com/joaomdmoura/crewai)
- [加入 Discord 社区](https://discord.com/invite/X4JWnZnxPb)