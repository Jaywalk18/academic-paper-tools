[English](README.md) | [中文](README_CN.md)

# 学术论文工具 - Cursor Agent Skills

为 Cursor AI 设计的 Agent 原生学术论文工具，充分利用 Agent 自身能力。

## 设计理念

这些 Skills 采用 **Agent 原生** 设计：

- **无需外部 LLM 调用** - Cursor Agent 直接分析内容
- **直接文件访问** - 原生读取 TeX 源码、图片和参考文献
- **最小依赖** - 仅在必要时调用外部 API（如学术数据库）
- **LaTeX 优先** - 针对 TeX 项目优化，读取源文件以获得更好的分析效果

## 可用 Skills

### 1. 论文审稿 (`paper-review/`)

直接分析 LaTeX 源文件的 AI 论文审稿工具。

**功能特性：**
- 读取 `.tex` 文件理解论文结构和内容
- 分析图片的视觉质量
- 检查参考文献完整性
- 提供带有具体文件/行号引用的结构化审稿意见

**使用方式：**
```
"审稿一下 release/ 文件夹里的论文"
"给我的实验部分提点反馈"
"这篇论文有什么缺点？"
```

### 2. 引用检查 (`ref-check/`)

通过学术数据库（Crossref、OpenAlex）验证 BibTeX 引用。

**功能特性：**
- 直接解析 `.bib` 文件
- 查询免费学术 API（无需 API Key）
- 检测标题错误、年份错误、虚假引用
- 提供修正建议

**使用方式：**
```
"检查 main.bib 里的引用"
"验证一下我的参考文献"
"有没有可疑的引用？"
```

## 安装

### 方式一：复制到 Cursor Skills 目录

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

### 方式二：直接在项目中使用

将 skill 文件夹放入项目的 `.cursor/skills/` 目录。

## 为什么用 Agent 原生设计？

传统方式通过脚本调用外部 LLM API：

```
❌ 旧方式: 用户 → Cursor Agent → Python 脚本 → OpenAI API → 响应
```

这完全是多此一举 - Cursor Agent 本身就是强大的 LLM！

```
✅ 新方式: 用户 → Cursor Agent（直接分析文件）→ 响应
```

**优势：**
- **更快** - 无额外 API 往返
- **更省钱** - 无额外 API 费用
- **更好的上下文** - Agent 能看到完整项目结构
- **更精确** - 可以引用具体文件位置

## 为什么读 TeX 源码而不是 PDF？

对于 LaTeX 项目，读取源文件优于 PDF：

| 对比维度 | PDF | TeX 源码 |
|---------|-----|----------|
| 文本质量 | 可能丢失格式 | 完美 |
| 数学公式 | 经常乱码 | 原始 LaTeX |
| 结构信息 | 需要推断 | 明确的章节划分 |
| 图片 | 压缩后 | 原始高清 |
| 可定位性 | "第5页第2段" | "method.tex 第42行" |

## 项目结构

```
cursor-skills/
├── paper-review/
│   ├── SKILL.md          # 主 Skill 定义
│   └── prompts.md        # 参考 Prompts（可选）
├── ref-check/
│   ├── SKILL.md          # 主 Skill 定义
│   └── reference.md      # API 文档（可选）
├── README.md
└── README_CN.md
```

## 系统要求

- Cursor IDE（Agent 模式）
- paper-review 无额外依赖
- ref-check 需要网络连接（API 查询）

## 许可证

MIT License

## 致谢

**灵感来源：**
- [PaperDecision](https://github.com/PaperDecision/PaperDecision) - 多 Agent 论文审稿概念
- [RefCheck.ai](https://github.com/HuaHenry/RefCheck_ai) - 引用验证方法论

**数据来源：**
- [Crossref](https://www.crossref.org/) - 免费学术元数据 API
- [OpenAlex](https://openalex.org/) - 开放学术作品目录
