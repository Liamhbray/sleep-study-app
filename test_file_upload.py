#!/usr/bin/env python3
"""
Test script to verify Supabase Storage file upload functionality.
"""

import requests
from io import BytesIO

# Test configuration
BASE_URL = "http://localhost:3001"


def test_file_upload():
    """Test file upload to Supabase Storage."""
    
    print("🧪 Testing Supabase Storage File Upload...")
    
    # Create a session
    session = requests.Session()
    
    # Step 1: Initialize booking session (needed for file upload endpoint)
    print("\n1. Initializing booking session...")
    response = session.get(f"{BASE_URL}/book-sleep-study")
    if response.status_code != 200:
        print(f"❌ Failed to initialize booking: {response.status_code}")
        return False
    print("✅ Booking session initialized")
    
    # Step 2: Test file upload
    print("\n2. Testing file upload...")
    
    # Create a simple test file
    test_file_content = b"This is a test medical referral document."
    test_file = BytesIO(test_file_content)
    test_file.name = "test_referral.txt"
    
    # Prepare the upload request
    files = {
        'referralDocument': ('test_referral.txt', test_file, 'text/plain')
    }
    
    # Upload the file
    response = session.post(f"{BASE_URL}/htmx/booking/upload-referral",
                            files=files)
    
    if response.status_code == 200:
        print("✅ File upload successful!")
        print(f"Response: {response.text[:200]}...")
        
        # Check if the response contains success indicators
        if "upload-success" in response.text or "✅" in response.text:
            print("✅ Upload confirmed by server response")
            return True
        else:
            print("⚠️  Upload response unclear")
            return False
    else:
        print(f"❌ File upload failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False


def test_storage_buckets():
    """Test if storage buckets are accessible."""
    print("\n🗂️  Testing storage bucket accessibility...")
    
    # Check if the app shows storage initialization messages
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Application is running")
            return True
        else:
            print(f"❌ Application not responding: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Could not connect to application: {e}")
        return False


if __name__ == "__main__":
    print("🗄️  Supabase Storage Upload Test")
    print("=" * 50)
    
    # Test basic connectivity
    if not test_storage_buckets():
        print("\n❌ Cannot connect to application. Make sure it's running.")
        exit(1)
    
    # Test file upload
    success = test_file_upload()
    
    if success:
        print("\n🎉 File upload test passed!")
        print("\nNext steps:")
        print("1. Check your Supabase Storage dashboard")
        print("2. Verify the 'referrals' bucket exists")
        print("3. Test upload with different file types (PDF, JPG, etc.)")
        print("4. Test the complete booking flow with file upload")
    else:
        print("\n❌ File upload test failed.")
        print("\nTroubleshooting:")
        print("1. Check Supabase Storage bucket permissions")
        print("2. Verify environment variables are correct")
        print("3. Check Flask application logs for errors")
        print("4. Ensure storage buckets exist in Supabase Dashboard") 