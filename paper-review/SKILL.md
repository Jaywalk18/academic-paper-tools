---
name: paper-review
description: Review academic papers in LaTeX projects. Analyzes TeX source files, figures, and bibliography to provide comprehensive peer review feedback. Use when the user asks to review a paper, evaluate a submission, or wants feedback on their LaTeX manuscript.
version: 1.0.0
author: Academic Paper Tools
license: MIT
tags: [Academic, Paper Review, LaTeX, Peer Review, NeurIPS, ICML, ICLR, CVPR]
---

# Paper Review - AI-Powered Academic Paper Evaluation

This skill provides comprehensive peer review for LaTeX academic papers by directly analyzing source files.

## Activation Triggers

Use this skill when the user:
- Asks to "review this paper" or "review my paper"
- Wants feedback on a LaTeX manuscript
- Asks about paper quality, novelty, or acceptance chances
- Mentions ICLR, NeurIPS, ICML, CVPR, or other venue submissions

## Review Process

### Step 1: Discover Project Structure

First, identify the LaTeX project structure:

```
Typical LaTeX project:
├── main.tex              # Main document (look for \documentclass)
├── sections/             # Or mysec/, chapters/, etc.
│   ├── 1_intro.tex
│   ├── 2_method.tex
│   └── ...
├── figures/              # Or figs/, images/, asset/
│   ├── figure1.pdf
│   └── ...
├── main.bib              # Or references.bib, ref.bib
└── *.sty                 # Style files (can ignore)
```

**Actions:**
1. Use `LS` to explore the project root
2. Find the main `.tex` file (contains `\documentclass`)
3. Locate figure directories and `.bib` files

### Step 2: Read Core Content

Read files in this priority order:

1. **Main tex file** - Get document structure, abstract, title
2. **Introduction** - Understand motivation and contributions
3. **Method/Approach** - Core technical content
4. **Experiments** - Results and evaluation
5. **Figures** - Visual quality and clarity (use `Read` on image files)
6. **Bibliography** - Reference quality and completeness

**Tips:**
- For `\input{sections/intro}`, read `sections/intro.tex`
- For `\includegraphics{figures/fig1}`, read the image file
- Pay attention to `\cite{}` commands for reference analysis

### Step 3: Evaluate Paper Quality

Assess the following dimensions:

#### 3.1 Technical Contribution
- **Novelty**: Groundbreaking / Significant / Incremental
- **Soundness**: Are the methods technically correct?
- **Completeness**: Is the approach fully described?

#### 3.2 Experimental Evaluation
- **Baselines**: Are comparisons fair and comprehensive?
- **Datasets**: Appropriate and sufficient?
- **Metrics**: Standard and meaningful?
- **Ablations**: Do they validate design choices?

#### 3.3 Presentation Quality
- **Clarity**: Is the writing clear and well-organized?
- **Figures**: High quality, informative, readable?
- **Math**: Notation consistent? Equations well-explained?

#### 3.4 Related Work
- **Coverage**: Are key papers cited?
- **Positioning**: How does this work differ from prior art?

### Step 4: Generate Review Report

Provide a structured review in this format:

```markdown
## Paper Review: [Title]

### Summary
[2-3 sentence summary of the paper's main contribution]

### Strengths
1. [Major strength with specific reference to content]
2. [Another strength]
3. ...

### Weaknesses
1. [Major weakness with specific location, e.g., "Section 3.2, line discussing X"]
2. [Another weakness]
3. ...

### Questions for Authors
1. [Clarifying question]
2. ...

### Detailed Comments

#### Introduction (sections/1_intro.tex)
- [Specific feedback with line references if helpful]

#### Method (sections/3_method.tex)
- [Specific feedback]

#### Experiments (sections/4_experiments.tex)
- [Specific feedback]

#### Figures
- Figure 1: [Assessment]
- Figure 2: [Assessment]

### Overall Assessment

| Aspect | Rating | Comment |
|--------|--------|---------|
| Novelty | ⭐⭐⭐☆☆ | [Brief comment] |
| Soundness | ⭐⭐⭐⭐☆ | [Brief comment] |
| Presentation | ⭐⭐⭐☆☆ | [Brief comment] |
| Significance | ⭐⭐⭐☆☆ | [Brief comment] |

**Recommendation**: Accept / Weak Accept / Borderline / Weak Reject / Reject

**Confidence**: High / Medium / Low
```

## Special Modes

### Quick Review Mode
If user asks for a "quick review" or "brief feedback":
- Read only main.tex, intro, and method sections
- Provide 3 strengths, 3 weaknesses, overall recommendation

### Focus Review Mode
If user asks about specific aspects (e.g., "review my experiments"):
- Focus on the requested sections
- Provide deeper analysis of that specific area

### Rebuttal Helper Mode
If user provides reviewer comments:
- Analyze each reviewer concern
- Suggest specific responses with references to paper content
- Identify which concerns need new experiments vs. clarification

## Important Notes

1. **Be Constructive**: Frame criticism as suggestions for improvement
2. **Be Specific**: Reference exact locations (file, section, paragraph)
3. **Be Fair**: Acknowledge both strengths and weaknesses
4. **Be Actionable**: Provide concrete suggestions, not vague complaints
5. **Consider Venue**: Adjust standards based on target venue (top-tier vs. workshop)

## Example Interaction

**User**: Review my paper in the release/ folder

**Agent Actions**:
1. `LS release/` → Find main.tex, mysec/, figures/, main.bib
2. `Read release/main.tex` → Get structure, abstract
3. `Read release/mysec/1_intro.tex` → Analyze introduction
4. `Read release/mysec/3_method.tex` → Analyze methodology
5. `Read release/mysec/4_experiments.tex` → Analyze experiments
6. `Read release/figures/figure1.pdf` → Check figure quality
7. Synthesize findings into structured review report
