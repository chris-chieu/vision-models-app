# Vision Model App - Template

This is a sanitized template for the Vision Model App with a clean, modular structure. Before using, replace all placeholder values with your actual configuration.

## 📁 Project Structure

```
template/
├── app.py                          # Main Dash web application
├── config.py                       # Central configuration (API keys, URLs, settings)
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── modules/                        # Functional modules
    ├── __init__.py                 # Package initialization
    ├── utils.py                    # Base64 utilities
    ├── vision_query.py             # Vision model queries (GPT-5, Claude, Llama)
    ├── shutterstock_generator.py   # Text-to-image generation (Shutterstock)
    ├── image_transformer.py        # Image-to-image transformation (Kandinsky)
    ├── image_scorer.py             # Image quality scoring (LLM-as-a-Judge)
    ├── intent_analyzer.py          # Intent analysis (Claude Sonnet 4)
    └── intelligent_router.py       # Main routing logic
```

## 🎯 Module Responsibilities

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| **`config.py`** | Centralized configuration | API keys, model configs, endpoints |
| **`utils.py`** | Helper utilities | Base64 encoding/decoding, image processing |
| **`vision_query.py`** | Vision model queries | Query GPT-5, Claude Sonnet 4, Llama 4 Maverick |
| **`shutterstock_generator.py`** | Image generation | Text-to-image with Shutterstock ImageAI |
| **`image_transformer.py`** | Image transformation | Image-to-image with Kandinsky ControlNet |
| **`image_scorer.py`** | Quality scoring | Score images using vision models as judges |
| **`intent_analyzer.py`** | Intent detection | Analyze user intent (generate/transform/analyze) |
| **`intelligent_router.py`** | Main router | Route requests to appropriate models |
| **`app.py`** | Web interface | Dash application UI and callbacks |

---

## 📋 Configuration Placeholders

All sensitive values have been replaced with placeholders. You need to update `config.py` with your actual values:

### 1. **`<INSERT_DATABRICKS_TOKEN>`**
   - **Location**: `config.py` line 13
   - **Description**: Your Databricks workspace API token
   - **How to get**:
     ```python
     # Option 1: Generate from Databricks UI
     # Settings → User Settings → Access Tokens → Generate New Token
     
     # Option 2: In Databricks notebook
     DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
     ```

### 2. **`<INSERT_BASE_URL>`**
   - **Location**: `config.py` line 17
   - **Description**: Databricks model serving endpoint base URL
   - **Format**: `https://<workspace-url>/serving-endpoints`
   - **Example**: `https://your-workspace.cloud.databricks.com/serving-endpoints`

### 3. **Image-to-Image Configuration** (in `config.py`)
   - **`<INSERT_ENV_VAR_NAME>`**: Environment variable name for token storage
     - Example: `DATABRICKS_TOKEN`
   - **`<INSERT_SECRET_SCOPE>`**: Databricks secret scope name
     - Example: `my_secret_scope`
   - **`<INSERT_SECRET_KEY>`**: Key within the secret scope
     - Example: `model_serving_token`
   - **`<INSERT_IMAGE_TO_IMAGE_ENDPOINT_URL>`**: Kandinsky ControlNet endpoint URL
     - Example: `https://your-workspace.cloud.databricks.com/serving-endpoints/kandinsky-controlnet-img2img-endpoint/invocations`

---

## 🚀 Quick Start

### 1. **Configure the Application**

Edit `config.py` and replace all `<INSERT_*>` placeholders:

```python
# config.py
DATABRICKS_TOKEN = 'your_actual_token_here'
BASE_URL = "https://your-workspace.cloud.databricks.com/serving-endpoints"

IMAGE_TO_IMAGE_CONFIG = {
    "env_var_name": "YOUR_ENV_VAR",
    "secret_scope": "your_secret_scope",
    "secret_key": "your_secret_key",
    "endpoint_url": "https://your-workspace.../invocations"
}
```

### 2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 3. **Run the Application**

```bash
python app.py
```

### 4. **Access the App**

Open your browser to `http://localhost:8050`

---

## 🔧 Customization

### Adding a New Model

1. **Update `config.py`**:
   ```python
   MODEL_CONFIGS = {
       "your-new-model": {
           "name": "Your Model Name",
           "requires_cache_control": False,
           "type": "vision"  # or "diffuser"
       }
   }
   ```

