"""
Image Scorer Module

Implements Image-as-a-Judge scoring for generated images,
inspired by MLflow's LLM-as-a-Judge approach.
"""

import base64
import json
from config import client


# Image Quality Scoring Criteria (inspired by MLflow LLM-as-a-Judge)
IMAGE_SCORING_CRITERIA = {
    "prompt_adherence": {
        "name": "Prompt Adherence",
        "description": "How well does the generated image match the text prompt?",
        "scale": "1-5 (1=Poor match, 5=Perfect match)"
    },
    "visual_quality": {
        "name": "Visual Quality",
        "description": "Overall technical quality: clarity, composition, lighting, colors",
        "scale": "1-5 (1=Poor quality, 5=Professional quality)"
    },
    "creativity": {
        "name": "Creativity",
        "description": "How creative and aesthetically pleasing is the image?",
        "scale": "1-5 (1=Generic, 5=Highly creative)"
    },
    "coherence": {
        "name": "Coherence",
        "description": "Are all elements in the image logical and well-integrated?",
        "scale": "1-5 (1=Incoherent, 5=Perfectly coherent)"
    }
}


def encode_image_to_base64(image_bytes, image_type="jpeg"):
    """
    Convert image bytes to base64 data URL.
    
    Args:
        image_bytes: Raw bytes of the image
        image_type: Type of image (jpeg, png, etc.)
    
    Returns:
        str: Base64 encoded data URL
    """
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:image/{image_type};base64,{base64_image}"


def score_generated_image(image_bytes, original_prompt, judge_model="databricks-claude-sonnet-4", criteria=None):
    """
    Score a generated image using a vision model as judge (Image-as-a-Judge).
    Inspired by MLflow's LLM-as-a-Judge approach adapted for images.
    
    Args:
        image_bytes: Raw bytes of the generated image
        original_prompt: The text prompt used to generate the image
        judge_model: Vision model to use as judge (default: databricks-claude-sonnet-4)
        criteria: List of criteria keys to evaluate (default: all criteria)
    
    Returns:
        dict: Scores and rationales for each criterion
    """
    if criteria is None:
        criteria = list(IMAGE_SCORING_CRITERIA.keys())
    
    # Build evaluation prompt
    criteria_descriptions = "\n".join([
        f"- **{IMAGE_SCORING_CRITERIA[c]['name']}**: {IMAGE_SCORING_CRITERIA[c]['description']} (Scale: {IMAGE_SCORING_CRITERIA[c]['scale']})"
        for c in criteria if c in IMAGE_SCORING_CRITERIA
    ])
    
    evaluation_prompt = f"""You are an expert image quality evaluator. Evaluate the generated image based on the following criteria:

**Original Prompt**: "{original_prompt}"

**Evaluation Criteria**:
{criteria_descriptions}

For EACH criterion, provide:
1. A score (1-5)
2. A brief rationale explaining your score

Respond in the following JSON format:
{{
  "scores": {{
    "prompt_adherence": {{"score": <1-5>, "rationale": "explanation"}},
    "visual_quality": {{"score": <1-5>, "rationale": "explanation"}},
    "creativity": {{"score": <1-5>, "rationale": "explanation"}},
    "coherence": {{"score": <1-5>, "rationale": "explanation"}}
  }},
  "overall_score": <average of all scores>,
  "summary": "brief overall assessment"
}}"""
    
    try:
        # Encode image to base64 data URL
        img_data_url = encode_image_to_base64(image_bytes, "png")
        
        # Build the content array
        # For Claude Sonnet 4, use cache_control at the image_url level
        image_content = {
            "type": "image_url",
            "image_url": {
                "url": img_data_url
            }
        }
        
        # Add cache_control for Claude models
        if "claude" in judge_model.lower():
            image_content["cache_control"] = {"type": "ephemeral"}
        
        content = [
            {
                "type": "text",
                "text": evaluation_prompt
            },
            image_content
        ]
        
        # Query vision model as judge
        response = client.chat.completions.create(
            model=judge_model,
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ]
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON if wrapped in markdown
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        scores = json.loads(result_text)
        scores['judge_model'] = judge_model
        
        return scores
        
    except Exception as e:
        # Return detailed error information for debugging
        import traceback
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "judge_model": judge_model,
            "message": f"Scoring failed: {str(e)}"
        }

