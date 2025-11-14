"""
Vision Model App - Main Dash Application

A web application for image generation, transformation, and analysis using various AI models.
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import base64
import io
from PIL import Image

# Import from config and modules
from config import MODEL_CONFIGS
from modules import (
    query_vision_model,
    intelligent_query_router,
    score_generated_image
)


# Initialize the Dash app with a modern theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

app.title = "Vision Model App"

# App layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("🖼️ Vision Model Query App", className="text-center mt-4 mb-2"),
            html.P(
                "Upload an image and ask questions about it using the Databricks GPT-5 vision model.",
                className="text-center text-muted mb-4"
            )
        ])
    ]),
    
    # Mode selection
    dbc.Row([
        dbc.Col([
            dbc.Label("Select Mode", className="fw-bold"),
            dbc.RadioItems(
                id="mode-selection",
                options=[
                    {"label": "🤖 Intelligent Router (Auto-detect intent)", "value": "intelligent"},
                    {"label": "🎯 Manual Model Selection", "value": "manual"}
                ],
                value="intelligent",
                className="mb-3"
            )
        ], width=12)
    ]),
    
    # Model selection (shown only in manual mode)
    dbc.Row([
        dbc.Col([
            html.Div(id="model-selection-container", children=[
                dbc.Label("Select Vision Model", className="fw-bold"),
                dcc.Dropdown(
                    id="model-dropdown",
                    options=[
                        {"label": config["name"], "value": model_id}
                        for model_id, config in MODEL_CONFIGS.items()
                        if config.get("type") == "vision"
                    ],
                    value="databricks-claude-sonnet-4",
                    clearable=False,
                    className="mb-3"
                )
            ])
        ], width=12)
    ]),
    
    # Question input
    dbc.Row([
        dbc.Col([
            dbc.Label("What would you like to know about the image?", className="fw-bold"),
            dbc.Input(
                id="question-input",
                type="text",
                placeholder="Enter your question...",
                value="What's in this image?",
                className="mb-3"
            )
        ], width=12)
    ]),
    
    # File upload
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id='upload-image',
                children=dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="bi bi-cloud-upload", style={"fontSize": "3rem"}),
                            html.H5("Drag and Drop or Click to Select an Image (Optional)", className="mt-2"),
                            html.P("Supported formats: JPG, PNG, GIF, BMP", className="text-muted"),
                            html.P("💡 Tip: Leave empty for text-to-image generation!", className="text-info small")
                        ], className="text-center")
                    ])
                ], color="light", className="border-2 border-dashed mb-3"),
                style={
                    'borderRadius': '5px',
                    'cursor': 'pointer'
                },
                multiple=False
            )
        ], width=12)
    ]),
    
    # Image preview
    dbc.Row([
        dbc.Col([
            html.Div(id='image-preview', className="mb-3")
        ], width=12)
    ]),
    
    # Clear image button (shown only when image is uploaded)
    dbc.Row([
        dbc.Col([
            html.Div(id='clear-button-container')
        ], width=12)
    ]),
    
    # Analyze button
    dbc.Row([
        dbc.Col([
            dbc.Button(
                "🚀 Process Query",
                id="analyze-button",
                color="primary",
                size="lg",
                className="w-100 mb-3",
                disabled=False
            )
        ], width=12)
    ]),
    
    # Results with loading spinner
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading-process",
                type="default",
                children=html.Div(id='result-output'),
                fullscreen=False,
                color="#0d6efd",
                parent_style={'minHeight': '100px'}
            )
        ], width=12)
    ]),
    
    # Score Image button (shown only after generation)
    dbc.Row([
        dbc.Col([
            html.Div(id='score-button-container')
        ], width=12)
    ]),
    
    # Scoring results with loading spinner
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading-scoring",
                type="circle",
                children=html.Div(id='scoring-output'),
                fullscreen=False,
                color="#0dcaf0",
                parent_style={'minHeight': '100px'}
            )
        ], width=12)
    ]),
    
    # Footer
    html.Hr(className="mt-4"),
    dbc.Row([
        dbc.Col([
            html.P(
                "Powered by Databricks Model Serving",
                className="text-center text-muted small"
            )
        ])
    ]),
    
    # Hidden div to store image data
    dcc.Store(id='stored-image-data'),
    
    # Store for generated image data (for scoring)
    dcc.Store(id='generated-image-data'),
    
    # Hidden button for clear functionality (actual button created dynamically)
    html.Button(id='clear-image-button', style={'display': 'none'}),
    
    # Hidden button for scoring (actual button created dynamically)
    html.Button(id='score-image-button', style={'display': 'none'})
    
], fluid=False, className="py-3", style={"maxWidth": "900px"})


@app.callback(
    Output('model-selection-container', 'style'),
    [Input('mode-selection', 'value')]
)
def toggle_model_selection(mode):
    """Show/hide model selection based on mode."""
    if mode == "manual":
        return {'display': 'block'}
    return {'display': 'none'}


@app.callback(
    [Output('image-preview', 'children'),
     Output('stored-image-data', 'data'),
     Output('clear-button-container', 'children')],
    [Input('upload-image', 'contents'),
     Input('clear-image-button', 'n_clicks')],
    [State('upload-image', 'filename')]
)
def update_image_preview(contents, clear_clicks, filename):
    """Update the image preview when a file is uploaded or cleared."""
    ctx = dash.callback_context
    
    # Check if clear button was clicked
    if ctx.triggered and ctx.triggered[0]['prop_id'] == 'clear-image-button.n_clicks':
        return html.Div(
            dbc.Alert(
                "💡 Image cleared. You can upload a new image or enter a text prompt for image generation!",
                color="info",
                className="text-center"
            )
        ), None, None
    
    if contents is None:
        return html.Div(
            dbc.Alert(
                "💡 No image uploaded. You can still enter a text prompt for image generation!",
                color="info",
                className="text-center"
            )
        ), None, None
    
    try:
        # Store the image data
        image_data = {
            'contents': contents,
            'filename': filename
        }
        
        # Create preview
        preview = dbc.Card([
            dbc.CardHeader(html.H5("Uploaded Image", className="mb-0")),
            dbc.CardBody([
                html.Img(
                    src=contents,
                    style={
                        'maxWidth': '100%',
                        'height': 'auto',
                        'display': 'block',
                        'margin': '0 auto'
                    }
                )
            ])
        ], className="mb-3")
        
        # Add clear button
        clear_button = dbc.Button(
            "🗑️ Clear Image",
            id="clear-image-button",
            color="secondary",
            size="sm",
            className="mb-3"
        )
        
        return preview, image_data, clear_button
        
    except Exception as e:
        return html.Div(
            dbc.Alert(
                f"Error loading image: {str(e)}",
                color="danger"
            )
        ), None, None


@app.callback(
    [Output('result-output', 'children'),
     Output('score-button-container', 'children'),
     Output('generated-image-data', 'data')],
    [Input('analyze-button', 'n_clicks')],
    [State('stored-image-data', 'data'),
     State('question-input', 'value'),
     State('model-dropdown', 'value'),
     State('mode-selection', 'value')]
)
def analyze_image(n_clicks, image_data, question, selected_model, mode):
    """Analyze the image when the button is clicked."""
    if n_clicks is None:
        return None, None, None
    
    if not question or question.strip() == "":
        return dbc.Alert(
            "Please enter a question or prompt.",
            color="warning"
        ), None, None
    
    try:
        # Prepare image data if available
        decoded = None
        image_type = "jpeg"
        
        if image_data is not None:
            content_string = image_data['contents']
            filename = image_data['filename']
            
            # Decode the base64 string to get image bytes
            content_type, content_string = content_string.split(',')
            decoded = base64.b64decode(content_string)
            
            # Determine image type from filename
            if filename:
                ext = filename.lower().split('.')[-1]
                if ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
                    image_type = 'jpeg' if ext == 'jpg' else ext
        
        # Use intelligent router or manual mode
        if mode == "intelligent":
            # Intelligent routing
            result = intelligent_query_router(
                prompt=question or "What's in this image?",
                image_bytes=decoded,
                image_type=image_type,
                vision_model=selected_model or "databricks-claude-sonnet-4"
            )
            
            if result.get('error'):
                return dbc.Alert([
                    html.H5("Error", className="alert-heading"),
                    html.P(result['result'])
                ], color="danger", className="mt-3"), None, None
            
            # Build response card based on action taken
            card_body_content = [
                html.P([
                    html.Strong("🤖 Mode: "),
                    "Intelligent Router"
                ], className="mb-2"),
                html.P([
                    html.Strong("🎯 Action Taken: "),
                    "Image Generation" if result['action_taken'] == 'generate_image' 
                    else "Image Transformation" if result['action_taken'] == 'transform_image'
                    else "Base64 Image Decoding" if result['action_taken'] == 'decode_base64'
                    else "Image Analysis"
                ], className="mb-2"),
                html.P([
                    html.Strong("💭 Reasoning: "),
                    result['reasoning']
                ], className="mb-3")
            ]
            
            # Handle different action types
            if result['action_taken'] in ['generate_image', 'transform_image']:
                # Display generated/transformed image
                img_b64 = result['image_base64']
                model_used = result.get('model_used', 'Unknown')
                model_name = MODEL_CONFIGS.get(model_used, {}).get("name", model_used)
                
                card_body_content.extend([
                    html.P([
                        html.Strong("Model Used: "),
                        model_name
                    ], className="mb-2"),
                    html.P([
                        html.Strong("Prompt: "),
                        question
                    ], className="mb-3"),
                    html.Hr(),
                    html.H6("Result Image:", className="mb-2"),
                    html.Img(
                        src=f"data:image/png;base64,{img_b64}",
                        style={'maxWidth': '100%', 'height': 'auto', 'borderRadius': '8px'}
                    )
                ])
                
                # Create score button
                score_button = dbc.Button(
                    html.Span("⭐ Score This Image (LLM-as-a-Judge)"),
                    id="score-image-button",
                    color="info",
                    size="lg",
                    className="w-100 mt-3 mb-3"
                )
                
                gen_img_data = {
                    'image_base64': img_b64,
                    'prompt': question
                }
                
                header_text = "🤖 Intelligent Router Result"
                if result['action_taken'] == 'transform_image':
                    header_text = "🎨 Image Transformation Complete"
                
                result_card = dbc.Card([
                    dbc.CardHeader(
                        html.H5(header_text, className="mb-0"),
                        className="bg-success text-white"
                    ),
                    dbc.CardBody(card_body_content)
                ], className="mt-3")
                
                return result_card, score_button, gen_img_data
            
            elif result['action_taken'] == 'decode_base64':
                # Display decoded image
                img_b64 = result['image_base64']
                if img_b64.startswith('data:image'):
                    img_b64 = img_b64.split(',')[1]
                
                card_body_content.extend([
                    html.P([
                        html.Strong("Image Type: "),
                        result.get('image_type', 'unknown')
                    ], className="mb-2"),
                    html.Hr(),
                    html.H6("Decoded Image:", className="mb-2"),
                    html.Img(
                        src=f"data:image/{result.get('image_type', 'png')};base64,{img_b64}",
                        style={'maxWidth': '100%', 'height': 'auto', 'borderRadius': '8px'}
                    )
                ])
                
                result_card = dbc.Card([
                    dbc.CardHeader(
                        html.H5("🤖 Base64 Image Decoded", className="mb-0"),
                        className="bg-info text-white"
                    ),
                    dbc.CardBody(card_body_content)
                ], className="mt-3")
                
                return result_card, None, None
            
            else:
                # Display analysis result
                model_used = result.get('model_used', 'Unknown')
                model_name = MODEL_CONFIGS.get(model_used, {}).get("name", model_used)
                
                card_body_content.extend([
                    html.P([
                        html.Strong("Model Used: "),
                        model_name
                    ], className="mb-2"),
                    html.Hr(),
                    html.P([
                        html.Strong("Answer:")
                    ], className="mb-2"),
                    html.Div(result['result'], className="border-start border-4 border-primary ps-3")
                ])
                
                result_card = dbc.Card([
                    dbc.CardHeader(
                        html.H5("🤖 Intelligent Router Result", className="mb-0"),
                        className="bg-success text-white"
                    ),
                    dbc.CardBody(card_body_content)
                ], className="mt-3")
                
                return result_card, None, None
            
        else:
            # Manual mode - direct vision model call
            if decoded is None:
                return dbc.Alert(
                    "Please upload an image for manual vision model analysis.",
                    color="warning",
                    className="mt-3"
                ), None, None
            
            response = query_vision_model(
                image_bytes=decoded,
                question=question or "What's in this image?",
                image_type=image_type,
                model=selected_model or "databricks-claude-sonnet-4"
            )
            
            # Get model name for display
            model_name = MODEL_CONFIGS.get(selected_model, {}).get("name", selected_model)
            
            # Return the result
            result_card = dbc.Card([
                dbc.CardHeader(
                    html.H5("🎯 Manual Model Response", className="mb-0"),
                    className="bg-success text-white"
                ),
                dbc.CardBody([
                    html.P([
                        html.Strong("Model: "),
                        model_name
                    ], className="mb-2"),
                    html.P([
                        html.Strong("Question: "),
                        question or "What's in this image?"
                    ], className="mb-3"),
                    html.Hr(),
                    html.P([
                        html.Strong("Answer:")
                    ], className="mb-2"),
                    html.Div(response, className="border-start border-4 border-primary ps-3")
                ])
            ], className="mt-3")
            
            return result_card, None, None
        
    except Exception as e:
        return dbc.Alert([
            html.H5("An error occurred", className="alert-heading"),
            html.P(str(e)),
            html.Hr(),
            html.P("Please check your API credentials and connection.", className="mb-0")
        ], color="danger", className="mt-3"), None, None


@app.callback(
    Output('scoring-output', 'children'),
    [Input('score-image-button', 'n_clicks')],
    [State('generated-image-data', 'data')]
)
def score_image(n_clicks, gen_img_data):
    """Score a generated image using vision model as judge."""
    if n_clicks is None or gen_img_data is None:
        return None
    
    try:
        # Decode base64 image
        img_b64 = gen_img_data['image_base64']
        img_bytes = base64.b64decode(img_b64)
        original_prompt = gen_img_data['prompt']
        
        # Score the image
        scores = score_generated_image(
            image_bytes=img_bytes,
            original_prompt=original_prompt
        )
        
        if 'error' in scores:
            return dbc.Alert([
                html.H5("Scoring Failed", className="alert-heading"),
                html.P(scores.get('message', scores['error']))
            ], color="danger", className="mt-3")
        
        # Build scoring display
        judge_name = MODEL_CONFIGS.get(scores.get('judge_model'), {}).get("name", "Claude Sonnet 4")
        
        score_items = []
        for criterion, data in scores.get('scores', {}).items():
            criterion_name = criterion.replace('_', ' ').title()
            score_val = data.get('score', 'N/A')
            rationale = data.get('rationale', 'No rationale provided')
            
            # Color based on score
            if score_val >= 4:
                badge_color = "success"
            elif score_val >= 3:
                badge_color = "warning"
            else:
                badge_color = "danger"
            
            score_items.append(
                html.Div([
                    html.H6([
                        criterion_name,
                        " ",
                        dbc.Badge(f"{score_val}/5", color=badge_color, className="ms-2")
                    ], className="mb-2"),
                    html.P(rationale, className="text-muted small mb-3")
                ])
            )
        
        overall_score = scores.get('overall_score', 'N/A')
        summary = scores.get('summary', '')
        
        return dbc.Card([
            dbc.CardHeader(
                html.H5("⭐ Image Quality Scores (LLM-as-a-Judge)", className="mb-0"),
                className="bg-info text-white"
            ),
            dbc.CardBody([
                html.P([
                    html.Strong("Judge Model: "),
                    judge_name
                ], className="mb-3"),
                html.Hr(),
                html.H5([
                    "Overall Score: ",
                    dbc.Badge(f"{overall_score}/5", color="primary", className="fs-5")
                ], className="mb-3"),
                html.P([
                    html.Strong("Summary: "),
                    summary
                ], className="mb-4"),
                html.Hr(),
                html.H6("Detailed Scores:", className="mb-3"),
                *score_items,
                html.Hr(),
                html.P([
                    html.Small([
                        "💡 ",
                        html.Em("Scoring inspired by MLflow's LLM-as-a-Judge approach")
                    ], className="text-muted")
                ])
            ])
        ], className="mt-3")
        
    except Exception as e:
        return dbc.Alert([
            html.H5("An error occurred", className="alert-heading"),
            html.P(str(e))
        ], color="danger", className="mt-3")


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
