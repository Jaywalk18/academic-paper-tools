# Paper Review - Reference Prompts

This document provides reference prompts and evaluation criteria for the paper review skill.

## Evaluation Dimensions

### 1. Novelty Assessment

When evaluating novelty, consider:

| Level | Description | Indicators |
|-------|-------------|------------|
| **Groundbreaking** | Introduces fundamentally new concepts | New paradigm, significant impact potential |
| **Significant** | Novel combination or substantial improvement | Clear advancement over prior work |
| **Incremental** | Minor improvements or engineering contributions | Similar to existing work with tweaks |

**Key Questions:**
- What is genuinely new in this paper?
- How does it differ from the most similar prior work?
- Would the community find this contribution meaningful?

### 2. Technical Soundness

Check for:
- Mathematical correctness of derivations
- Validity of assumptions
- Proper use of evaluation metrics
- Statistical significance of results
- Reproducibility (are details sufficient?)

**Red Flags:**
- Missing proofs for theoretical claims
- Unfair baseline comparisons
- Cherry-picked results
- Missing error bars or confidence intervals

### 3. Experimental Quality

| Aspect | Good | Problematic |
|--------|------|-------------|
| Baselines | Recent, strong, diverse | Outdated, weak, limited |
| Datasets | Standard benchmarks + real-world | Only toy datasets |
| Metrics | Multiple, standard | Single, custom |
| Ablations | Comprehensive | Missing or incomplete |
| Analysis | Insightful failure cases | Only positive results |

### 4. Writing Quality

Assess:
- **Clarity**: Can a PhD student in the field follow it?
- **Organization**: Logical flow from intro to conclusion?
- **Figures**: Self-explanatory with proper captions?
- **Related Work**: Fair and comprehensive?

## Review Templates

### Strength Template
```
[S1] Clear problem motivation: The paper identifies a genuine gap in...
[S2] Strong empirical results: Achieves X% improvement on benchmark Y...
[S3] Good ablation study: Table N clearly shows the contribution of each component...
```

### Weakness Template
```
[W1] Limited novelty: The proposed method is a straightforward combination of A and B...
[W2] Missing comparison: The paper does not compare with recent work Z (VENUE 2024)...
[W3] Unclear explanation: Section 3.2 does not explain why the specific choice of...
```

### Question Template
```
[Q1] In Eq. 5, how is the hyperparameter λ chosen? Is it sensitive to this choice?
[Q2] Have the authors tried applying this method to domain X? Why or why not?
[Q3] The assumption in Section 3.1 seems restrictive. Can the authors clarify...
```

## Venue-Specific Standards

### Top-tier Venues (NeurIPS, ICML, ICLR, CVPR)
- Expect significant novelty
- Strong baselines including SOTA
- Multiple datasets
- Thorough ablations
- Clear writing

### Mid-tier Venues (Workshops, Regional Conferences)
- Incremental contributions acceptable
- Fewer baselines okay
- Preliminary results acceptable
- Work-in-progress allowed

## Common Issues by Section

### Abstract
- Too vague ("we propose a novel method")
- Missing quantitative results
- Overclaiming ("state-of-the-art")

### Introduction
- Motivation unclear
- Contributions not specific
- Missing key citations

### Method
- Notation inconsistent
- Key details in appendix
- Assumptions not stated

### Experiments
- Baselines outdated
- Missing ablations
- No failure analysis
- Results not reproducible

### Related Work
- Missing recent papers
- Unfair characterization
- Poor positioning

## Scoring Guidelines

Use this mental model for overall assessment:

| Score | Meaning | Typical Characteristics |
|-------|---------|------------------------|
| **Strong Accept** | Top 5% | Groundbreaking, flawless execution |
| **Accept** | Top 20% | Significant contribution, minor issues |
| **Weak Accept** | Top 35% | Solid work, some concerns |
| **Borderline** | Top 50% | Decent but not compelling |
| **Weak Reject** | Bottom 50% | Notable issues, limited contribution |
| **Reject** | Bottom 30% | Major flaws or insufficient novelty |
| **Strong Reject** | Bottom 10% | Fundamental problems |

## Ethics Considerations

Flag if you notice:
- Potential dual-use concerns
- Missing ethics statement for human data
- Biased datasets or evaluation
- Environmental impact not discussed (large models)
- Reproducibility barriers (proprietary data/compute)
