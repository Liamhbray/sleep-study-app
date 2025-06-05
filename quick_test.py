#!/usr/bin/env python3
"""
Quick Sign-In Test
Tests just the authentication part to verify credentials
"""

import requests

# Configuration
BASE_URL = "http://localhost:3001"

def test_signin():
    print("🔐 Quick Sign-In Test")
    print("=" * 30)
    
    # Get credentials from user
    email = input("Enter email: ")
    password = input("Enter password: ")
    
    print(f"\n🧪 Testing sign-in for {email}...")
    
    session = requests.Session()
    
    signin_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = session.post(f"{BASE_URL}/auth/signin", data=signin_data, allow_redirects=False)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 302:
            print("✅ Sign-in successful! (Got redirect)")
            print(f"Redirect location: {response.headers.get('Location', 'Not specified')}")
            
            # Test accessing dashboard
            dashboard_response = session.get(f"{BASE_URL}/dashboard")
            if dashboard_response.status_code == 200:
                print("✅ Dashboard accessible after sign-in")
                print("🎉 Credentials are working correctly!")
                return True
            else:
                print(f"❌ Dashboard access failed: {dashboard_response.status_code}")
                return False
        else:
            print("❌ Sign-in failed")
            if "Invalid credentials" in response.text:
                print("   Reason: Invalid email or password")
            elif "error" in response.text.lower():
                print("   Reason: Authentication error (check Supabase)")
            else:
                print("   Reason: Unknown error")
            
            # Show a snippet of the response
            print(f"   Response preview: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Quick Authentication Test")
    print("=" * 40)
    
    # Check if app is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ App is running on {BASE_URL}")
    except requests.exceptions.RequestException:
        print(f"❌ App is not running on {BASE_URL}")
        print("   Start Flask app: cd sleep-study-app && python3 app.py")
        exit(1)
    
    print()
    success = test_signin()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Update the password in test_booking_flow.py")
        print("2. Run: python test_booking_flow.py")
        print("3. Watch the full end-to-end test!")
    else:
        print("\n💡 Troubleshooting:")
        print("1. Check your email/password combination")
        print("2. Try signing in manually at http://localhost:3001/auth")
        print("3. Make sure your account is verified") 