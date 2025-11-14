"""
Vision Query Module

Handles queries to vision models (GPT-5, Claude Sonnet 4, Llama 4 Maverick).
"""

from config import client, MODEL_CONFIGS
from .utils import encode_image_to_base64


def query_vision_model(image_bytes, question="What's in this image?", image_type="jpeg", model="databricks-gpt-5"):
    """
    Query the vision model with an image and optional question.
    
    Args:
        image_bytes: Raw bytes of the image
        question: Text question to ask about the image
        image_type: Type of image (jpeg, png, etc.)
        model: Model identifier (e.g., "databricks-gpt-5", "databricks-llama-4-maverick")
    
    Returns:
        str: The model's response text
    """
    img_data_url = encode_image_to_base64(image_bytes, image_type)
    
    # Get model configuration
    model_config = MODEL_CONFIGS.get(model, {"requires_cache_control": False})
    
    # Build the image_url content
    image_url_content = {
        "type": "image_url",
        "image_url": {
            "url": img_data_url
        }
    }
    
    # Add cache_control for models that require it
    if model_config.get("requires_cache_control"):
        image_url_content["cache_control"] = {"type": "ephemeral"}

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": question
                    },
                    image_url_content
                ]
            }
        ]
    )
    
    return response.choices[0].message.content

