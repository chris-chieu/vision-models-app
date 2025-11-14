"""
Utility Functions Module

Contains helper functions for base64 encoding/decoding and image processing.
"""

import base64
import re


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


def decode_base64_to_image(base64_string):
    """
    Decode a base64 string to image bytes.
    
    Args:
        base64_string: Base64 encoded string (with or without data URL prefix)
    
    Returns:
        tuple: (image_bytes, image_type) or (None, None) if decoding fails
    """
    try:
        # Remove data URL prefix if present
        if base64_string.startswith('data:image'):
            # Extract the image type and base64 data
            parts = base64_string.split(',')
            if len(parts) == 2:
                header = parts[0]  # data:image/png;base64
                base64_data = parts[1]
                # Extract image type from header
                image_type = header.split('/')[1].split(';')[0]
            else:
                base64_data = base64_string
                image_type = 'png'  # default
        else:
            base64_data = base64_string
            image_type = 'png'  # default
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(base64_data)
        
        return image_bytes, image_type
    except Exception as e:
        print(f"Error decoding base64: {e}")
        return None, None


def detect_base64_in_prompt(prompt):
    """
    Detect if the prompt contains a base64 encoded image.
    Base64 strings are typically long (>100 chars) and contain only valid base64 characters.
    
    Args:
        prompt: User's text prompt
    
    Returns:
        tuple: (has_base64, base64_string, cleaned_prompt)
    """
    # Look for long strings that look like base64 (alphanumeric + / + = + -)
    # Typically base64 images are >100 characters
    base64_pattern = r'[A-Za-z0-9+/]{100,}={0,2}'
    
    # Also check for data URL format
    data_url_pattern = r'data:image/[^;]+;base64,[A-Za-z0-9+/]+=*'
    
    # Check for data URL first
    data_url_match = re.search(data_url_pattern, prompt)
    if data_url_match:
        base64_string = data_url_match.group(0)
        cleaned_prompt = prompt.replace(base64_string, '').strip()
        return True, base64_string, cleaned_prompt
    
    # Check for raw base64
    base64_match = re.search(base64_pattern, prompt)
    if base64_match:
        base64_string = base64_match.group(0)
        cleaned_prompt = prompt.replace(base64_string, '').strip()
        return True, base64_string, cleaned_prompt
    
    return False, None, prompt

