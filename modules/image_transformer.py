"""
Image Transformer Module

Handles image-to-image transformation using Kandinsky ControlNet.
"""

import os
import json
import base64
import requests
import pandas as pd
from typing import Optional, Tuple
from config import IMAGE_TO_IMAGE_CONFIG


def generate_image_from_image(
    prompt: str,
    input_image,
    strength: float = 0.5,
    guidance_scale: float = 12.0,
    num_inference_steps: int = 50,
    negative_prior_prompt: Optional[str] = None
) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Generate a new image based on an input image and text prompt using Kandinsky ControlNet.
    
    Args:
        prompt: Text description of what you want to generate
        input_image: Input image as bytes or base64 string
        strength: How much to transform the image (0.0-1.0). 
                 0.0 = keep original, 1.0 = completely new image
        guidance_scale: How closely to follow the prompt (higher = more adherence)
        num_inference_steps: Number of denoising steps (more = better quality)
        negative_prior_prompt: What NOT to include in the generated image
    
    Returns:
        tuple: (image_bytes, error_message) - one will be None
    """
    try:
        # Get Databricks token from secrets
        from databricks.sdk import WorkspaceClient
        
        _environ_var_name = IMAGE_TO_IMAGE_CONFIG["env_var_name"]
        _secret_scope_name = IMAGE_TO_IMAGE_CONFIG["secret_scope"]
        _secret_scope_key = IMAGE_TO_IMAGE_CONFIG["secret_key"]
        
        try:
            w = WorkspaceClient()
            os.environ[_environ_var_name] = w.dbutils.secrets.get(
                scope=_secret_scope_name, 
                key=_secret_scope_key
            )
        except Exception as e:
            # If not in Databricks environment, try to use existing env var
            if _environ_var_name not in os.environ:
                return None, f"Failed to get Databricks token: {e}"
        
        # Default negative prompt if not provided
        if negative_prior_prompt is None:
            negative_prior_prompt = (
                "lowres, changed skin tones, error, cropped, worst quality, "
                "low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, "
                "out of frame, extra fingers, mutated hands, poorly drawn hands, "
                "poorly drawn face, mutation, deformed, blurry, dehydrated, "
                "bad anatomy, bad proportions, extra limbs, cloned face"
            )
        
        # Convert input to base64 if not already
        if isinstance(input_image, bytes):
            # Convert bytes to base64
            input_image_base64 = base64.b64encode(input_image).decode('utf-8')
            print(f"Converted {len(input_image)} bytes to base64 ({len(input_image_base64)} chars)")
        elif isinstance(input_image, str):
            # Already base64
            input_image_base64 = input_image
            print(f"Using provided base64 string ({len(input_image_base64)} chars)")
        else:
            return None, f"Invalid input_image type: {type(input_image)}. Expected bytes or str."
        
        # Prepare input data
        input_example = pd.DataFrame({
            "prompt": [prompt],
            "negative_prior_prompt": [negative_prior_prompt],
            "num_inference_steps": [num_inference_steps],
            "init_image": [input_image_base64],
            "strength": [strength],
            "guidance_scale": [guidance_scale]
        })
        
        # API endpoint
        url = IMAGE_TO_IMAGE_CONFIG["endpoint_url"]
        
        # Prepare request
        headers = {
            'Authorization': f'Bearer {os.environ.get(_environ_var_name)}',
            'Content-Type': 'application/json'
        }
        
        ds_dict = {'dataframe_split': input_example.to_dict(orient='split')}
        data_json = json.dumps(ds_dict, allow_nan=True)
        
        # Make request
        print(f"Sending image-to-image request to Kandinsky endpoint...")
        print(f"Prompt: {prompt}")
        print(f"Strength: {strength}, Guidance: {guidance_scale}, Steps: {num_inference_steps}")
        
        response = requests.request(
            method='POST',
            headers=headers,
            url=url,
            data=data_json,
            timeout=120  # 2 minute timeout
        )
        
        # Check response
        if response.status_code != 200:
            error_msg = f"API request failed with status {response.status_code}: {response.text}"
            print(error_msg)
            return None, error_msg
        
        # Decode the generated image from response
        result = response.json()
        image_bytes = base64.b64decode(result['predictions'])
        print(f"✓ Successfully generated image ({len(image_bytes):,} bytes)")
        return image_bytes, None
    
    except requests.exceptions.Timeout:
        return None, "Request timed out. The image generation took too long."
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {e}"
    except Exception as e:
        return None, f"Unexpected error in image-to-image generation: {e}"


def image_to_image_query(
    prompt: str,
    image_bytes: bytes,
    image_type: str = "jpeg",
    strength: float = 0.5,
    guidance_scale: float = 12.0,
    num_inference_steps: int = 50
) -> dict:
    """
    High-level wrapper for image-to-image generation.
    
    Args:
        prompt: What to generate
        image_bytes: Input image as bytes
        image_type: Image type (jpeg, png, etc.)
        strength: Transformation strength (0.0-1.0)
        guidance_scale: Prompt adherence (1-20, typically 7-15)
        num_inference_steps: Quality steps (20-100, typically 30-50)
    
    Returns:
        dict: Contains 'result', 'image_base64', 'image_bytes', 'metadata', or 'error'
    """
    try:
        # Validate input
        if not image_bytes or len(image_bytes) == 0:
            return {
                'result': "Error: No image data provided",
                'error': "Empty image bytes"
            }
        
        # Generate new image (conversion to base64 happens inside the function)
        generated_bytes, error = generate_image_from_image(
            prompt=prompt,
            input_image=image_bytes,
            strength=strength,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps
        )
        
        if error:
            return {
                'result': f"Image generation failed: {error}",
                'error': error
            }
        
        # Encode generated image for display
        generated_base64 = base64.b64encode(generated_bytes).decode('utf-8')
        
        return {
            'result': f"Successfully generated image from your input! Prompt: '{prompt}'",
            'image_base64': generated_base64,
            'image_bytes': generated_bytes,
            'image_type': 'png',  # Kandinsky typically returns PNG
            'metadata': {
                'model': 'kandinsky-controlnet-img2img',
                'prompt': prompt,
                'strength': strength,
                'guidance_scale': guidance_scale,
                'num_inference_steps': num_inference_steps,
                'input_image_size': len(image_bytes),
                'output_image_size': len(generated_bytes)
            }
        }
    
    except Exception as e:
        return {
            'result': f"Error in image-to-image generation: {str(e)}",
            'error': str(e)
        }

