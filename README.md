# LLM Monitor

A comprehensive package for monitoring LLM applications and supporting fine-tuning techniques like LoRA and QLoRA.

## Original Application

This project extends the original Gemini application:

- Gemini-pro for text (app.py)
- Gemini-pro-vision for image (vision.py)
- Deployment: [https://qa-system-using-gemini-pro-api-1.onrender.com/](https://qa-system-using-gemini-pro-api-1.onrender.com/)

## Features

- **Custom Logging System**: Advanced logging with different levels and formats
- **LLM Monitoring**: Track latency, token usage, inputs, and outputs
- **Fine-tuning Support**: Tools for LoRA and QLoRA fine-tuning
- **Evaluation Pipeline**: Evaluate and compare model performance
- **Configuration System**: Flexible configuration options

## Project Structure

```plaintext
.
├── .github/workflows/       # GitHub Actions workflows
├── config/                  # Configuration files
├── src/llm_monitor/         # Main package
│   ├── components/          # Core components
│   ├── utils/               # Utility functions
│   ├── config/              # Configuration handling
│   ├── pipeline/            # Processing pipelines
│   ├── entity/              # Data entities
│   └── constants/           # Constants and enums
├── app.py                   # Example application
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
├── params.yaml              # Parameters for DVC
└── dvc.yaml                 # DVC pipeline configuration
```

## Installation

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. For fine-tuning support, install additional dependencies:

   ```bash
   pip install torch transformers datasets peft accelerate bitsandbytes tensorboard
   ```

## Usage

### Running the Application

```bash
streamlit run app.py
```

### Basic Logging

```python
from src.llm_monitor.utils.logger import LLMLogger

# Create a logger
logger = LLMLogger(log_dir="logs", module_name="my_app")

# Log messages
logger.info("Application started")
logger.warning("Warning message")
logger.error("Error message")
```

### Monitoring LLM Models

```python
from src.llm_monitor.components.monitor import LLMMonitor

# Create a monitor
monitor = LLMMonitor(
    model_name="my-model",
    track_latency=True,
    track_tokens=True
)

# Use as a decorator
@monitor.monitor
def get_model_response(prompt):
    # Call your model here
    return model.generate(prompt)

# Get metrics summary
metrics = monitor.get_metrics_summary()
print(metrics)
```
