#!/usr/bin/env python3
"""
Paper Review Script - AI-Powered Academic Paper Evaluation

This script uses a multi-agent system to simulate academic paper review
and predict acceptance decisions.

Usage:
    python review_paper.py --pdf path/to/paper.pdf
    python review_paper.py --pdf paper.pdf --reviews reviews.json
    python review_paper.py --pdf paper.pdf --output result.json

Environment Variables:
    PAPER_REVIEW_API_KEY  - OpenAI-compatible API key (required)
    PAPER_REVIEW_API_BASE - API base URL (optional, defaults to OpenAI)
    PAPER_REVIEW_MODEL    - Model name (optional, defaults to gpt-4o)
"""

import argparse
import base64
import io
import json
import os
import sys
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)

try:
    from pdf2image import convert_from_path
    from PIL import Image
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("Warning: pdf2image/Pillow not installed. PDF support disabled.")
    print("Install with: pip install pdf2image Pillow")


# =============================================================================
# CONFIGURATION
# =============================================================================

API_KEY = os.environ.get("PAPER_REVIEW_API_KEY", "")
API_BASE = os.environ.get("PAPER_REVIEW_API_BASE", "https://api.openai.com/v1")
MODEL_NAME = os.environ.get("PAPER_REVIEW_MODEL", "gpt-4o")

if not API_KEY:
    print("Error: PAPER_REVIEW_API_KEY environment variable not set.")
    print("Please set your OpenAI-compatible API key:")
    print("  export PAPER_REVIEW_API_KEY='your-api-key'")
    sys.exit(1)

client = OpenAI(api_key=API_KEY, base_url=API_BASE)


# =============================================================================
# PROMPTS
# =============================================================================

PROMPT_CONTENT_EVALUATOR = """
你现在是一位拥有 18 年顶会审稿经验的 Senior Area Chair。

请分析这篇论文的 PDF 页面图像，执行以下评估：

1. 提取 3 个最核心的技术贡献点
2. 评估新颖性等级：Groundbreaking / Significant / Incremental
3. 评估获奖潜力：High / Medium / Low
4. 评估视觉质量：High / Medium / Low

输出严格 JSON 格式：
{
  "core_claims": ["claim1", "claim2", "claim3"],
  "novelty_level": "Groundbreaking|Significant|Incremental",
  "award_potential": "High|Medium|Low",
  "visual_quality": "High|Medium|Low",
  "reasoning": "详细推理过程"
}
"""

PROMPT_REVIEW_SYNTHESIZER = """
你现在是资深 Area Chair，分析以下审稿意见。

评分含义：
- 0-2: strong reject
- 4: marginally below threshold
- 6: marginally above threshold  
- 8: accept (poster)
- 10: strong accept (oral/spotlight)

请分析：
1. 每位审稿人的专业度（Expert/Competent/Shallow）
2. 是否存在致命缺陷指控
3. 共识类型
4. 风险等级

输出严格 JSON 格式：
{
  "reviewer_analysis": {
    "Reviewer 1": {"credibility": "...", "type": "...", "score": 0, "critic": "..."}
  },
  "fatal_flaw_allegations": [],
  "consensus_type": "...",
  "risk_level": "High|Medium|Low",
  "meta_review_one_liner": "..."
}
"""

PROMPT_REBUTTAL_ANALYZER = """
你现在是 Senior Area Chair，分析 rebuttal 阶段的交互。

请评估：
1. Rebuttal 有效性：Strong / Moderate / Weak / Disastrous
2. 解决问题的成功率
3. 审稿人最终态度

输出严格 JSON 格式：
{
  "rebuttal_effectiveness": "Strong|Moderate|Weak|Disastrous",
  "success_rate": 0.0,
  "admitted_fatal_error": false,
  "reviewer_final_states": {},
  "ac_inner_monologue": "..."
}
"""

PROMPT_DECISION_COORDINATOR = """
你现在是 Program Chair，综合所有信息做出最终决策。

核心原则：
- 高分不等于接收（缺乏激情的论文应该拒绝）
- 低分不等于拒绝（如果有 Champion 支持且理由充分）
- 关键是有没有人愿意为这篇论文而战

输出严格 JSON 格式：
{
  "final_decision": "Oral|Spotlight|Poster|Reject",
  "final_score": 7.5,
  "decision_archetype": "...",
  "score_interpretation": "...",
  "key_factor": "...",
  "confidence": "High|Medium|Low"
}
"""


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def pdf_to_base64_images(pdf_path: str, max_pages: int = 8, max_size: int = 1024) -> List[str]:
    """Convert PDF pages to base64-encoded images."""
    if not PDF_SUPPORT:
        raise RuntimeError("PDF support not available. Install pdf2image and Pillow.")
    
    images = convert_from_path(pdf_path, dpi=150)
    base64_images = []
    
    for i, img in enumerate(images[:max_pages]):
        # Resize if too large
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        base64_images.append(b64)
    
    return base64_images


def call_api(system_prompt: str, user_message: str, images: Optional[List[str]] = None) -> str:
    """Call the OpenAI-compatible API."""
    messages = [{"role": "system", "content": system_prompt}]
    
    if images:
        # Vision request with images
        content = [{"type": "text", "text": user_message}]
        for img_b64 in images:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img_b64}"}
            })
        messages.append({"role": "user", "content": content})
    else:
        messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3,
            max_tokens=4096
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        print(f"API Error: {e}")
        return "{}"


def parse_json_response(text: str) -> Dict[str, Any]:
    """Extract JSON from API response."""
    # Try to find JSON in the response
    text = text.strip()
    
    # Remove markdown code blocks if present
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
    
    return {}


