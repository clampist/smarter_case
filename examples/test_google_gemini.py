"""
Test Google Gemini API Configuration

This script verifies that Google Gemini API is correctly configured
and can be used with aisuite.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

def test_google_api_key():
    """Test if Google API key is configured"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print("✅ GOOGLE_API_KEY is configured")
        print(f"   Key: {api_key[:10]}...{api_key[-4:]}")
        return True
    else:
        print("❌ GOOGLE_API_KEY is not configured")
        return False

def test_google_cloud_config():
    """Test if Google Cloud configuration is set up"""
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    region = os.getenv("GOOGLE_REGION")
    credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    all_configured = True
    
    if project_id:
        print(f"✅ GOOGLE_PROJECT_ID: {project_id}")
    else:
        print("❌ GOOGLE_PROJECT_ID is not configured")
        all_configured = False
    
    if region:
        print(f"✅ GOOGLE_REGION: {region}")
    else:
        print("❌ GOOGLE_REGION is not configured")
        all_configured = False
    
    if credentials:
        print(f"✅ GOOGLE_APPLICATION_CREDENTIALS: {credentials}")
        if os.path.exists(credentials):
            print("   ✅ Credentials file exists")
        else:
            print("   ❌ Credentials file does not exist")
            all_configured = False
    else:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS is not configured")
        all_configured = False
    
    return all_configured

def test_google_rest_api():
    """Test Google Gemini API directly via REST"""
    try:
        import requests
        print("\n🧪 Testing Google Gemini via REST API...")
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found")
            return False
        
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}'
        
        data = {
            'contents': [{
                'parts': [{'text': 'Say Hello from Gemini in one sentence.'}]
            }]
        }
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            print("✅ Successfully called Google Gemini REST API")
            print(f"   Response: {text}")
            return True
        else:
            print(f"❌ Failed to call Google Gemini REST API")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
    except ImportError as e:
        print(f"❌ Failed to import requests: {e}")
        print("   Install with: pip install requests")
        return False
    except Exception as e:
        print(f"❌ Failed to call Google Gemini REST API: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def main():
    print("🧪 Google Gemini Configuration Test")
    print("=" * 60)
    
    print("\n1. Testing Google API Key Configuration")
    print("-" * 60)
    api_key_ok = test_google_api_key()
    
    print("\n2. Testing Google Cloud Configuration")
    print("-" * 60)
    cloud_config_ok = test_google_cloud_config()
    
    print("\n3. Testing Google Gemini REST API")
    print("-" * 60)
    rest_api_ok = test_google_rest_api()
    
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Google API Key: {'✅ PASS' if api_key_ok else '❌ FAIL'}")
    print(f"Google Cloud Config: {'✅ PASS' if cloud_config_ok else '⚠️  OPTIONAL'}")
    print(f"Google Gemini REST API: {'✅ PASS' if rest_api_ok else '❌ FAIL'}")
    
    if api_key_ok and rest_api_ok:
        print("\n🎉 All tests passed! Google Gemini is ready to use.")
        print("\n📝 Configuration Summary:")
        print("✅ Google API Key is configured and working")
        print("✅ Google Gemini REST API is accessible")
        if cloud_config_ok:
            print("✅ Google Cloud (Vertex AI) configuration is complete")
        else:
            print("⚠️  Google Cloud (Vertex AI) configuration is optional")
        print("\n💡 You can now use Google Gemini in your agents!")
        print("   Set ACTIVE_MODEL=google:gemini-2.0-flash-exp in .env")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please check your configuration.")
        print("\n📝 Configuration Notes:")
        print("1. Make sure GOOGLE_API_KEY is set in .env file")
        print("2. For Vertex AI (optional), also set:")
        print("   - GOOGLE_PROJECT_ID")
        print("   - GOOGLE_REGION")
        print("   - GOOGLE_APPLICATION_CREDENTIALS")
        print("3. Install required packages: pip install requests")
        return 1

if __name__ == "__main__":
    sys.exit(main())

