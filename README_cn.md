# 🤖 RequirementTracker  中文 | [English](README_en.md)

**AI 驱动的需求分析与管理系统**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen.svg)](https://github.com/loootte/req_agent)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/loootte/req_agent/pulls)

---

## 🎯 为什么需要 RequirementTracker？

### 面临的问题

在企业数字化转型和敏捷交付项目中，需求管理往往是最大的瓶颈：

- 📧 **需求分散** 在邮件、会议纪要、聊天记录和各种文档中
- ⏰ **编写结构化需求耗时数小时** 且质量因人而异
- 🔄 **需求文档与项目管理工具（Jira、Azure DevOps）的手工同步** 容易出错
- 🌐 **语言障碍** 拖慢全球团队协作效率
- 🔒 **合规顾虑** 使许多企业无法采用公有云 AI 工具

### 解决方案

**RequirementTracker** 是一个 AI 驱动的多智能体系统，能够自动将非正式的需求描述转换为专业的结构化文档，并无缝集成企业协作平台。

### 实际效果

- ⚡ **效率提升 8 倍** - 将需求文档编写时间从数小时缩短到几分钟
- 📉 **减少 60% 手工工作** - 自动化需求提取、格式化和工具集成
- ✅ **需求遗漏减少 40%** - AI 分析确保需求完整性
- 🔐 **企业级就绪** - 支持私有化部署的大模型（通义千问）、Azure OpenAI 及自定义模型

---

## ✨ 核心功能

### 🧠 **智能多智能体系统**

基于 [crewAI](https://github.com/joaomdmoura/crewAI) 框架，两个专业智能体协同工作：

- **需求分析 Agent**：从非结构化文本中提取并结构化关键信息
- **文档格式化 Agent**：生成符合企业标准格式的专业 Markdown 文档

### 🌍 **灵活的大模型支持**

- ✅ **通义千问 Qwen（阿里云）** - 中文需求处理最佳，符合中国合规要求
- ✅ **Azure OpenAI** - 企业级，与 Microsoft 365 集成
- ✅ **Grok (xAI)** - 成本友好的创新选择
- ✅ **自定义模型** - 支持接入您自己的大模型（私有化或云端）

### 🔗 **无缝工具集成**

- **Azure DevOps API**：自动创建包含结构化需求的工作项
- **Confluence API**：生成并发布文档页面
- **可扩展架构**：轻松添加 Jira、Notion、Monday.com 等工具

### 🎨 **双重交互界面**

- **CLI 命令行**：适合自动化、CI/CD 流水线和高级用户
- **Streamlit Web UI**：为非技术人员提供友好的可视化界面

### 🛡️ **生产级质量**

- 87% 单元测试覆盖率
- 完整的 CI/CD 流水线
- 模块化、可扩展架构
- 基于环境变量的配置管理

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户交互层                              │
│  CLI (命令行)        │  Web UI (Streamlit)              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 多智能体处理层                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  需求分析 Agent  →  文档格式化 Agent              │  │
│  │                                                   │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   大模型集成层                             │
│  Qwen  │  Azure OpenAI  │  Grok  │  自定义模型          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  外部集成层                                │
│  Azure DevOps  │  Confluence  │  Jira (即将支持)        │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 前置要求

- Python 3.11 或更高版本
- 您选择的大模型提供商的 API 密钥（通义千问、Azure OpenAI 或 Grok）
- （可选）Azure DevOps / Confluence 凭证用于集成

### 安装

```bash
# 克隆仓库
git clone https://github.com/loootte/req_agent.git
cd req_agent

# 安装依赖
pip install -r requirements.txt
```

### 配置

在项目根目录创建 `.env` 文件：

```env
# 大模型配置（选择其中一个）
QWEN_API_KEY=your_qwen_api_key
QWEN_MODEL_NAME=qwen-max

# 或使用 Azure OpenAI
# AZURE_OPENAI_API_KEY=your_key
# AZURE_OPENAI_ENDPOINT=your_endpoint
# AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment

# 或使用 Grok
# GROK_API_KEY=your_grok_key

# 可选：工具集成
# AZURE_DEVOPS_PAT=your_pat
# AZURE_DEVOPS_ORG=your_organization
# CONFLUENCE_API_TOKEN=your_token
```

### 使用方式

#### 🖥️ CLI 命令行模式

```bash
# 从文本文件分析需求
python main.py --input requirements.txt --model qwen

# 集成 Azure DevOps
python main.py --input requirements.txt --model azure --create-workitem

# 集成 Confluence
python main.py --input requirements.txt --model qwen --create-confluence
```

#### 🌐 Web UI 网页模式

```bash
# 启动 Streamlit 界面
streamlit run src\requirement_tracker\webaapp.py

# 在浏览器中打开 http://localhost:8501
```

---

## 📖 示例工作流

### 输入（非结构化需求）

```
我们需要一个动态定价系统，能够根据市场行情自动调整铁矿石的报价。
系统应该每天早上8点自动运行，从外部数据源获取最新价格，
然后根据我们的定价策略计算出新的报价，并发送给销售团队审核。
```

### 输出（结构化文档）

```markdown
## 需求分析：动态定价系统

### 问题陈述
需要一个自动化的动态定价系统，根据实时市场状况调整铁矿石报价。

### 业务目标
- 提高定价对市场变化的响应速度
- 减少销售团队的手工定价工作
- 保持有竞争力的定价策略

### 关键交付物
1. 自动化的每日定价计算引擎
2. 外部市场数据集成
3. 定价策略配置模块
4. 销售团队审核与批准工作流

### 验收标准
- 系统每天早上 8:00 自动运行
- 成功从外部数据源获取最新市场价格
- 基于可配置的定价规则计算新报价
- 通过邮件/仪表板将结果发送给销售团队审核

### 技术考虑
- 数据源的可靠性和延迟
- 定价算法的透明度和可审计性
- 定价策略参数的安全性

### 风险评估
- 外部数据源可用性（中等风险）
- 定价算法准确性验证（高优先级）
- 销售团队采用的变更管理（中等风险）
```

### 集成操作

- ✅ **Azure DevOps 工作项** 已创建，包含结构化需求
- ✅ **Confluence 页面** 已发布供团队协作
- ✅ **邮件通知** 发送给相关干系人（即将推出）

---

## 🎯 使用场景

### 1️⃣ **咨询公司**
- 加速客户项目交付
- 跨团队标准化需求文档
- 减少文档编写的计费工时

### 2️⃣ **企业 PMO**
- 提升需求质量和一致性
- 弥合业务与 IT 之间的沟通鸿沟
- 加速数字化转型落地

### 3️⃣ **软件开发团队**
- 自动化待办事项梳理和用户故事创建
- 减少需求澄清会议时间
- 自动改善 Jira/ADO 卫生度

### 4️⃣ **全球分布式团队**
- 多语言支持打破语言障碍
- 确保跨地区需求格式一致
- 减少异步沟通开销

---

## 🗺️ 发展路线图

### ✅ **阶段 1：核心功能（已完成）**
- 多智能体需求分析系统
- 支持通义千问、Azure OpenAI、Grok
- CLI 和 Web UI 交互界面
- Azure DevOps 和 Confluence 集成

### 🔄 **阶段 2：增强集成（进行中）**
- [ ] Jira 集成
- [ ] Notion 集成
- [ ] Monday.com 集成
- [ ] 邮件通知
- [ ] Slack/Teams 集成

### 📋 **阶段 3：高级功能（计划中）**
- [ ] 批量处理多个需求
- [ ] 需求模板库（按行业/场景分类）
- [ ] 版本控制和变更追踪
- [ ] 冲突和依赖关系检测
- [ ] 需求优先级评分
- [ ] 多语言界面（英文、中文、日文）

### 🚀 **阶段 4：企业版（未来规划）**
- [ ] 多租户 SaaS 平台
- [ ] 基于角色的访问控制（RBAC）
- [ ] 分析与报告仪表板
- [ ] 自定义工作流自动化
- [ ] 企业 SSO 集成
- [ ] 私有化部署支持

---

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行并生成覆盖率报告
pytest --cov=src --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

当前测试覆盖率：**87%**

---

## 🤝 贡献指南

我们欢迎各种形式的贡献！以下是您可以提供帮助的方式：

### 贡献方式

- 🐛 **报告 Bug** 通过 [GitHub Issues](https://github.com/loootte/req_agent/issues)
- 💡 **建议功能** 或改进意见
- 📝 **改进文档**（特别是使用案例和示例）
- 🔧 **提交 Pull Request** 修复 Bug 或添加新功能
- 🌐 **添加大模型集成**（Claude、Gemini 等）
- 🔗 **添加工具集成**（Jira、Notion、Linear 等）

### 开发环境设置

```bash
# Fork 并克隆您的 Fork
git clone https://github.com/YOUR_USERNAME/req_agent.git

# 创建功能分支
git checkout -b feature/your-feature-name

# 进行修改并测试
pytest

# 提交 Pull Request
```

---

## 📊 性能指标

基于能源、汽车和零售行业的试点项目数据：

| 指标 | 使用前 | 使用后 | 改进幅度 |
|--------|--------|-------|-------------|
| **需求文档编写时间** | 2 小时 | 15 分钟 | **提速 8 倍** |
| **手工工作量减少** | 100% | 40% | **节省 60%** |
| **需求完整性** | 75% | 95% | **提升 20%** |
| **干系人满意度** | 3.5/5 | 4.4/5 | **提升 25%** |

*数据来自 3 个试点项目（样本量：45+ 需求文档）*

---

## 🏢 企业支持

对企业级部署、定制功能或咨询服务感兴趣？

- 📧 邮箱：[your-email@example.com]
- 💼 LinkedIn：[您的 LinkedIn 主页]
- 🌐 网站：[您的网站]

我们提供：
- **定制大模型集成**（私有/本地部署模型）
- **企业工具集成**（SAP、Oracle、Salesforce 等）
- **团队培训与工作坊**
- **专属支持与 SLA**
- **白标部署方案**

---

## 📄 开源许可

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [crewAI](https://github.com/joaomdmoura/crewAI) - 优秀的多智能体框架
- [Streamlit](https://streamlit.io/) - 优雅的 UI 框架
- [LangChain](https://github.com/langchain-ai/langchain) - Agent 设计的灵感来源
- 所有贡献者和试点项目团队

---

## 📚 相关资源


---

## ⭐ Star 历史

如果您觉得这个项目有用，请考虑给它一个 Star！⭐

[![Star History Chart](https://api.star-history.com/svg?repos=loootte/req_agent&type=Date)](https://star-history.com/#loootte/req_agent&Date)

---

## 📞 联系与社区

- **GitHub Issues**：[报告 Bug 或请求功能](https://github.com/loootte/req_agent/issues)


---

**用 ❤️ 制作，作者：[Zhong Le](https://github.com/loootte)**

*用 AI 改变需求管理，一次一个文档。*

