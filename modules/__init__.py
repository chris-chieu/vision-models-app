"""
Modules Package

This package contains all the functional modules for the Vision Model App.
"""

from .utils import encode_image_to_base64, decode_base64_to_image, detect_base64_in_prompt
from .vision_query import query_vision_model
from .shutterstock_generator import generate_image_shutterstock
from .image_transformer import image_to_image_query
from .image_scorer import score_generated_image, IMAGE_SCORING_CRITERIA
from .intent_analyzer import analyze_intent_with_claude
from .intelligent_router import intelligent_query_router

__all__ = [
    'encode_image_to_base64',
    'decode_base64_to_image',
    'detect_base64_in_prompt',
    'query_vision_model',
    'generate_image_shutterstock',
    'image_to_image_query',
    'score_generated_image',
    'IMAGE_SCORING_CRITERIA',
    'analyze_intent_with_claude',
    'intelligent_query_router'
]