def preprocess_reviews(raw_data: Dict) -> Dict:
    """Preprocess review data into agent-friendly format."""
    processed = {
        "title": raw_data.get("title", ""),
        "abstract": raw_data.get("abstract", ""),
        "reviews": [],
        "global_rebuttal": ""
    }
    
    # Extract global rebuttal
    for comment in raw_data.get("official_comment", []):
        if "Response to all reviewers" in comment.get("title", ""):
            processed["global_rebuttal"] = comment.get("comment", {}).get("comment", "")
            break
    
    # Extract reviews
    for idx, item in enumerate(raw_data.get("peer_discussion", [])):
        review = item.get("review", {})
        processed["reviews"].append({
            "id": f"Reviewer_{idx+1}",
            "score": review.get("rating", 0),
            "confidence": review.get("confidence", 0),
            "summary": review.get("summary", ""),
            "strengths": review.get("strengths", ""),
            "weaknesses": review.get("weaknesses", "")
        })
    
    return processed


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def run_review_pipeline(pdf_path: str, reviews_path: Optional[str] = None) -> Dict[str, Any]:
    """Run the full paper review pipeline."""
    print(f"[*] Reviewing: {pdf_path}")
    
    # Agent 1: Visual Content Evaluation
    print("[1/4] Analyzing PDF content...")
    if PDF_SUPPORT:
        images = pdf_to_base64_images(pdf_path)
        agent1_response = call_api(
            PROMPT_CONTENT_EVALUATOR,
            "Analyze these paper pages and evaluate the technical contribution.",
            images=images
        )
    else:
        agent1_response = "{}"
    
    agent1_result = parse_json_response(agent1_response)
    
    # Load review data if provided
    reviews_data = None
    if reviews_path and os.path.exists(reviews_path):
        print("[*] Loading review data...")
        with open(reviews_path, 'r', encoding='utf-8') as f:
            raw_reviews = json.load(f)
        reviews_data = preprocess_reviews(raw_reviews)
    
    # Agent 2: Review Synthesis (if reviews available)
    agent2_result = {}
    if reviews_data and reviews_data["reviews"]:
        print("[2/4] Analyzing reviewer comments...")
        reviews_input = json.dumps(reviews_data["reviews"], ensure_ascii=False)
        agent2_response = call_api(
            PROMPT_REVIEW_SYNTHESIZER,
            f"Analyze these reviews: {reviews_input}"
        )
        agent2_result = parse_json_response(agent2_response)
    else:
        print("[2/4] No review data, skipping...")
    
    # Agent 3: Rebuttal Analysis (if rebuttal available)
    agent3_result = {}
    if reviews_data and reviews_data.get("global_rebuttal"):
        print("[3/4] Analyzing rebuttal...")
        rebuttal_input = json.dumps({
            "global_rebuttal": reviews_data["global_rebuttal"],
            "reviews": reviews_data["reviews"]
        }, ensure_ascii=False)
        agent3_response = call_api(
            PROMPT_REBUTTAL_ANALYZER,
            f"Analyze the rebuttal: {rebuttal_input}"
        )
        agent3_result = parse_json_response(agent3_response)
    else:
        print("[3/4] No rebuttal data, skipping...")
    
    # Agent 4: Final Decision
    print("[4/4] Making final decision...")
    final_input = {
        "visual_content_eval": agent1_result,
        "review_analysis": agent2_result,
        "rebuttal_analysis": agent3_result
    }
    
    if reviews_data:
        final_input["raw_scores"] = [r["score"] for r in reviews_data["reviews"]]
    
    decision_response = call_api(
        PROMPT_DECISION_COORDINATOR,
        f"Make the final decision based on: {json.dumps(final_input, ensure_ascii=False)}"
    )
    decision_result = parse_json_response(decision_response)
    
    # Compile final report
    report = {
        "title": reviews_data.get("title", os.path.basename(pdf_path)) if reviews_data else os.path.basename(pdf_path),
        "prediction": decision_result.get("final_decision", "Unknown"),
        "final_score": decision_result.get("final_score", 0),
        "decision": decision_result,
        "content_analysis": agent1_result,
        "review_analysis": agent2_result,
        "rebuttal_analysis": agent3_result
    }
    
    return report


def main():
    parser = argparse.ArgumentParser(
        description="AI-Powered Academic Paper Review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python review_paper.py --pdf paper.pdf
  python review_paper.py --pdf paper.pdf --reviews reviews.json
  python review_paper.py --pdf paper.pdf --output result.json

Environment Variables:
  PAPER_REVIEW_API_KEY  - OpenAI-compatible API key (required)
  PAPER_REVIEW_API_BASE - API base URL (optional)
  PAPER_REVIEW_MODEL    - Model name (optional, defaults to gpt-4o)
        """
    )
    parser.add_argument("--pdf", required=True, help="Path to the paper PDF file")
    parser.add_argument("--reviews", help="Path to reviews JSON file (optional)")
    parser.add_argument("--output", "-o", help="Output JSON file path (optional)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf):
        print(f"Error: PDF file not found: {args.pdf}")
        sys.exit(1)
    
    # Run pipeline
    result = run_review_pipeline(args.pdf, args.reviews)
    
    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n[*] Result saved to: {args.output}")
    else:
        print("\n" + "=" * 60)
        print("REVIEW RESULT")
        print("=" * 60)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Prediction: {result['prediction']}")
    print(f"Score: {result['final_score']}")
    print(f"Confidence: {result['decision'].get('confidence', 'N/A')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
