"""
Intent Analyzer Module

Analyzes user intent using Claude Sonnet 4 to determine whether
the user wants to generate, transform, or analyze an image.
"""

import json
from config import client, DEFAULT_ROUTER_MODEL


def analyze_intent_with_claude(prompt, has_image=False):
    """
    Use Claude Sonnet 4 to analyze user intent and determine the appropriate action and model.
    
    Args:
        prompt: User's text prompt
        has_image: Boolean indicating if an image is provided
    
    Returns:
        dict: Contains 'action', 'model_recommendation', and 'reasoning'
    """
    analysis_prompt = f"""You are an AI router that determines user intent and recommends the best model. Analyze the following:

User Prompt: "{prompt}"
Has Image Attached: {has_image}

Determine which action and model is appropriate:

ACTIONS:
1. "generate_image" - User wants to CREATE/GENERATE an image from text description (no input image)
2. "analyze_image" - User wants to ANALYZE/UNDERSTAND an existing image
3. "transform_image" - User wants to TRANSFORM/MODIFY an existing image based on a prompt (image-to-image)

Important Rules:
- PRIORITY: If prompt asks about existing content ("what", "describe", "identify", "what's", "tell me about"), choose "analyze_image" 
- If has_image is True AND prompt contains generation/transformation verbs ("generate", "create", "draw", "make", "produce", "turn into", "convert", "transform", "modify"), choose "transform_image"
- If has_image is False AND prompt contains generation verbs, choose "generate_image"
- If has_image is True AND prompt is ambiguous, default to "analyze_image"
- For text-to-image generation, use Shutterstock ImageAI
- For image-to-image transformation, use Kandinsky ControlNet

EXAMPLES:
- "generate a sunset" + has_image=False → "generate_image" (text-to-image)
- "generate a pokemon" + has_image=True → "transform_image" (image-to-image transformation)
- "what's in this image?" + has_image=True → "analyze_image" (analysis keywords)
- "turn this into a watercolor painting" + has_image=True → "transform_image"
- "create an impressionist painting" + has_image=False → "generate_image"
- "make this image look like a cartoon" + has_image=True → "transform_image"

Respond ONLY with a JSON object in this exact format:
{{"action": "generate_image" or "analyze_image" or "transform_image", "reasoning": "brief explanation"}}"""

    try:
        response = client.chat.completions.create(
            model=DEFAULT_ROUTER_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": analysis_prompt
                }
            ],
            temperature=0.1
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON if wrapped in markdown
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(result_text)
        return result
    except Exception as e:
        # Fallback logic if Claude analysis fails
        if has_image:
            return {"action": "analyze_image", "reasoning": f"Image provided (fallback due to: {str(e)})"}
        else:
            return {"action": "generate_image", "reasoning": f"No image provided (fallback due to: {str(e)})"}

