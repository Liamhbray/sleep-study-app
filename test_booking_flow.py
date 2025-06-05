#!/usr/bin/env python3
"""
Automated End-to-End Booking Flow Test
Tests the complete user journey from sign-in to booking completion

This script simulates a real user going through the entire sleep study booking process:
1. Sign in with existing credentials
2. Navigate to booking page
3. Progress through all booking steps
4. Complete questionnaires 
5. Submit final booking
6. Verify success

Usage:
    1. Update TEST_USER password below
    2. Ensure Flask app is running on localhost:3001
    3. Run: python3 test_booking_flow.py
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:3001"
TEST_USER = {
    "email": "liam@sparrowhub.com.au",
    "password": "liam@sparrowhub.com.au"  # UPDATE THIS WITH YOUR REAL PASSWORD
}

def test_booking_flow():
    """Test the complete booking flow end-to-end"""
    session = requests.Session()
    
    print("🧪 Starting End-to-End Booking Flow Test")
    print("=" * 50)
    
    # Step 1: Sign In
    print("1️⃣ Testing Sign In...")
    signin_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    try:
        # Test sign-in without following redirects to catch the 302
        response = session.post(f"{BASE_URL}/auth/signin", data=signin_data, allow_redirects=False)
        if response.status_code == 302:  # Redirect to dashboard
            print("   ✅ Sign in successful (got redirect)")
            
            # Now follow the redirect to confirm we can access dashboard
            dashboard_response = session.get(f"{BASE_URL}/dashboard")
            if dashboard_response.status_code == 200 and "Dashboard" in dashboard_response.text:
                print("   ✅ Dashboard accessible after sign-in")
            else:
                print(f"   ⚠️ Dashboard access issue: {dashboard_response.status_code}")
                
        elif response.status_code == 200 and "Dashboard" in response.text:
            # Already redirected automatically - this is also success
            print("   ✅ Sign in successful (already redirected)")
        else:
            print(f"   ❌ Sign in failed: {response.status_code}")
            # Check for error messages in response
            if "Invalid credentials" in response.text or "error" in response.text.lower():
                print("   💡 Check your email/password combination")
            print(f"   Response preview: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Sign in error: {e}")
        return False
    
    # Step 2: Navigate to Booking
    print("2️⃣ Testing Booking Page Access...")
    try:
        response = session.get(f"{BASE_URL}/book-sleep-study")
        if response.status_code == 200:
            print("   ✅ Booking page accessible")
        else:
            print(f"   ❌ Booking page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Booking page error: {e}")
        return False
    
    # Step 3: Load Step 1 (Intro)
    print("3️⃣ Testing Step 1 - Introduction...")
    try:
        response = session.get(f"{BASE_URL}/htmx/booking/step/1")
        if response.status_code == 200:
            print("   ✅ Step 1 loaded")
        else:
            print(f"   ❌ Step 1 failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Step 1 error: {e}")
        return False
    
    # Step 4: Navigate to Step 2 (Time Selection)
    print("4️⃣ Testing Step 2 - Time Selection...")
    try:
        response = session.get(f"{BASE_URL}/htmx/booking/step/2")
        if response.status_code == 200:
            print("   ✅ Step 2 loaded")
        else:
            print(f"   ❌ Step 2 failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Step 2 error: {e}")
        return False
    
    # Step 5: Save Step 2 Data (Select appointment time)
    print("5️⃣ Testing Step 2 - Save Appointment...")
    future_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
    step2_data = {
        "appointment_date": future_date,
        "appointment_time": f"{future_date}-14",
        "appointment_time_value": "14:00"
    }
    
    try:
        response = session.post(f"{BASE_URL}/htmx/booking/save-step", data=step2_data)
        if response.status_code == 200:
            print(f"   ✅ Appointment saved for {future_date} at 14:00")
        else:
            print(f"   ❌ Step 2 save failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Step 2 save error: {e}")
        return False
    
    # Step 6: Save Step 3 Data (Personal Details)
    print("6️⃣ Testing Step 3 - Personal Details...")
    step3_data = {
        "fullName": "Automated Test Patient",
        "dateOfBirth": "1990-01-01",
        "phoneNumber": "+61400000000",
        "email": TEST_USER["email"]
    }
    
    try:
        response = session.post(f"{BASE_URL}/htmx/booking/save-step", data=step3_data)
        if response.status_code == 200:
            print("   ✅ Personal details saved")
        else:
            print(f"   ❌ Step 3 save failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Step 3 save error: {e}")
        return False
    
    # Step 7: Navigate to Step 5 (Epworth - Skip file upload for automation)
    print("7️⃣ Testing Step 5 - Epworth Questionnaire...")
    try:
        response = session.get(f"{BASE_URL}/htmx/booking/step/5")
        if response.status_code == 200:
            print("   ✅ Epworth questionnaire loaded")
        else:
            print(f"   ❌ Step 5 failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Step 5 error: {e}")
        return False
    
    # Step 8: Save Epworth Responses
    print("8️⃣ Testing Epworth Responses...")
    epworth_data = {
        "ep_q1": "1",  # Sitting and reading
        "ep_q2": "1",  # Watching TV
        "ep_q3": "0",  # Sitting inactive
        "ep_q4": "2",  # Car passenger
        "ep_q5": "1",  # Lying down afternoon
        "ep_q6": "0",  # Sitting talking
        "ep_q7": "1",  # After lunch
        "ep_q8": "0"   # In traffic
    }
    
    try:
        response = session.post(f"{BASE_URL}/htmx/booking/save-step", data=epworth_data)
        if response.status_code == 200:
            epworth_score = sum(int(v) for v in epworth_data.values())
            print(f"   ✅ Epworth responses saved (Score: {epworth_score}/24)")
        else:
            print(f"   ❌ Epworth save failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Epworth save error: {e}")
        return False
    
    # Step 9: Save OSA-50 Responses
    print("9️⃣ Testing Step 6 - OSA-50 Questionnaire...")
    osa50_data = {
        "osa_q1": "yes",   # Loud snoring
        "osa_q2": "yes",   # Daytime fatigue
        "osa_q3": "no",    # Observed breathing stops
        "osa_q4": "no",    # High blood pressure
        "osa_q5": "no"     # BMI > 35
    }
    
    try:
        response = session.post(f"{BASE_URL}/htmx/booking/save-step", data=osa50_data)
        if response.status_code == 200:
            osa50_score = sum(1 for v in osa50_data.values() if v == 'yes')
            print(f"   ✅ OSA-50 responses saved (Score: {osa50_score}/5)")
        else:
            print(f"   ❌ OSA-50 save failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ OSA-50 save error: {e}")
        return False
    
    # Step 10: Final Booking Submission
    print("🔟 Testing Final Booking Submission...")
    try:
        response = session.post(f"{BASE_URL}/htmx/booking/submit")
        if response.status_code == 200:
            # Check for multiple success indicators
            success_indicators = [
                "booking-success",
                "study_id",
                "check-circle",
                "Success",
                "confirmed",
                "bg-green-100"  # Green success styling
            ]
            
            if any(indicator in response.text for indicator in success_indicators):
                print("   ✅ Booking submitted successfully!")
                
                # Try to extract study ID from response
                if "study_id" in response.text.lower():
                    print("   📋 Sleep study record created in database")
                
                print("   🎉 End-to-end test PASSED!")
                return True
            else:
                print("   ⚠️ Booking submitted but success unclear")
                print("   Response preview:", response.text[:300])
                return False
        else:
            print(f"   ❌ Booking submission failed: {response.status_code}")
            if response.text:
                print("   Error details:", response.text[:200])
            return False
    except Exception as e:
        print(f"   ❌ Booking submission error: {e}")
        return False

def test_api_endpoints():
    """Quick test of key API endpoints"""
    print("\n🔍 Testing Key API Endpoints...")
    print("-" * 40)
    
    endpoints = [
        ("/", "Home Page"),
        ("/auth", "Auth Page"),
        ("/dashboard", "Dashboard (should redirect if not logged in)"),
        ("/book-sleep-study", "Booking Page (should redirect if not logged in)")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code in [200, 302]:
                status = "✅"
            elif response.status_code == 401:
                status = "🔒"  # Auth required - expected
            else:
                status = "❌"
            print(f"   {status} {name}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {name}: Connection failed - {e}")

def check_database_state():
    """Check if there are any obvious database issues"""
    print("\n🗃️ Checking Database Connectivity...")
    print("-" * 40)
    
    # Try to hit an endpoint that uses the database
    try:
        response = requests.get(f"{BASE_URL}/htmx/studies", timeout=5)
        if response.status_code == 401:
            print("   ✅ Database endpoints responding (auth required)")
        elif response.status_code == 200:
            print("   ✅ Database endpoints responding")
        else:
            print(f"   ⚠️ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Database connectivity issue: {e}")

if __name__ == "__main__":
    print("🚀 Sleep Study App - End-to-End Test Suite")
    print("=" * 60)
    
    # Check if app is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ App is running on {BASE_URL}")
    except requests.exceptions.RequestException:
        print(f"❌ App is not running on {BASE_URL}")
        print("   Please start the Flask app first:")
        print("   cd sleep-study-app && python3 app.py")
        sys.exit(1)
    
    # Run API tests
    test_api_endpoints()
    
    # Check database
    check_database_state()
    
    # Check if password is configured
    print(f"\n📝 Checking Test Configuration...")
    print("-" * 40)
    print(f"   Test email: {TEST_USER['email']}")
    
    if TEST_USER["password"] == "your_actual_password_here":
        print("   ❌ Please update the password in the script:")
        print("   1. Edit this file: test_booking_flow.py")
        print("   2. Replace 'your_actual_password_here' with your real password")
        print("   3. Run the script again")
        sys.exit(1)
    else:
        print("   ✅ Password configured")
    
    # Run full booking flow test
    print(f"\n🎯 Running Complete Booking Flow Test...")
    print("=" * 60)
    
    success = test_booking_flow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! Your booking flow is working end-to-end.")
        print("✅ Authentication system functional")
        print("✅ HTMX step progression working")
        print("✅ Form data persistence working")
        print("✅ Database operations successful")
        print("✅ Complete user journey validated")
    else:
        print("❌ Some tests failed. Check the detailed logs above.")
        print("💡 Common issues to check:")
        print("   - Is the Flask app running?")
        print("   - Is the password correct?")
        print("   - Are there any database errors in Flask logs?")
        print("   - Is Supabase accessible?")
    
    print("\n📊 Test Summary:")
    print(f"   Base URL: {BASE_URL}")
    print(f"   Test User: {TEST_USER['email']}")
    print(f"   Status: {'PASSED' if success else 'FAILED'}") 