2. **Create a new module** in `modules/` (e.g., `my_model.py`)
3. **Import in `modules/__init__.py`**
4. **Update routing logic** in `intelligent_router.py`

### Changing Default Models

Edit `config.py`:

```python
DEFAULT_VISION_MODEL = "databricks-gpt-5"  # Change this
DEFAULT_JUDGE_MODEL = "databricks-claude-sonnet-4"  # Change this
DEFAULT_ROUTER_MODEL = "databricks-claude-sonnet-4"  # Change this
```

---

## 🔒 Security Best Practices

1. **Never commit** `config.py` with real credentials to version control
2. **Use environment variables** for production:
   ```python
   import os
   DATABRICKS_TOKEN = os.getenv('DATABRICKS_TOKEN')
   ```
3. **Use Databricks Secrets** for sensitive data in notebooks:
   ```python
   from databricks.sdk import WorkspaceClient
   w = WorkspaceClient()
   token = w.dbutils.secrets.get(scope="my_scope", key="my_key")
   ```

### Recommended `.gitignore`

```
config.py
*.pyc
__pycache__/
.env
```

---

## 📦 Dependencies

All required packages are in `requirements.txt`:

- `dash` - Web framework
- `dash-bootstrap-components` - UI components
- `openai` - OpenAI API client (for Databricks)
- `Pillow` - Image processing
- `requests` - HTTP requests
- `pandas` - Data manipulation
- `databricks-sdk` - Databricks SDK

---

## 🧪 Testing Individual Modules

You can test each module independently:

### Test Vision Query
```python
from modules import query_vision_model

with open('test_image.jpg', 'rb') as f:
    img_bytes = f.read()

result = query_vision_model(
    image_bytes=img_bytes,
    question="What's in this image?",
    model="databricks-claude-sonnet-4"
)
print(result)
```

### Test Image Generation
```python
from modules import generate_image_shutterstock

result = generate_image_shutterstock("A sunset over mountains")
print(f"Generated image: {len(result['image_base64'])} bytes")
```

### Test Intelligent Router
```python
from modules import intelligent_query_router

result = intelligent_query_router(
    prompt="Generate a beautiful landscape",
    image_bytes=None  # Text-to-image
)
print(result)
```

---

## 🐛 Troubleshooting

### Import Errors

```python
# Make sure you're running from the template directory
cd /path/to/template
python app.py
```

### Module Not Found

```python
# Ensure modules/ has __init__.py
ls modules/__init__.py  # Should exist
```

### API Connection Errors

1. Check `config.py` has correct `BASE_URL`
2. Verify your Databricks token is valid
3. Ensure model endpoints are deployed in Databricks

### Image Generation Fails

- Verify the model name matches your deployed endpoint
- Check Databricks endpoint logs for errors
- Ensure you have sufficient quota/resources

---

## 📚 Additional Resources

- [Databricks Model Serving Documentation](https://docs.databricks.com/machine-learning/model-serving/index.html)
- [Databricks Secrets Management](https://docs.databricks.com/security/secrets/index.html)
- [Dash Documentation](https://dash.plotly.com/)
- [OpenAI Python Library](https://github.com/openai/openai-python)

---

## 🎯 Features

- **🤖 Intelligent Router**: Auto-detects user intent (generate/transform/analyze)
- **🖼️ Multiple Vision Models**: GPT-5, Claude Sonnet 4, Llama 4 Maverick
- **🎨 Image Generation**: Text-to-image with Shutterstock ImageAI
- **✨ Image Transformation**: Image-to-image with Kandinsky ControlNet
- **⭐ Quality Scoring**: LLM-as-a-Judge for image evaluation
- **🔄 Base64 Support**: Decode and display base64 encoded images
- **📱 Responsive UI**: Modern Dash interface with Bootstrap

---

## 💡 Tips

1. **Start with Manual Mode** to test individual models
2. **Use Intelligent Router** for production (auto-routes to best model)
3. **Check Databricks Logs** if you encounter API errors
4. **Test with small images first** to ensure endpoints work
5. **Monitor API usage** to avoid hitting quota limits

---

## 📝 License

This is a template for educational and development purposes. Make sure to comply with Databricks and model provider terms of service.

---

**Ready to deploy?** Just update `config.py` and you're good to go! 🚀
