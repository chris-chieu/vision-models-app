"""
Configuration Module

Central configuration for all API keys, URLs, and model settings.
"""

import os
from openai import OpenAI


# ============================================================================
# API CONFIGURATION
# ============================================================================

DATABRICKS_TOKEN = '<INSERT_DATABRICKS_TOKEN>'
# Alternative in Databricks notebook:
# DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

BASE_URL = "<INSERT_BASE_URL>"


# ============================================================================
# OPENAI CLIENT (for Databricks Model Serving)
# ============================================================================

client = OpenAI(
    api_key=DATABRICKS_TOKEN,
    base_url=BASE_URL
)


# ============================================================================
# MODEL CONFIGURATIONS
# ============================================================================

MODEL_CONFIGS = {
    "databricks-gpt-5": {
        "name": "Databricks GPT-5",
        "requires_cache_control": False,
        "type": "vision"
    },
    "databricks-claude-sonnet-4": {
        "name": "Claude Sonnet 4",
        "requires_cache_control": True,
        "type": "vision"
    },
    "databricks-llama-4-maverick": {
        "name": "Llama 4 Maverick",
        "requires_cache_control": True,
        "type": "vision"
    },
    "databricks-shutterstock-imageai": {
        "name": "Shutterstock ImageAI (Text-to-Image)",
        "requires_cache_control": False,
        "type": "diffuser"
    }
}


# ============================================================================
# IMAGE-TO-IMAGE CONFIGURATION (Kandinsky ControlNet)
# ============================================================================

IMAGE_TO_IMAGE_CONFIG = {
    "env_var_name": "<INSERT_ENV_VAR_NAME>",
    "secret_scope": "<INSERT_SECRET_SCOPE>",
    "secret_key": "<INSERT_SECRET_KEY>",
    "endpoint_url": "<INSERT_IMAGE_TO_IMAGE_ENDPOINT_URL>"
}


# ============================================================================
# DEFAULT SETTINGS
# ============================================================================

DEFAULT_VISION_MODEL = "databricks-claude-sonnet-4"
DEFAULT_JUDGE_MODEL = "databricks-claude-sonnet-4"
DEFAULT_ROUTER_MODEL = "databricks-claude-sonnet-4"

