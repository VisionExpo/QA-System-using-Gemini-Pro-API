# Deployment Guide for QA System

This guide provides instructions for deploying the QA System using various methods.

## Prerequisites

Before deploying, make sure you have:

1. A Google API key for the Gemini API
2. An AstraDB account with a token and endpoint
3. (Optional) A LangSmith API key for monitoring

## Option 1: Basic Deployment with Gunicorn

### Step 1: Install Gunicorn

```bash
pip install gunicorn
```

### Step 2: Set Environment Variables

Create a `.env` file with your API keys and configuration:

```
GOOGLE_API_KEY=your_google_api_key
ASTRA_DB_TOKEN=your_astra_token
ASTRA_DB_ENDPOINT=your_astra_endpoint
ASTRA_DB_COLLECTION=qa_system_vectors
LANGCHAIN_API_KEY=your_langsmith_api_key
```

### Step 3: Run with Gunicorn

```bash
gunicorn wsgi:application
```

## Option 2: Docker Deployment

### Step 1: Build the Docker Image

```bash
docker build -t qa-system-gemini .
```

### Step 2: Run the Docker Container

```bash
docker run -p 5000:5000 --env-file .env qa-system-gemini
```

### Step 3: Using Docker Compose

```bash
docker-compose up
```

## Option 3: Heroku Deployment

### Step 1: Install the Heroku CLI

Follow the instructions at [https://devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)

### Step 2: Login to Heroku

```bash
heroku login
```

### Step 3: Create a New Heroku App

```bash
heroku create qa-system-gemini
```

### Step 4: Set Environment Variables

```bash
heroku config:set GOOGLE_API_KEY=your_google_api_key
heroku config:set ASTRA_DB_TOKEN=your_astra_token
heroku config:set ASTRA_DB_ENDPOINT=your_astra_endpoint
heroku config:set ASTRA_DB_COLLECTION=qa_system_vectors
heroku config:set LANGCHAIN_API_KEY=your_langsmith_api_key
```

### Step 5: Deploy to Heroku

```bash
git push heroku main
```

## Option 4: AWS Elastic Beanstalk Deployment

### Step 1: Install the EB CLI

```bash
pip install awsebcli
```

### Step 2: Initialize EB

```bash
eb init -p python-3.10 qa-system-gemini
```

### Step 3: Create an Environment

```bash
eb create qa-system-gemini-env
```

### Step 4: Set Environment Variables

```bash
eb setenv GOOGLE_API_KEY=your_google_api_key ASTRA_DB_TOKEN=your_astra_token ASTRA_DB_ENDPOINT=your_astra_endpoint
```

### Step 5: Deploy the App

```bash
eb deploy
```

## Option 5: Google Cloud Run Deployment

### Step 1: Install the Google Cloud SDK

Follow the instructions at [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)

### Step 2: Initialize gcloud

```bash
gcloud init
```

### Step 3: Set Your Project

```bash
gcloud config set project your-project-id
```

### Step 4: Build and Deploy

```bash
gcloud builds submit --config cloudbuild.yaml
```

## Option 6: AWS Lambda with Zappa

### Step 1: Initialize Zappa

```bash
zappa init
```

This will create a `zappa_settings.json` file (already provided in this repository).

### Step 2: Deploy to Lambda

```bash
zappa deploy dev
```

### Step 3: Update an Existing Deployment

```bash
zappa update dev
```

### Step 4: Set Environment Variables

```bash
zappa manage dev "aws lambda update-function-configuration --function-name qa-system-gemini-dev --environment 'Variables={GOOGLE_API_KEY=your_google_api_key,ASTRA_DB_TOKEN=your_astra_token,ASTRA_DB_ENDPOINT=your_astra_endpoint}'"
```

## Important Considerations

### 1. Environment Variables

Make sure to set all required environment variables for each deployment method:

- `GOOGLE_API_KEY`: Your Google API key for the Gemini API
- `ASTRA_DB_TOKEN`: Your AstraDB token
- `ASTRA_DB_ENDPOINT`: Your AstraDB endpoint
- `ASTRA_DB_COLLECTION`: The name of your AstraDB collection
- `LANGCHAIN_API_KEY`: Your LangSmith API key (optional)

### 2. File Storage

The application stores uploaded files temporarily. For cloud deployments, consider:

- Using cloud storage (S3, GCS) for file uploads
- Implementing a CDN for serving static files
- Setting up proper file cleanup mechanisms

### 3. Scaling

For high-traffic scenarios:

- Configure auto-scaling for your chosen platform
- Consider using a managed database service
- Implement caching for frequently accessed data

### 4. Monitoring

Set up monitoring using:

- LangSmith for LLM monitoring
- CloudWatch (AWS) or Cloud Monitoring (GCP) for application metrics
- Logging solutions like ELK stack or Datadog

### 5. Security

Ensure your deployment is secure:

- Use HTTPS for all traffic
- Implement proper authentication if needed
- Regularly update dependencies
- Follow the principle of least privilege for service accounts

## Troubleshooting

### Common Issues

1. **API Key Issues**: Ensure all API keys are correctly set in environment variables
2. **Memory Limits**: Increase memory allocation for serverless deployments
3. **Timeout Issues**: Increase timeout settings for long-running operations
4. **Cold Start**: For serverless, implement warming strategies
5. **File Upload Limits**: Configure proper limits for file uploads
