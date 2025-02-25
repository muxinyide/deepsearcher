```markdown
# AI 驱动的市场调研报告生成器

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 项目简介

本项目是一个基于人工智能（AI）的市场调研报告自动生成工具。用户只需输入感兴趣的研究主题，程序即可自动进行需求分析、多维度信息搜索、数据清洗与验证、知识图谱构建，并最终生成一份结构完整、内容详实的市场调研报告（PDF 格式）。本项目旨在通过自动化流程，提高市场调研的效率和质量。

## 功能特点

*   **智能需求解析：** 利用大型语言模型（LLM）将用户输入的主题分解为多个具体的研究维度。
*   **动态信息搜索：** 针对每个研究维度，自动生成关键词并进行网络搜索，获取相关信息。
*   **数据清洗与验证：** 从网页中提取关键信息，进行数据清洗、可信度评估、时效性检查和矛盾检测。
*   **知识图谱构建：** 将提取的信息整合成结构化的知识图谱，便于理解和分析。
*   **迭代式报告生成：** 基于知识图谱和 LLM，自动生成报告的标题、引言、章节、结论和参考文献。
*   **报告质量检查：** 对生成的报告进行整体质量评估，并提供改进建议。
*   **PDF 报告输出：** 将最终报告以 PDF 格式输出，方便分享和阅读。
*   **可扩展性：** 模块化设计，易于添加新的搜索源、数据处理方法和报告模板。

## 技术栈

*   Python 3.7+
*   `requests`：用于网络请求
*   `beautifulsoup4`：用于 HTML 解析
*   `reportlab`：用于 PDF 生成
*   大型语言模型（LLM）：用于文本生成、分析和验证（例如 OpenAI 的 GPT 系列模型，本项目中作为抽象接口，具体实现需用户自行配置）
*   DuckDuckGo Search API：用于网络搜索（可替换为其他搜索引擎）

## 安装与配置

1.  **克隆项目：**

    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2.  **安装依赖：**

    ```bash
    pip install requests beautifulsoup4 pandas nltk spacy python-dotenv reportlab duckduckgo-search zhipuai
    python -m spacy download zh_core_web_sm  # 如果使用spaCy进行中文处理
    ```

3.  **配置 API 密钥（可选）：**

    *   如果你使用需要 API 密钥的服务（如 LLM 或某些搜索引擎），请在 `config.py` 文件中配置相应的密钥。

## 使用方法

1.  **运行主程序：**

    ```bash
    python main.py
    ```

2.  **输入研究主题：**

    *   根据提示输入你感兴趣的研究主题（例如：“人工智能在医疗领域的应用”）。

3.  **等待报告生成：**

    *   程序将自动执行各个阶段，并在完成后生成 PDF 报告（默认保存为 `research_report.pdf`）。

## 文件结构

```
├── main.py             # 主程序入口
├── config.py           # 配置文件 (可选，根据 config_template.py 创建)
├── config_template.py  # 配置文件模板
├── requirements.txt    # 项目依赖
├── stages/             # 各阶段模块
│   ├── __init__.py
│   ├── stage1_demand_analysis.py    # 需求解析
│   ├── stage2_dynamic_search.py     # 动态搜索分析
│   ├── stage3_knowledge_graph.py   # 知识图谱构建
│   ├── stage4_iterative_reporting.py # 迭代式报告生成
│   └── utils/                      # 通用工具函数
│       ├── __init__.py
│       ├── llm_utils.py            # LLM 相关工具
│       ├── search_utils.py         # 搜索相关工具
│       ├── data_processing.py      # 数据处理工具
│       └── report_utils.py         # 报告生成工具
├── tests/              # 测试用例 (可选)
│   ├── ...
├── README.md           # 项目说明文档
└── LICENSE             # 开源许可证
```

## 贡献指南

欢迎对本项目提出改进建议或贡献代码。请遵循以下步骤：

1.  Fork 本项目。
2.  创建你的特性分支 (`git checkout -b feature/AmazingFeature`)。
3.  提交你的改动 (`git commit -m 'Add some AmazingFeature'`)。
4.  推送到你的分支 (`git push origin feature/AmazingFeature`)。
5.  发起一个 Pull Request。

## 许可证

本项目采用 MIT 许可证。详细信息请参见 [LICENSE](LICENSE) 文件。

## 免责声明

*   本项目生成的报告仅供参考，不构成任何投资或决策建议。
*   用户需自行承担使用本项目产生的任何风险和责任。
*   本项目依赖于第三方服务（如搜索引擎和 LLM），其可用性和准确性不受本项目控制。
*   请确保你的使用行为符合相关法律法规和服务条款。



