"""
Test Google Vertex AI with aisuite

This script verifies that Google Vertex AI is correctly configured
and can be used with aisuite library.

Prerequisites:
1. Google Cloud account with billing enabled
2. Project created with Vertex AI API enabled
3. Service account created with appropriate permissions
4. Environment variables set:
   - GOOGLE_PROJECT_ID
   - GOOGLE_REGION
   - GOOGLE_APPLICATION_CREDENTIALS
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()


def check_environment_variables():
    """Check if all required environment variables are set"""
    print("🔍 Checking Environment Variables")
    print("=" * 60)
    
    required_vars = {
        "GOOGLE_PROJECT_ID": "Your Google Cloud Project ID",
        "GOOGLE_REGION": "Your preferred Google Cloud region",
        "GOOGLE_APPLICATION_CREDENTIALS": "Path to service account JSON file"
    }
    
    all_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if var == "GOOGLE_APPLICATION_CREDENTIALS":
                print(f"✅ {var}: {value}")
                if os.path.exists(value):
                    print(f"   ✅ Credentials file exists")
                else:
                    print(f"   ❌ Credentials file does not exist")
                    all_set = False
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            print(f"   Description: {description}")
            all_set = False
    
    return all_set


def check_vertexai_installation():
    """Check if vertexai package is installed"""
    print("\n🔍 Checking Vertex AI SDK Installation")
    print("=" * 60)
    
    try:
        import vertexai
        print(f"✅ vertexai package is installed (version: {vertexai.__version__})")
        return True
    except ImportError:
        print("❌ vertexai package is not installed")
        print("   Install with: pip install vertexai")
        return False


def check_aisuite_installation():
    """Check if aisuite package is installed"""
    print("\n🔍 Checking aisuite Installation")
    print("=" * 60)
    
    try:
        import aisuite as ai
        print("✅ aisuite package is installed")
        return True
    except ImportError:
        print("❌ aisuite package is not installed")
        print("   Install with: pip install aisuite")
        return False


def test_vertex_ai_simple():
    """Test Vertex AI with a simple chat completion"""
    print("\n🧪 Testing Vertex AI with Simple Chat Completion")
    print("=" * 60)
    
    try:
        import aisuite as ai
        
        client = ai.Client()
        
        model = "google:gemini-2.0-flash-exp"
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Respond concisely."},
            {"role": "user", "content": "Say 'Hello from Vertex AI!' in one sentence."},
        ]
        
        print(f"📤 Sending request to {model}...")
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        
        print("✅ Successfully received response from Vertex AI")
        print(f"📥 Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to call Vertex AI: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print(f"\n   Traceback:\n{traceback.format_exc()}")
        return str(e)  # Return error message instead of False


def test_vertex_ai_with_system_prompt():
    """Test Vertex AI with a system prompt"""
    print("\n🧪 Testing Vertex AI with System Prompt")
    print("=" * 60)
    
    try:
        import aisuite as ai
        
        client = ai.Client()
        
        model = "google:gemini-2.0-flash-exp"
        
        messages = [
            {"role": "system", "content": "Respond in Pirate English."},
            {"role": "user", "content": "Tell me a joke."},
        ]
        
        print(f"📤 Sending request to {model} with Pirate English system prompt...")
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.8
        )
        
        print("✅ Successfully received response from Vertex AI")
        print(f"📥 Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to call Vertex AI: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False


def test_vertex_ai_models():
    """Test different Vertex AI models"""
    print("\n🧪 Testing Different Vertex AI Models")
    print("=" * 60)
    
    models = [
        "google:gemini-2.0-flash-exp",
    ]
    
    results = {}
    
    for model in models:
        print(f"\n📤 Testing {model}...")
        try:
            import aisuite as ai
            
            client = ai.Client()
            
            messages = [
                {"role": "user", "content": "Say hello in one word."},
            ]
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.5
            )
            
            print(f"   ✅ {model}: {response.choices[0].message.content}")
            results[model] = True
            
        except Exception as e:
            print(f"   ❌ {model}: {e}")
            results[model] = False
    
    return all(results.values())


def print_setup_instructions():
    """Print setup instructions for Vertex AI"""
    print("\n" + "=" * 60)
    print("📚 Google Vertex AI Setup Instructions")
    print("=" * 60)
    print("""
1. Create a Google Cloud Account and Project:
   - Visit https://cloud.google.com/
   - Create a new project
   - Enable billing for the project

2. Enable Vertex AI API:
   - Go to APIs & Services > Library
   - Search for "Vertex AI API"
   - Click "Enable"

3. Create a Service Account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Grant "Vertex AI User" role
   - Create and download JSON key

4. Set Environment Variables in .env:
   GOOGLE_PROJECT_ID=your-project-id
   GOOGLE_REGION=asia-northeast1
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

5. Install Required Packages:
   pip install vertexai aisuite

