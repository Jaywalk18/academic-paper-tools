[English](README.md) | [中文](README_CN.md)

# 学术论文工具

AI 驱动的学术论文工作流工具。支持 Cursor、命令行及其他 AI 编辑器。

本仓库包含两个工具：

1. **paper-review** - 基于多智能体系统的 AI 论文评审模拟
2. **ref-check** - BibTeX 参考文献验证工具

## 功能特性

### 论文评审工具

- **多智能体流水线**：使用 4 个 AI 智能体模拟学术评审流程
- **视觉分析**：分析 PDF 页面，提取技术贡献
- **审稿意见综合**：评估审稿人意见，识别可信度
- **Rebuttal 分析**：评估作者对审稿意见的回复
- **决策预测**：预测录用结果（Oral/Spotlight/Poster/Reject）

### 参考文献检查工具

- **多源验证**：通过 Crossref、OpenAlex 和 Semantic Scholar 交叉验证
- **准确度评分**：计算标题相似度、作者匹配度、年份匹配度
- **状态分类**：将每条参考文献分类为 verified/uncertain/suspicious
- **详细报告**：提供差异详情和修正建议

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/Jaywalk18/academic-paper-tools.git
cd academic-paper-tools
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API 密钥

**论文评审工具**（必需）：
```bash
# Windows PowerShell
$env:PAPER_REVIEW_API_KEY = "your-openai-api-key"

# macOS/Linux
export PAPER_REVIEW_API_KEY="your-openai-api-key"
```

**参考文献检查工具**（可选，增强搜索）：
```bash
# Windows PowerShell
$env:SEMANTIC_SCHOLAR_API_KEY = "your-s2-api-key"

# macOS/Linux
export SEMANTIC_SCHOLAR_API_KEY="your-s2-api-key"
```

## 使用方法

### 命令行

### 论文评审

```bash
# 基础评审（仅 PDF）
python paper-review/scripts/review_paper.py --pdf paper.pdf

# 带审稿意见
python paper-review/scripts/review_paper.py --pdf paper.pdf --reviews reviews.json

# 保存输出
python paper-review/scripts/review_paper.py --pdf paper.pdf -o result.json
```

### 参考文献检查

```bash
# 检查 .bib 文件
python ref-check/scripts/check_references.py --bib references.bib

# 检查内联 BibTeX
python ref-check/scripts/check_references.py --content "@article{key, title={...}}"

# 保存报告
python ref-check/scripts/check_references.py --bib refs.bib -o report.json
```

## 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `PAPER_REVIEW_API_KEY` | 是（论文评审） | OpenAI 兼容的 API 密钥 |
| `PAPER_REVIEW_API_BASE` | 否 | 自定义 API 基础 URL（默认：OpenAI） |
| `PAPER_REVIEW_MODEL` | 否 | 模型名称（默认：gpt-4o） |
| `SEMANTIC_SCHOLAR_API_KEY` | 否 | Semantic Scholar API 密钥 |

## 输出示例

### 论文评审输出

```json
{
  "title": "Deep Learning for NLP",
  "prediction": "Poster",
  "final_score": 7.5,
  "decision": {
    "final_decision": "Poster",
    "decision_archetype": "Uncontested_Success",
    "key_factor": "Strong empirical results",
    "confidence": "High"
  }
}
```

### 参考文献检查输出

```json
{
  "summary": {
    "total": 10,
    "counts": {
      "verified": 7,
      "uncertain": 2,
      "suspicious": 1
    }
  },
  "items": [
    {
      "key": "smith2023",
      "status": "verified",
      "score": 90,
      "best_match": {
        "title": "...",
        "sim_title": 0.95
      }
    }
  ]
}
```

## 系统要求

- Python 3.8+
- 网络连接（用于 API 调用）

### 论文评审额外要求

- Poppler（用于 PDF 处理）
  - **Windows**：从 [poppler-for-windows](https://github.com/osber/poppler-for-windows/releases) 下载
  - **macOS**：`brew install poppler`
  - **Linux**：`apt-get install poppler-utils`

## AI 编辑器集成（可选）

这些工具可作为 Agent Skills 在 Cursor 等 AI 编辑器中使用：

**Windows:**
```powershell
Copy-Item -Recurse .\paper-review\ "$env:USERPROFILE\.cursor\skills\paper-review"
Copy-Item -Recurse .\ref-check\ "$env:USERPROFILE\.cursor\skills\ref-check"
```

**macOS/Linux:**
```bash
cp -r ./paper-review ~/.cursor/skills/
cp -r ./ref-check ~/.cursor/skills/
```

然后可以使用自然语言命令：
- "评审这篇论文：paper.pdf"
- "检查 paper.bib 的参考文献"

## 许可证

MIT License

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 致谢

**基于以下项目：**
- [PaperDecision](https://github.com/PaperDecision/PaperDecision) - 多智能体论文评审预测系统
- [RefCheck.ai](https://github.com/HuaHenry/RefCheck_ai) - BibTeX 参考文献验证工具

**数据来源：**
- [Crossref](https://www.crossref.org/) - 学术元数据 API
- [OpenAlex](https://openalex.org/) - 开放学术作品目录
- [Semantic Scholar](https://www.semanticscholar.org/) - AI 驱动的研究工具
