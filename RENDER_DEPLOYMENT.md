# Deploying QA System to Render

This guide provides step-by-step instructions for deploying the QA System to Render.

## Prerequisites

Before deploying, make sure you have:

1. A [Render account](https://render.com/)
2. A Google API key for the Gemini API
3. An AstraDB account with a token and endpoint
4. (Optional) A LangSmith API key for monitoring

## Deployment Steps

### Option 1: Deploy via GitHub

1. **Fork or Push to GitHub**
   - Make sure your project is in a GitHub repository
   - Ensure all files are committed and pushed
   - Make sure the build.sh script is executable (you may need to run `git update-index --chmod=+x build.sh` before committing)

2. **Create a New Web Service on Render**
   - Log in to your Render dashboard
   - Click "New" and select "Web Service"
   - Connect your GitHub repository
   - Select the repository with your QA System

3. **Configure the Web Service**
   - Name: `qa-system-gemini` (or your preferred name)
   - Environment: `Python 3`
   - Build Command: `./build.sh`
   - Start Command: `gunicorn wsgi:application`

4. **Set Environment Variables**
   - Click on "Environment" and add the following variables:
     - `GOOGLE_API_KEY`: Your Google API key
     - `ASTRA_DB_TOKEN`: Your AstraDB token
     - `ASTRA_DB_ENDPOINT`: Your AstraDB endpoint
     - `ASTRA_DB_COLLECTION`: `qa_system_vectors`
     - `LANGCHAIN_API_KEY`: Your LangSmith API key (optional)
     - `LANGCHAIN_PROJECT`: `qa-system-gemini`
     - `LANGCHAIN_TRACING_V2`: `true`

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application

### Option 2: Deploy via render.yaml (Blueprint)

1. **Push your code to GitHub**
   - Make sure your project with the `render.yaml` file is in a GitHub repository

2. **Deploy via Blueprint**
   - Go to the Render Dashboard
   - Click "New" and select "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file and configure your services

3. **Set Secret Environment Variables**
   - After the initial deployment, you'll need to set the secret environment variables:
     - `GOOGLE_API_KEY`
     - `ASTRA_DB_TOKEN`
     - `ASTRA_DB_ENDPOINT`
     - `LANGCHAIN_API_KEY` (optional)

## Post-Deployment Steps

1. **Verify Deployment**
   - Once deployed, Render will provide a URL for your application
   - Visit the URL to ensure your application is running correctly

2. **Set Up a Custom Domain (Optional)**
   - In your Render dashboard, go to your web service
   - Click on "Settings" and then "Custom Domain"
   - Follow the instructions to set up your custom domain

3. **Monitor Your Application**
   - Use the Render dashboard to monitor your application's logs and metrics
   - Set up LangSmith monitoring by adding your API key

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check the build logs for errors
   - Ensure all dependencies are correctly listed in `requirements.txt`
   - Make sure your Python version is compatible (Render uses Python 3.7 by default)

2. **Runtime Errors**
   - Check the application logs in the Render dashboard
   - Verify that all environment variables are correctly set
   - Ensure your AstraDB instance is accessible from Render

3. **Slow Startup**
   - The first deployment may take longer due to downloading dependencies
   - Sentence transformers models are large and may take time to download

4. **Memory Issues**
   - If you encounter memory issues, consider upgrading your Render plan
   - Optimize your code to reduce memory usage

## Scaling on Render

As your application grows, you can scale your Render service:

1. **Upgrade Plan**
   - Go to your web service in the Render dashboard
   - Click on "Settings" and then "Plan"
   - Choose a plan with more resources

2. **Auto-Scaling**
   - Higher-tier plans support auto-scaling
   - Configure auto-scaling based on your traffic patterns

## Maintaining Your Deployment

1. **Updates**
   - Push changes to your GitHub repository
   - Render will automatically rebuild and deploy your application

2. **Monitoring**
   - Regularly check your application logs
   - Monitor your AstraDB usage
   - Use LangSmith to monitor your LLM usage

3. **Backups**
   - Regularly backup your AstraDB data
   - Consider setting up scheduled backups
