"""
Shutterstock Image Generator Module

Handles text-to-image generation using Shutterstock ImageAI.
"""

import base64
import requests
from config import client


def generate_image_shutterstock(prompt):
    """
    Generate an image using Shutterstock ImageAI.
    Optimized for artistic styles and creative prompts.
    
    Args:
        prompt: Text description of the image to generate (can include style hints)
    
    Returns:
        dict: Contains 'image_base64' and 'metadata'
    
    Raises:
        Exception: If image generation fails
    """
    try:
        response = client.images.generate(
            model="databricks-shutterstock-imageai",
            prompt=prompt
        )
        
        # Extract the generated image
        image_data = response.data[0]
        
        # If the response contains a URL, we need to fetch it
        # If it contains base64, we can use it directly
        if hasattr(image_data, 'b64_json'):
            return {
                'image_base64': image_data.b64_json,
                'metadata': {
                    'prompt': prompt,
                    'model': 'databricks-shutterstock-imageai'
                }
            }
        elif hasattr(image_data, 'url'):
            img_response = requests.get(image_data.url)
            img_base64 = base64.b64encode(img_response.content).decode('utf-8')
            return {
                'image_base64': img_base64,
                'metadata': {
                    'prompt': prompt,
                    'model': 'databricks-shutterstock-imageai'
                }
            }
    except Exception as e:
        raise Exception(f"Shutterstock image generation failed: {str(e)}")

