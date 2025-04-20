# LangSmith Monitoring for QA System

This project includes integration with LangSmith for monitoring, tracing, and evaluating LLM calls. LangSmith provides a comprehensive platform for debugging, testing, and monitoring your LLM applications.

## What is LangSmith?

LangSmith is a platform developed by LangChain for:

- **Tracing**: Track inputs, outputs, and intermediate steps of your LLM calls
- **Monitoring**: Monitor performance metrics, costs, and usage patterns
- **Evaluation**: Evaluate model outputs against ground truth or custom criteria
- **Feedback Collection**: Collect user feedback on model outputs

## Setting Up LangSmith

### 1. Sign Up for LangSmith

1. Go to [https://smith.langchain.com/](https://smith.langchain.com/)
2. Sign up for an account
3. Create a new API key from your account settings

### 2. Add Your API Key to .env

Add your LangSmith API key to the `.env` file:

```
LANGCHAIN_API_KEY=your_langsmith_api_key_here
```

Uncomment the line in the `.env` file and replace `your_langsmith_api_key_here` with your actual API key.

### 3. Restart the Application

After adding your API key, restart the application to enable LangSmith monitoring.

## Viewing Traces in LangSmith

Once you've set up LangSmith and made some requests to your QA system:

1. Go to [https://smith.langchain.com/](https://smith.langchain.com/)
2. Navigate to the "Traces" section
3. You should see your requests listed with details about inputs, outputs, and performance metrics

## Customizing Monitoring

The LangSmith integration is implemented in `app/services/langsmith_monitor.py`. You can customize the monitoring by:

- Adding more tags to trace specific types of requests
- Collecting user feedback on responses
- Creating custom evaluations for response quality

## Benefits of LangSmith Monitoring

- **Debugging**: Easily identify and fix issues in your LLM application
- **Performance Tracking**: Monitor latency, token usage, and other metrics
- **Cost Optimization**: Track token usage to optimize costs
- **Quality Assurance**: Evaluate response quality and collect user feedback

## Additional Resources

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangChain Documentation](https://python.langchain.com/docs/langsmith)
- [LangSmith Python SDK](https://github.com/langchain-ai/langsmith-sdk)
