
# 🤖 RequirementTracker
[中文](README_zh.md) | English

**AI-Powered Requirements Analysis & Management System**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen.svg)](https://github.com/loootte/req_agent)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/loootte/req_agent/pulls)

---

## 🎯 Why RequirementTracker?

### The Problem

In enterprise digital transformation and agile delivery projects, requirements management is often the biggest bottleneck:

- 📧 **Requirements are scattered** across emails, meeting notes, chat messages, and documents
- ⏰ **Writing structured requirements takes hours** and quality varies by person
- 🔄 **Manual synchronization** between requirements documents and project management tools (Jira, Azure DevOps) is error-prone
- 🌐 **Language barriers** slow down global team collaboration
- 🔒 **Compliance concerns** prevent many enterprises from adopting public cloud AI tools

### The Solution

**RequirementTracker** is an AI-powered multi-agent system that automatically transforms informal requirement descriptions into professional, structured documents and seamlessly integrates with enterprise collaboration platforms.

### The Impact

- ⚡ **8x faster** - Reduce requirements documentation time from hours to minutes
- 📉 **60% less manual work** - Automate requirement extraction, formatting, and tool integration
- ✅ **40% fewer missed requirements** - AI-powered analysis ensures completeness
- 🔐 **Enterprise-ready** - Support for on-premises LLMs (Qwen), Azure OpenAI, and custom models

---

## ✨ Key Features

### 🧠 **Intelligent Multi-Agent System**

Powered by [crewAI](https://github.com/joaomdmoura/crewAI), two specialized agents work together:

- **Requirements Analyst Agent**: Extracts and structures key information from unstructured text
- **Document Formatter Agent**: Generates professional Markdown documentation with enterprise-standard formats

### 🌍 **Flexible LLM Support**

- ✅ **Qwen (Alibaba Cloud)** - Best for Chinese requirements, China compliance-ready
- ✅ **Azure OpenAI** - Enterprise-grade, Microsoft 365 integrated
- ✅ **Grok (xAI)** - Cost-effective, innovative alternative
- ✅ **Custom Models** - Bring your own LLM (on-premises or cloud)

### 🔗 **Seamless Tool Integration**

- **Azure DevOps API**: Automatically create Work Items with structured requirements
- **Confluence API**: Generate and publish documentation pages
- **Extensible Architecture**: Easy to add Jira, Notion, Monday.com, etc.

### 🎨 **Dual Interface**

- **CLI**: Perfect for automation, CI/CD pipelines, and power users
- **Streamlit Web UI**: User-friendly interface for non-technical stakeholders

### 🛡️ **Production-Ready Quality**

- 87% unit test coverage
- Comprehensive CI/CD pipeline
- Modular, extensible architecture
- Environment-based configuration management

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  User Interface Layer                    │
│  CLI (Command Line)  │  Web UI (Streamlit)              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Multi-Agent Processing Layer                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Requirements Analyst  →  Document Formatter     │  │
│  │         Agent                    Agent            │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   LLM Integration Layer                  │
│  Qwen  │  Azure OpenAI  │  Grok  │  Custom Models       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              External Integrations Layer                 │
│  Azure DevOps  │  Confluence  │  Jira (Coming Soon)    │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- API keys for your chosen LLM provider (Qwen, Azure OpenAI, or Grok)
- (Optional) Azure DevOps / Confluence credentials for integration

### Installation

```bash
# Clone the repository
git clone https://github.com/loootte/req_agent.git
cd req_agent

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
# LLM Configuration (choose one)
QWEN_API_KEY=your_qwen_api_key
QWEN_MODEL_NAME=qwen-max

# Or use Azure OpenAI
# AZURE_OPENAI_API_KEY=your_key
# AZURE_OPENAI_ENDPOINT=your_endpoint
# AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment

# Or use Grok
# GROK_API_KEY=your_grok_key

# Optional: Tool Integration
# AZURE_DEVOPS_PAT=your_pat
# AZURE_DEVOPS_ORG=your_organization
# CONFLUENCE_API_TOKEN=your_token
```

### Usage

#### 🖥️ CLI Mode

```bash
# Analyze requirements from a text file
python main.py --input requirements.txt --model qwen

# With Azure DevOps integration
python main.py --input requirements.txt --model azure --create-workitem

# With Confluence integration
python main.py --input requirements.txt --model qwen --create-confluence
```

#### 🌐 Web UI Mode

```bash
# Launch Streamlit interface
python -m streamlit run src/requirement_tracker/webapp.py

# Open browser at http://localhost:8501
```

---

## 📖 Example Workflow

### Input (Unstructured Requirement)

```
我们需要一个动态定价系统，能够根据市场行情自动调整铁矿石的报价。
系统应该每天早上8点自动运行，从外部数据源获取最新价格，
然后根据我们的定价策略计算出新的报价，并发送给销售团队审核。
```

### Output (Structured Document)

```markdown
## Requirements Analysis: Dynamic Pricing System

### Problem Statement
Need an automated dynamic pricing system for iron ore that adjusts 
quotations based on real-time market conditions.

### Business Goals
- Improve pricing responsiveness to market changes
- Reduce manual pricing work for sales team
- Maintain competitive pricing strategy

### Key Deliverables
1. Automated daily pricing calculation engine
2. External market data integration
3. Pricing strategy configuration module
4. Sales team review and approval workflow

### Acceptance Criteria
- System runs daily at 8:00 AM automatically
- Successfully retrieves latest market prices from external sources
- Calculates new quotations based on configurable pricing rules
- Sends results to sales team for review via email/dashboard

### Technical Considerations
- Data source reliability and latency
- Pricing algorithm transparency and auditability
- Security for pricing strategy parameters

### Risk Assessment
- External data source availability (Medium risk)
- Pricing algorithm accuracy validation (High priority)
- Change management for sales team adoption (Medium risk)
```

### Integrated Actions

- ✅ **Azure DevOps Work Item** created with structured requirements
- ✅ **Confluence Page** published for team collaboration
- ✅ **Email notification** sent to stakeholders (coming soon)

---

## 🎯 Use Cases

### 1️⃣ **Consulting Companies**
- Accelerate client project delivery
- Standardize requirements documentation across teams
- Reduce billable hours spent on documentation

### 2️⃣ **Enterprise PMOs**
- Improve requirements quality and consistency
- Bridge communication gaps between business and IT
- Enable faster digital transformation initiatives

### 3️⃣ **Software Development Teams**
- Automate backlog grooming and user story creation
- Reduce time spent in requirements clarification meetings
- Improve Jira/ADO hygiene automatically

### 4️⃣ **Global Distributed Teams**
- Break language barriers with multi-language support
- Ensure consistent requirements format across regions
- Reduce asynchronous communication overhead

---

## 🗺️ Roadmap

### ✅ **Phase 1: Core Functionality (Completed)**
- Multi-agent requirements analysis system
- Support for Qwen, Azure OpenAI, Grok
- CLI and Web UI interfaces
- Azure DevOps and Confluence integration

### 🔄 **Phase 2: Enhanced Integration (In Progress)**
- [ ] Jira integration
- [ ] Notion integration
- [ ] Monday.com integration
- [ ] Email notifications
- [ ] Slack/Teams integration

### 📋 **Phase 3: Advanced Features (Planned)**
- [ ] Batch processing for multiple requirements
- [ ] Requirements template library (by industry/scenario)
- [ ] Version control and change tracking
- [ ] Conflict and dependency detection
- [ ] Requirements prioritization scoring
- [ ] Multi-language UI (English, Chinese, Japanese)

### 🚀 **Phase 4: Enterprise Edition (Future)**
- [ ] Multi-tenant SaaS platform
- [ ] Role-based access control (RBAC)
- [ ] Analytics and reporting dashboard
- [ ] Custom workflow automation
- [ ] Enterprise SSO integration
- [ ] On-premises deployment support

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

Current test coverage: **87%**

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

- 🐛 **Report bugs** via [GitHub Issues](https://github.com/loootte/req_agent/issues)
- 💡 **Suggest features** or improvements
- 📝 **Improve documentation** (especially use cases and examples)
- 🔧 **Submit pull requests** for bug fixes or new features
- 🌐 **Add LLM integrations** (Claude, Gemini, etc.)
- 🔗 **Add tool integrations** (Jira, Notion, Linear, etc.)

### Development Setup

```bash
# Fork and clone your fork
git clone https://github.com/loootte/req_agent

# Create a feature branch
git checkout -b feature/your-feature-name

# Make changes and test
pytest

# Submit pull request
```

---
## 🏢 Enterprise Support

Interested in enterprise deployment, custom features, or consulting services?

- 📧 Email: tuya000000@gmail.com
- 📞 Phone: +86 180 5718 8110


We offer:
- **Custom LLM integration** (private/on-premises models)
- **Enterprise tool integration** (SAP, Oracle, Salesforce, etc.)
- **Training and workshops** for your teams
- **Dedicated support** and SLA
- **White-label deployment** options

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [crewAI](https://github.com/joaomdmoura/crewAI) - Excellent multi-agent framework
- [Streamlit](https://streamlit.io/) - Beautiful UI framework
- [LangChain](https://github.com/langchain-ai/langchain) - Inspiration for agent design
- All contributors and pilot project teams

---

## 📚 Related Resources


---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=loootte/req_agent&type=Date)](https://star-history.com/#loootte/req_agent&Date)

---

## 📞 Contact & Community

- **GitHub Issues**: [Report bugs or request features](https://github.com/loootte/req_agent/issues)


---

**Made with ❤️ by [Zhong Le](https://github.com/loootte)**

*Transforming requirements management with AI, one document at a time.*
