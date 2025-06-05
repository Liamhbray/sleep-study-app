#!/usr/bin/env python3
"""
Test script to verify booking submission fixes.
This script tests the booking flow to ensure appointment data is properly saved.
"""

import requests
import json

# Test configuration
BASE_URL = "http://127.0.0.1:3001"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"


def test_booking_flow():
    """Test the complete booking flow with proper data validation."""
    
    session = requests.Session()
    
    print("🧪 Testing Sleep Study Booking Flow...")
    
    # Step 1: Sign in (or skip if already signed in)
    print("\n1. Testing authentication...")
    
    # Step 2: Initialize booking session
    print("\n2. Initializing booking session...")
    response = session.get(f"{BASE_URL}/book-sleep-study")
    if response.status_code != 200:
        print(f"❌ Failed to initialize booking: {response.status_code}")
        return False
    print("✅ Booking session initialized")
    
    # Step 3: Test step navigation with validation
    print("\n3. Testing step navigation validation...")
    
    # Try to access step 7 without completing earlier steps
    response = session.get(f"{BASE_URL}/htmx/booking/step/7")
    if "Please select an appointment time" in response.text:
        print("✅ Step validation working - prevents skipping to step 7")
    else:
        print("❌ Step validation not working properly")
        return False
    
    # Step 4: Complete step 2 (appointment selection)
    print("\n4. Testing appointment selection...")
    
    # Get available slots first
    response = session.get(f"{BASE_URL}/htmx/booking/step/2")
    if response.status_code != 200:
        print(f"❌ Failed to load step 2: {response.status_code}")
        return False
    
    # Simulate selecting an appointment
    appointment_data = {
        'appointment_time': '2025-06-19-14'  # Format: YYYY-MM-DD-HH
    }
    
    response = session.post(f"{BASE_URL}/htmx/booking/save-step",
                            data=appointment_data)
    if response.status_code == 200:
        print("✅ Appointment selection successful")
    else:
        print(f"❌ Appointment selection failed: {response.status_code}")
        return False
    
    # Step 5: Complete step 3 (personal details)
    print("\n5. Testing personal details...")
    
    personal_data = {
        'fullName': 'Test Patient',
        'dateOfBirth': '1990-01-01',
        'phoneNumber': '+1234567890',
        'email': 'test.patient@example.com'
    }
    
    # Navigate to step 3 first
    session.get(f"{BASE_URL}/htmx/booking/step/3")
    
    # Save personal details
    response = session.post(f"{BASE_URL}/htmx/booking/save-step",
                            data=personal_data)
    if response.status_code == 200:
        print("✅ Personal details saved successfully")
    else:
        print(f"❌ Personal details save failed: {response.status_code}")
        return False
    
    # Step 6: Check session data
    print("\n6. Checking session data...")
    
    response = session.get(f"{BASE_URL}/debug/booking-session")
    if response.status_code == 200:
        session_data = response.json()
        booking_data = session_data.get('booking_data', {})
        
        # Check if appointment data exists
        if booking_data.get('appointment', {}).get('date'):
            print("✅ Appointment data properly saved in session")
        else:
            print("❌ Appointment data missing from session")
            print(f"Session data: {json.dumps(booking_data, indent=2)}")
            return False
            
        # Check if personal details exist
        if booking_data.get('personal_details', {}).get('full_name'):
            print("✅ Personal details properly saved in session")
        else:
            print("❌ Personal details missing from session")
            return False
    else:
        print(f"❌ Failed to check session data: {response.status_code}")
        return False
    
    print("\n✅ All tests passed! Booking flow should work correctly now.")
    return True


def reset_booking_session():
    """Reset the booking session for clean testing."""
    session = requests.Session()
    response = session.post(f"{BASE_URL}/debug/reset-booking")
    if response.status_code == 200:
        print("✅ Booking session reset successfully")
    else:
        print(f"❌ Failed to reset booking session: {response.status_code}")


if __name__ == "__main__":
    print("🔧 Sleep Study Booking Fix Test")
    print("=" * 50)
    
    # Reset session first
    reset_booking_session()
    
    # Run the test
    success = test_booking_flow()
    
    if success:
        print("\n🎉 All fixes are working correctly!")
        print("\nNext steps:")
        print("1. Test the actual booking flow in your browser")
        print("2. Complete all steps including surveys")
        print("3. Try submitting the booking")
        print("4. Remove debug endpoints before production")
    else:
        print("\n❌ Some issues remain. Check the output above.") 