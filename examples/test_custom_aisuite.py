"""
Test Custom aisuite with Google REST API Support

This script tests the custom aisuite implementation that supports
Google REST API directly without requiring Vertex AI setup.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()


def test_custom_aisuite_google_rest():
    """Test custom aisuite with Google REST API"""
    print("🧪 Testing Custom aisuite with Google REST API")
    print("=" * 60)
    
    try:
        import aisuite as ai
        print("✅ Custom aisuite imported successfully")
        
        # Test basic client creation
        client = ai.Client()
        print("✅ aisuite Client created successfully")
        
        # Test with Google REST API model
        model = "google_rest:gemini-2.5-flash"
        print(f"📤 Testing with model: {model}")
        
        messages = [
            {"role": "user", "content": "Say 'Hello from Custom aisuite!' in one sentence."},
        ]
        
        print("📤 Sending request to Google REST API via custom aisuite...")
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        
        print("✅ Successfully received response from Google REST API")
        print(f"📥 Response: {response.choices[0].message.content}")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import custom aisuite: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to call Google REST API via custom aisuite: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False


def test_custom_aisuite_system_prompt():
    """Test custom aisuite with system prompt"""
    print("\n🧪 Testing Custom aisuite with System Prompt")
    print("=" * 60)
    
    try:
        import aisuite as ai
        
        client = ai.Client()
        
        model = "google_rest:gemini-2.5-flash"
        
        messages = [
            {"role": "system", "content": "You are a helpful coding assistant. Respond concisely."},
            {"role": "user", "content": "What is the capital of France?"},
        ]
        
        print(f"📤 Sending request to {model} with system prompt...")
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.5
        )
        
        print("✅ Successfully received response from custom aisuite")
        print(f"📥 Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to call Google REST API via custom aisuite: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False


def test_custom_aisuite_models():
    """Test different models with custom aisuite"""
    print("\n🧪 Testing Different Models with Custom aisuite")
    print("=" * 60)
    
    models = [
        "google_rest:gemini-2.5-flash",  # Latest free model        
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
    
    return results


def test_agent_integration():
    """Test integration with our agents"""
    print("\n🧪 Testing Agent Integration with Custom aisuite")
    print("=" * 60)
    
    try:
        from src.agents.simple_agents import code_analysis_agent
        
        print("📤 Testing code analysis agent with custom aisuite...")
        
        result = code_analysis_agent(
            commit_hash="test123",
            branch="main",
            model="google_rest:gemini-2.5-flash"
        )
        
        if result['status'] == 'completed':
            print("✅ Agent integration successful")
            print(f"📥 Agent output: {result['output'][:200]}...")
            return True
        else:
            print(f"❌ Agent failed: {result['status']}")
            return False
        
    except Exception as e:
        print(f"❌ Agent integration failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False


def main():
    print("🧪 Custom aisuite with Google REST API Test")
    print("=" * 60)
    
    print("\n📋 Test Summary:")
    print("- Custom aisuite installation and import")
    print("- Google REST API integration")
    print("- System prompt handling")
    print("- Multiple model support")
    print("- Agent integration")
    
    # Run tests
    basic_test_ok = test_custom_aisuite_google_rest()
    system_prompt_test_ok = test_custom_aisuite_system_prompt()
    models_test_results = test_custom_aisuite_models()
    agent_test_ok = test_agent_integration()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Basic Google REST API Test: {'✅ PASS' if basic_test_ok else '❌ FAIL'}")
    print(f"System Prompt Test: {'✅ PASS' if system_prompt_test_ok else '❌ FAIL'}")
    print(f"Multiple Models Test: {'✅ PASS' if all(models_test_results.values()) else '❌ FAIL'}")
    print(f"Agent Integration Test: {'✅ PASS' if agent_test_ok else '❌ FAIL'}")
    
    # Show model results
    print("\n📋 Model Test Results:")
    for model, success in models_test_results.items():
        print(f"  {model}: {'✅ PASS' if success else '❌ FAIL'}")
    
    if all([basic_test_ok, system_prompt_test_ok, agent_test_ok]) and all(models_test_results.values()):
        print("\n🎉 All tests passed! Custom aisuite with Google REST API is working perfectly!")
        print("\n💡 Benefits of your custom aisuite:")
        print("✅ Direct Google REST API support")
        print("✅ No Vertex AI setup required")
        print("✅ No billing configuration needed")
        print("✅ Simplified integration")
        print("✅ Better error handling")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
