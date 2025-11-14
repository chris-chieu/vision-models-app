"""
Intelligent Router Module

Main routing logic that analyzes user input and directs to appropriate model/function.
"""

from config import DEFAULT_VISION_MODEL
from .utils import detect_base64_in_prompt, decode_base64_to_image, encode_image_to_base64
from .intent_analyzer import analyze_intent_with_claude
from .shutterstock_generator import generate_image_shutterstock
from .image_transformer import image_to_image_query
from .vision_query import query_vision_model


def intelligent_query_router(prompt, image_bytes=None, image_type="jpeg", vision_model=None):
    """
    Intelligent router that analyzes the input and calls the appropriate function.
    
    Args:
        prompt: User's text prompt
        image_bytes: Optional image bytes (None if no image)
        image_type: Type of image (jpeg, png, etc.)
        vision_model: Which vision model to use for image analysis (default from config)
    
    Returns:
        dict: Contains 'result', 'action_taken', 'reasoning', and optionally 'image_base64'
    """
    if vision_model is None:
        vision_model = DEFAULT_VISION_MODEL
    
    # Step 0: Check if prompt contains a base64 encoded image
    has_base64, base64_string, cleaned_prompt = detect_base64_in_prompt(prompt)
    
    if has_base64:
        # Decode the base64 string to image
        decoded_bytes, decoded_type = decode_base64_to_image(base64_string)
        
        if decoded_bytes:
            # Successfully decoded - re-encode to data URL for display
            display_base64 = encode_image_to_base64(decoded_bytes, decoded_type)
            
            return {
                'result': f"Base64 image decoded successfully! {cleaned_prompt if cleaned_prompt else 'Image displayed below.'}",
                'action_taken': 'decode_base64',
                'reasoning': 'Detected base64 encoded image in prompt',
                'image_base64': display_base64,
                'image_type': decoded_type,
                'metadata': {
                    'decoded_from': 'base64_string',
                    'image_size_bytes': len(decoded_bytes)
                }
            }
        else:
            return {
                'result': "Error: Failed to decode base64 string. Please check if it's a valid base64 encoded image.",
                'action_taken': 'decode_base64_failed',
                'reasoning': 'Base64 decoding failed'
            }
    
    has_image = image_bytes is not None
    
    # Step 1: Analyze intent using Claude
    intent = analyze_intent_with_claude(prompt, has_image)
    
    # Step 2: Route to appropriate function
    if intent['action'] == 'generate_image':
        # User wants to generate an image from text - use Shutterstock ImageAI
        result = generate_image_shutterstock(prompt)
        
        return {
            'result': f"Image generated successfully based on prompt: '{prompt}'",
            'action_taken': 'generate_image',
            'reasoning': intent['reasoning'],
            'image_base64': result['image_base64'],
            'metadata': result['metadata'],
            'model_used': 'databricks-shutterstock-imageai'
        }
    
    elif intent['action'] == 'transform_image':
        # User wants to transform/modify an existing image (image-to-image)
        if not has_image:
            return {
                'result': "Error: Image transformation requested but no image was provided.",
                'action_taken': 'transform_image',
                'reasoning': intent['reasoning'],
                'error': True
            }
        
        result = image_to_image_query(
            prompt=prompt,
            image_bytes=image_bytes,
            image_type=image_type
        )
        
        # Check if there was an error
        if 'error' in result:
            return {
                'result': result['result'],
                'action_taken': 'transform_image',
                'reasoning': intent['reasoning'],
                'error': True
            }
        
        return {
            'result': result['result'],
            'action_taken': 'transform_image',
            'reasoning': intent['reasoning'],
            'image_base64': result['image_base64'],
            'image_bytes': result['image_bytes'],
            'image_type': result['image_type'],
            'metadata': result['metadata'],
            'model_used': 'kandinsky-controlnet-img2img'
        }
    
    elif intent['action'] == 'analyze_image':
        # User wants to analyze an existing image
        if not has_image:
            return {
                'result': "Error: Image analysis requested but no image was provided.",
                'action_taken': 'analyze_image',
                'reasoning': intent['reasoning'],
                'error': True
            }
        
        response = query_vision_model(
            image_bytes=image_bytes,
            question=prompt,
            image_type=image_type,
            model=vision_model
        )
        
        return {
            'result': response,
            'action_taken': 'analyze_image',
            'reasoning': intent['reasoning'],
            'model_used': vision_model
        }
    
    else:
        return {
            'result': "Error: Unable to determine appropriate action.",
            'action_taken': 'unknown',
            'reasoning': "Intent analysis returned unexpected result",
            'error': True
        }