6. Run this test again to verify setup
""")


def main():
    print("🧪 Google Vertex AI Configuration Test (with aisuite)")
    print("=" * 60)
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    # Check package installations
    vertexai_ok = check_vertexai_installation()
    aisuite_ok = check_aisuite_installation()
    
    # If prerequisites are not met, show setup instructions
    if not (env_ok and vertexai_ok and aisuite_ok):
        print("\n⚠️  Prerequisites not met. Please complete the setup first.")
        print_setup_instructions()
        return 1
    
    # Run tests
    simple_test_ok = test_vertex_ai_simple()
    system_prompt_test_ok = test_vertex_ai_with_system_prompt()
    models_test_ok = test_vertex_ai_models()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Environment Variables: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"Vertex AI SDK: {'✅ PASS' if vertexai_ok else '❌ FAIL'}")
    print(f"aisuite Library: {'✅ PASS' if aisuite_ok else '❌ FAIL'}")
    print(f"Simple Chat Completion: {'✅ PASS' if simple_test_ok else '❌ FAIL'}")
    print(f"System Prompt Test: {'✅ PASS' if system_prompt_test_ok else '❌ FAIL'}")
    print(f"Multiple Models Test: {'✅ PASS' if models_test_ok else '❌ FAIL'}")
    
    if all([env_ok, vertexai_ok, aisuite_ok, simple_test_ok, system_prompt_test_ok, models_test_ok]):
        print("\n🎉 All tests passed! Google Vertex AI is ready to use with aisuite.")
        print("\n💡 You can now use Vertex AI in your agents:")
        print("   Set ACTIVE_MODEL=google:gemini-2.0-flash-exp in .env")
        print("   Or use model='google:gemini-2.0-flash-exp' in your code")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
        
        # Check for common issues
        if not simple_test_ok:
            # Get error message from the test result
            error_msg = ""
            if hasattr(simple_test_ok, '__str__'):
                error_msg = str(simple_test_ok)
            elif isinstance(simple_test_ok, str):
                error_msg = simple_test_ok
            else:
                error_msg = "Unknown error"
            
            if "DNS resolution failed" in error_msg:
                print("\n🌐 Network/DNS Issue Detected")
                print("=" * 60)
                print("The Vertex AI endpoint cannot be reached due to DNS resolution failure.")
                print("This could be caused by:")
                print("  - Network firewall or proxy settings")
                print("  - VPN or corporate network restrictions")
                print("  - DNS configuration issues")
                print("\n💡 Alternative: Use Google Gemini API (REST) instead")
                print("   Run: python examples/test_google_gemini.py")
                print("   This uses direct REST API calls without Vertex AI SDK")
                
            elif "SERVICE_DISABLED" in error_msg or "Vertex AI API has not been used" in error_msg:
                print("\n🔧 Vertex AI API Not Enabled")
                print("=" * 60)
                print("The Vertex AI API is not enabled in your Google Cloud project.")
                print("\n📝 To fix this:")
                print("1. Visit the Google Cloud Console:")
                print("   https://console.developers.google.com/apis/api/aiplatform.googleapis.com/overview")
                print(f"   Make sure you're in project: {os.getenv('GOOGLE_PROJECT_ID')}")
                print("2. Click 'Enable API'")
                print("3. Wait a few minutes for the changes to propagate")
                print("4. Run this test again")
                print("\n💡 Alternative: Use Google Gemini API (REST) instead")
                print("   Run: python examples/test_google_gemini.py")
                print("   This uses direct REST API calls without requiring Vertex AI setup")
                
            elif "BILLING_DISABLED" in error_msg or "billing to be enabled" in error_msg:
                print("\n💳 Billing Not Enabled")
                print("=" * 60)
                print("Vertex AI requires billing to be enabled on your Google Cloud project.")
                print("\n📝 To fix this:")
                print("1. Visit the Google Cloud Billing Console:")
                print("   https://console.developers.google.com/billing/enable")
                print(f"   Make sure you're in project: {os.getenv('GOOGLE_PROJECT_ID')}")
                print("2. Enable billing for your project")
                print("3. Add a payment method (credit card)")
                print("4. Wait a few minutes for billing to be activated")
                print("5. Run this test again")
                print("\n⚠️  Note: Vertex AI charges per API call")
                print("   Check pricing: https://cloud.google.com/vertex-ai/pricing")
                print("\n💡 Alternative: Use Google Gemini API (REST) instead")
                print("   Run: python examples/test_google_gemini.py")
                print("   This uses direct REST API calls with free tier available")
                
            else:
                print("\n⚠️  Unknown Error")
                print("=" * 60)
                print("Please check the error details above.")
                print("\n💡 Alternative: Use Google Gemini API (REST) instead")
                print("   Run: python examples/test_google_gemini.py")
        
        if not env_ok:
            print_setup_instructions()
        return 1


if __name__ == "__main__":
    sys.exit(main())

