# RequirementTracker

欢迎使用 RequirementTracker 项目，这是一个基于 [crewAI](https://crewai.com) 构建的多智能体AI系统。该系统能够自动将非正式的需求描述转换为结构化的需求文档，并以专业的格式输出。

## 功能特点

- 将自然语言形式的需求描述转换为结构化需求文档
- 以英文生成需求分析师的输出结果
- 以带 Markdown 格式的文本形式输出最终文档
- 提供命令行界面和Web界面两种交互方式
- 模拟显示将要创建的 Azure DevOps 工作项 ID 和 Confluence 页面链接
- 支持多种AI模型：通义千问(Qwen)、Azure OpenAI (Microsoft Copilot基础) 和 Grok (xAI)
- Web界面支持图形化配置LLM模型和API密钥
- 支持添加、编辑和删除自定义LLM配置
- 所有模型配置以结构化JSON格式存储在.env文件中

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

在使用前，需要配置相关环境变量。您可以通过以下两种方式之一进行配置：

### 方式一：使用 Web 界面配置（推荐）

运行 Web 界面后，在左侧边栏选择「LLM 配置」页面，可以通过图形界面配置所有必要的 API 密钥和模型选项。

### 方式二：直接编辑 .env 文件

请在项目根目录下的 `.env` 文件中添加以下配置：

```env
# 默认选择的模型 (qwen, azure, grok, 或自定义模型标识符)
SELECTED_MODEL=qwen

# 通义千问 API 密钥 (任选其一或两者都配置)
DASHSCOPE_API_KEY=your-dashscope-api-key

# Azure OpenAI 配置 (Microsoft Copilot 基础)
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4  # 或 gpt-3.5-turbo

# xAI Grok API 密钥
GROK_API_KEY=your-xai-api-key

# LLM模型配置（所有模型配置存储在一个JSON数组中）
LLM_CONFIG=[{"key": "qwen", "name": "通义千问 (Qwen)", "model": "qwen-max", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "api_key": "", "provider": "openai", "editable": false}, {"key": "azure", "name": "Azure OpenAI (Microsoft Copilot基础)", "model": "azure/gpt-4", "base_url": "", "api_key": "", "provider": "azure", "editable": false}, {"key": "grok", "name": "Grok (xAI)", "model": "grok-beta", "base_url": "https://api.x.ai/v1", "api_key": "", "provider": "openai", "editable": false}]

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

您可以使用 `--model` 参数选择不同的AI模型：
```bash
# 使用默认的 Qwen 模型
python src/main.py

# 或明确指定使用 Qwen 模型
python src/main.py --model qwen

# 使用 Azure OpenAI 模型
python src/main.py --model azure

# 使用 Grok 模型
python src/main.py --model grok

# 使用自定义模型 (需要先在配置中添加)
python src/main.py --model your-custom-model-id
```

### Web界面

要启动 RequirementTracker Web 界面，请在项目根目录下运行：

```bash
streamlit run src/requirement_tracker/webapp.py
```

在浏览器中打开提供的地址，即可通过图形界面输入需求并查看结果。Web界面具有以下功能：

1. **主页** - 输入需求并选择要使用的AI模型
2. **LLM 配置** - 图形化配置各种AI模型的API密钥和端点

在主页中，您可以：
- 查看当前配置的默认AI模型
- 临时更换要使用的模型（包括自定义模型）
- 输入需求描述并处理

在配置页面中，您可以：
- 设置默认使用的AI模型
- 配置各个AI模型的API密钥和相关参数
- 添加、编辑和删除自定义LLM配置
- 查看当前各模型的配置状态

#### 模型配置管理

在「LLM 配置」页面中，所有模型（包括默认模型和自定义模型）都在统一界面中管理：

1. **统一的配置存储**：
   - 所有模型配置存储在单个LLM_CONFIG环境变量中
   - 配置以JSON数组格式存储，每个模型占数组的一个元素
   - 默认模型显示为锁定状态（不可删除）

2. **默认模型**：
   - 包括通义千问、Azure OpenAI、Grok
   - 显示为锁定状态（不可删除）
   - API密钥仍存储在传统环境变量中以保持兼容性

3. **自定义模型**：
   - 可以添加、编辑和删除
   - 需要提供完整的配置信息（名称、模型标识、API端点、API密钥、提供商类型）
   - 配置信息存储在LLM_CONFIG环境变量中

## 项目结构

```
src/
├── requirement_tracker/
│   ├── agents.py      # 定义智能体角色和能力
│   ├── tasks.py       # 定义任务流程
│   ├── tools.py       # 实现具体工具函数
│   ├── crew.py        # 组装智能体团队
│   ├── webapp.py      # Web应用主界面
│   └── config.py      # Web配置界面
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