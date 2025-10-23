# Google Gemini Setup Guide

This guide explains two ways to use Google Gemini with the Smarter Case project.

## Overview

There are two methods to integrate Google Gemini:

1. **Google Gemini API (REST)** - Simpler, uses API key only
2. **Google Vertex AI** - Enterprise solution, requires Google Cloud setup

## Method 1: Google Gemini API (REST) ⭐ Recommended for Quick Start

### Prerequisites

- Google API Key

### Setup Steps

1. **Get Google API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Click "Create API Key"
   - Copy the API key

2. **Configure Environment Variables**
   
   Add to `.env` file:
   ```bash
   GOOGLE_API_KEY=your-api-key-here
   ```

3. **Test Configuration**
   ```bash
   python examples/test_google_gemini.py
   ```

### Usage

The REST API method works without additional Google Cloud setup:

```python
from src.agents.simple_agents import code_analysis_agent

# Use Google Gemini via REST API
result = code_analysis_agent(
    commit_hash="abc123",
    model="google:gemini-2.0-flash-exp"
)
```

### Advantages

- ✅ Simple setup (only API key needed)
- ✅ No Google Cloud project required
- ✅ No billing setup needed
- ✅ Works in restricted network environments
- ✅ Direct REST API calls

### Limitations

- ❌ No enterprise features
- ❌ No custom model tuning
- ❌ Rate limits may be lower

## Method 2: Google Vertex AI (Enterprise)

### Prerequisites

- Google Cloud account with billing enabled
- Google Cloud project
- Service account with Vertex AI permissions

### Setup Steps

1. **Create Google Cloud Account and Project**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable billing for the project

2. **Enable Vertex AI API**
   - Go to APIs & Services > Library
   - Search for "Vertex AI API"
   - Click "Enable"

3. **Create Service Account**
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Name: `smarter-case` (or your preferred name)
   - Grant role: "Vertex AI User"
   - Click "Create and Continue"
   - Click "Done"

4. **Create and Download JSON Key**
   - Click on the service account you just created
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Choose "JSON" format
   - Click "Create" (file will download automatically)
   - Move the JSON file to your project directory

5. **Configure Environment Variables**
   
   Add to `.env` file:
   ```bash
   GOOGLE_PROJECT_ID=your-project-id
   GOOGLE_REGION=asia-northeast1
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
   ```

6. **Install Vertex AI SDK**
   ```bash
   pip install vertexai
   ```

7. **Test Configuration**
   ```bash
   python examples/test_google_vertex_ai.py
   ```

### Usage

```python
import aisuite as ai

client = ai.Client()

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Analyze this code change."},
]

response = client.chat.completions.create(
    model="google:gemini-1.5-flash",
    messages=messages,
)

print(response.choices[0].message.content)
```

### Advantages

- ✅ Enterprise-grade features
- ✅ Custom model tuning
- ✅ Higher rate limits
- ✅ Better SLA and support
- ✅ Integration with other Google Cloud services

### Limitations

- ❌ Complex setup
- ❌ Requires Google Cloud billing
- ❌ May have network/firewall issues
- ❌ Requires service account management

## Troubleshooting

### DNS Resolution Failed (Vertex AI)

If you see this error:
```
DNS resolution failed for asia-northeast1-aiplatform.googleapis.com:443
```

**Possible causes:**
- Network firewall blocking Google Cloud endpoints
- VPN or corporate proxy restrictions
- DNS configuration issues

**Solutions:**
1. Use Method 1 (REST API) instead
2. Check firewall/proxy settings
3. Try a different network
4. Contact your network administrator

### API Key Not Working (REST API)

If you see authentication errors:

**Solutions:**
1. Verify API key is correct in `.env`
2. Check if API key has proper permissions
3. Ensure API key is not expired
4. Try generating a new API key

### Region Not Supported (Vertex AI)

If you see "Unsupported region" error:

**Supported regions:**
- `us-central1`
- `us-east1`
- `us-west1`
- `europe-west1`
- `europe-west4`
- `asia-northeast1`
- `asia-southeast1`

Update `GOOGLE_REGION` in `.env` to a supported region.

## Comparison Table

| Feature | REST API | Vertex AI |
|---------|----------|-----------|
| Setup Complexity | ⭐ Simple | ⭐⭐⭐ Complex |
| Cost | Free tier available | Pay-as-you-go |
| Network Requirements | Minimal | Requires Google Cloud access |
| Enterprise Features | Limited | Full |
| Rate Limits | Standard | Higher |
| Best For | Development, Testing | Production, Enterprise |

## Recommendation

- **For Development/Testing**: Use Method 1 (REST API)
- **For Production**: Use Method 2 (Vertex AI) if you need enterprise features
- **For Quick Start**: Use Method 1 (REST API)

## Current Project Status

✅ **Method 1 (REST API)** - Fully configured and tested
⚠️  **Method 2 (Vertex AI)** - Configured but may have network restrictions

You can use either method depending on your needs. The project defaults to mock mode for testing without requiring any API keys.

## Setting Active Model

To use Google Gemini as the default model, add to `.env`:

```bash
# For REST API
ACTIVE_MODEL=google:gemini-2.0-flash-exp

# For Vertex AI
ACTIVE_MODEL=google:gemini-1.5-flash
```

Or specify the model in your code:

```python
from src.agents.simple_agents import code_analysis_agent

result = code_analysis_agent(
    commit_hash="abc123",
    model="google:gemini-2.0-flash-exp"  # REST API
    # or
    # model="google:gemini-1.5-flash"  # Vertex AI
)
```

