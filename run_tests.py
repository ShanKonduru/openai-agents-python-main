"""
Test Runner for Content Creation API
Simple script to run all tests
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests for the content creation system"""
    print("🧪 Running Content Creation API Tests")
    print("=" * 50)
    
    # Check if pytest is installed
    try:
        import pytest
        print("✅ pytest is available")
    except ImportError:
        print("❌ pytest not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio"])
        print("✅ pytest installed")
    
    # Check if required test dependencies are available
    try:
        import httpx
        print("✅ httpx is available")
    except ImportError:
        print("❌ httpx not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "httpx"])
        print("✅ httpx installed")
    
    print("\n📋 Running Test Suites:")
    print("-" * 30)
    
    # Test files to run
    test_files = [
        "test_real_api_server.py",
        "test_openai.py",
        "test_agents.py"
    ]
    
    results = {}
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n🔍 Running {test_file}...")
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pytest", 
                    test_file, "-v", "--tb=short"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ {test_file} - PASSED")
                    results[test_file] = "PASSED"
                else:
                    print(f"❌ {test_file} - FAILED")
                    results[test_file] = "FAILED"
                    if result.stdout:
                        print("STDOUT:", result.stdout[-500:])  # Last 500 chars
                    if result.stderr:
                        print("STDERR:", result.stderr[-500:])  # Last 500 chars
                        
            except Exception as e:
                print(f"💥 {test_file} - ERROR: {e}")
                results[test_file] = "ERROR"
        else:
            print(f"⚠️  {test_file} - NOT FOUND")
            results[test_file] = "NOT FOUND"
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 30)
    
    passed = sum(1 for result in results.values() if result == "PASSED")
    failed = sum(1 for result in results.values() if result == "FAILED")
    errors = sum(1 for result in results.values() if result == "ERROR")
    not_found = sum(1 for result in results.values() if result == "NOT FOUND")
    
    for test_file, result in results.items():
        icon = "✅" if result == "PASSED" else "❌" if result == "FAILED" else "💥" if result == "ERROR" else "⚠️"
        print(f"{icon} {test_file}: {result}")
    
    print(f"\n📈 Total: {len(results)} test files")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"💥 Errors: {errors}")
    print(f"⚠️  Not Found: {not_found}")
    
    if failed == 0 and errors == 0:
        print("\n🎉 All tests completed successfully!")
        return True
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return False

def run_quick_api_test():
    """Run a quick API connectivity test"""
    print("\n🚀 Quick API Test")
    print("-" * 20)
    
    try:
        # Test OpenAI connectivity
        print("🔍 Testing OpenAI API connectivity...")
        result = subprocess.run([sys.executable, "test_openai.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ OpenAI API test passed")
        else:
            print("❌ OpenAI API test failed")
            if result.stdout:
                print("Output:", result.stdout[-300:])
            if result.stderr:
                print("Error:", result.stderr[-300:])
    
    except Exception as e:
        print(f"💥 Quick test error: {e}")

if __name__ == "__main__":
    print("🧪 Content Creation System Test Suite")
    print("🔧 Testing API endpoints and functionality")
    print()
    
    # Run quick test first
    run_quick_api_test()
    
    # Run full test suite
    success = run_tests()
    
    if success:
        print("\n🎯 Ready for deployment!")
        sys.exit(0)
    else:
        print("\n🔧 Please fix the failing tests before deployment.")
        sys.exit(1)