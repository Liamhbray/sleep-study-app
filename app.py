#!/usr/bin/env python3
"""
HTMX Sleep Study Management System
Flask backend with Supabase integration

Following https://github.com/henrygrant/htmx-supabase-auth-example pattern

A comprehensive healthcare platform for managing sleep study appointments,
patient assessments, and medical workflows. Built with Flask, HTMX, and
Supabase for optimal performance and compliance.

Core Features:
- Multi-step sleep study booking flow
- Role-based access control (Patient, Staff, Doctor, Admin)
- Secure file upload for medical referrals
- Standardized sleep assessments (Epworth Scale, OSA-50)
- Real-time UI updates with HTMX
- DDL-compliant database operations
- Healthcare privacy compliance (HIPAA-ready)
"""

import os
from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta
import uuid

# Load environment variables
load_dotenv('.env.local')

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Supabase configuration (following HTMX example pattern)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("Missing Supabase credentials in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Initialize storage buckets for file uploads
def initialize_storage_buckets():
    """
    Initialize Supabase Storage buckets for the sleep study application.
    
    Creates the following buckets with appropriate policies:
    - referrals: Medical referral documents (private)
    - sleep-data: Sleep study result files (private) 
    - reports: Generated reports (private)
    
    Based on environment configuration from .env.local
    """
    try:
        # Get bucket names from environment variables
        referrals_bucket = os.getenv('NEXT_PUBLIC_REFERRALS_BUCKET', 'referrals')
        sleep_data_bucket = os.getenv('NEXT_PUBLIC_SLEEP_DATA_BUCKET',
                                      'sleep-data')
        reports_bucket = os.getenv('NEXT_PUBLIC_REPORTS_BUCKET', 'reports')
        
        buckets_to_create = [
            {'name': referrals_bucket, 'public': False},
            {'name': sleep_data_bucket, 'public': False},
            {'name': reports_bucket, 'public': False}
        ]
        
        # Create buckets if they don't exist
        for bucket_config in buckets_to_create:
            try:
                # Check if bucket exists by trying to list it
                supabase.storage.from_(bucket_config['name']).list()
                bucket_name = bucket_config['name']
                print(f"✅ Storage bucket '{bucket_name}' already exists")
            except Exception:
                # Bucket doesn't exist, create it
                try:
                    supabase.storage.create_bucket(
                        bucket_config['name'],
                        options={'public': bucket_config['public']}
                    )
                    bucket_name = bucket_config['name']
                    print(f"✅ Created storage bucket '{bucket_name}'")
                except Exception as e:
                    bucket_name = bucket_config['name']
                    print(f"⚠️  Could not create bucket '{bucket_name}': {e}")
                    print("   This may require admin privileges or manual "
                          "setup in Supabase Dashboard")
        
        print("🗂️  Storage bucket initialization completed")
        
    except Exception as e:
        print(f"⚠️  Storage initialization error: {e}")
        print("   File uploads may not work until storage buckets are "
              "created manually")

# Initialize storage on app startup
try:
    initialize_storage_buckets()
except Exception as e:
    print(f"Storage initialization skipped: {e}")

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/')
def index():
    """
    Home page route that redirects users based on authentication status.
    
    Returns:
        Response: Redirect to dashboard if authenticated, otherwise renders index page
    """
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/auth')
def auth():
    """
    Authentication page for user login and registration.
    
    Returns:
        str: Rendered authentication page template
    """
    return render_template('auth.html')

@app.route('/auth/signin', methods=['POST'])
def signin():
    """
    Handle user sign-in with email and password authentication.
    
    Form Data:
        email (str): User's email address
        password (str): User's password
        
    Returns:
        Response: Redirect to dashboard on success, auth page with error on failure
    """
    email = request.form.get('email')
    password = request.form.get('password')
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            # Store user in session
            session['user'] = {
                'id': response.user.id,
                'email': response.user.email
            }
            session['access_token'] = response.session.access_token
            session['refresh_token'] = response.session.refresh_token
            
            # Get user profile from app_users table
            profile = get_user_profile(response.user.id)
            if profile:
                session['user']['role'] = profile.get('role')
                # Note: organization_id would come from staff_memberships table
            
            return redirect(url_for('dashboard'))
        else:
            return render_template('auth.html', error="Invalid credentials")
            
    except Exception as e:
        return render_template('auth.html', error=str(e))

@app.route('/auth/signup', methods=['POST'])
def signup():
    """
    Enhanced user registration following HTMX pattern with deferred profile creation.
    
    HTMX Pattern: Standard Supabase auth signup with email verification
    Enhanced: Defers app_users record creation until email verification to avoid timing issues
    
    Form Data:
        email (str): User's email address
        password (str): User's password
        role (str): User role (patient, staff, doctor, admin)
        organization_id (str, optional): Organization ID for staff members
        
    Enhanced Flow:
        1. Create auth.users record (HTMX pattern)
        2. Store role/org info in user metadata for callback
        3. Send verification email (HTMX pattern)
        4. User verifies → /authCallback creates app_users with role → dashboard
        
    Returns:
        str: Rendered auth page with success or error message
    """
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'patient')
    organization_id = request.form.get('organization_id')
    
    try:
        # Step 1: Create the auth user with role metadata
        user_metadata = {
            'role': role
        }
        if organization_id:
            user_metadata['organization_id'] = organization_id
            
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": user_metadata
            }
        })
        
        if response.user:
            return render_template('auth.html', 
                                 success="Account created! Check your email to verify and complete setup.")
        else:
            return render_template('auth.html', error="Failed to create account")
            
    except Exception as e:
        return render_template('auth.html', error=str(e))

@app.route('/auth/signout')
def signout():
    """
    Handle user sign-out and session cleanup.
    
    Returns:
        Response: Redirect to index page
    """
    try:
        supabase.auth.sign_out()
    except:
        pass  # Ignore errors during signout
    
    session.clear()
    return redirect(url_for('index'))

@app.route('/authCallback')
def auth_callback():
    """
    Enhanced auth callback combining HTMX pattern + role-based business logic.
    
    HTMX Pattern: Secure email verification using PKCE flow
    Enhanced: Creates app_users record during verification with role from metadata
    
    Query Parameters:
        code (str): Authorization code from Supabase (PKCE flow)
        error (str): Error message if verification failed
        
    Returns:
        Response: Redirect to dashboard with role-based access or auth with message
    """
    try:
        # HTMX Pattern: Handle error from Supabase
        error = request.args.get('error')
        if error:
            return render_template('auth.html', 
                                 error=f"Email verification failed: {error}")
        
        # HTMX Pattern: Get authorization code
        code = request.args.get('code')
        if not code:
            return render_template('auth.html', 
                                 error="Invalid verification link. Please request a new one.")
        
        # HTMX Pattern: Exchange code for session (PKCE flow)
        response = supabase.auth.exchange_code_for_session(code)
        
        if not response.user:
            return render_template('auth.html', 
                                 error="Email verification failed. Please try again.")
        
        # Enhanced: Create app_users record if it doesn't exist (first-time verification)
        profile = get_user_profile(response.user.id)
        if not profile:
            # Get role from user metadata stored during signup
            user_metadata = response.user.user_metadata or {}
            role = user_metadata.get('role', 'patient')
            organization_id = user_metadata.get('organization_id')
            
            # Use service role client to create profile
            service_supabase = create_client(
                supabase_url=os.getenv('SUPABASE_URL'),
                supabase_key=os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            )
            
            # Create user profile in app_users table
            profile_data = {
                'id': response.user.id,
                'role': role,
                'created_at': datetime.utcnow().isoformat()
            }
            
            service_supabase.table('app_users').insert(profile_data).execute()
            
            # If staff member, create staff membership record
            if role == 'staff' and organization_id:
                staff_membership_data = {
                    'id': str(uuid.uuid4()),
                    'user_id': response.user.id,
                    'organization_id': organization_id,
                    'role_details': {'position': 'staff', 'permissions': ['manage_studies']},
                    'created_at': datetime.utcnow().isoformat()
                }
                service_supabase.table('staff_memberships').insert(staff_membership_data).execute()
            
            # Refresh profile after creation
            profile = {'role': role}
        
        # Enhanced: Create rich session with role-based data
        session['user'] = {
            'id': response.user.id,
            'email': response.user.email,
            'role': profile.get('role'),
            'email_confirmed': True
        }
        session['access_token'] = response.session.access_token
        session['refresh_token'] = response.session.refresh_token
        
        # Enhanced: Role-based redirect
        user_role = profile.get('role')
        if user_role == 'patient':
            return redirect(url_for('dashboard') + '?verified=true')
        elif user_role in ['staff', 'doctor', 'admin']:
            return redirect(url_for('dashboard') + '?verified=true&role=' + user_role)
        else:
            # Fallback for unknown roles
            return render_template('auth.html', 
                                 success="Email verified! You can now sign in.")
            
    except Exception as e:
        return render_template('auth.html', 
                             error=f"Verification error: {str(e)}")

@app.route('/auth/callback')
def auth_callback_redirect():
    """
    Redirect old callback URL to match HTMX example pattern.
    """
    return redirect(url_for('auth_callback'))

@app.route('/auth/verify')
def auth_verify():
    """
    Alternative endpoint for email verification (handles older Supabase URLs).
    
    Returns:
        Response: Redirect to callback handler
    """
    return auth_callback()

# ============================================================================
# DASHBOARD ROUTES
# ============================================================================

@app.route('/dashboard')
def dashboard():
    """
    Enhanced dashboard with role-based content and verification status.
    
    HTMX Pattern: Server-side rendered with user session
    Enhanced: Role-based navigation and verification feedback
    
    Returns:
        str: Rendered dashboard template with user-specific data
        Response: Redirect to auth if not authenticated
    """
    if 'user' not in session:
        return redirect(url_for('auth'))
    
    user = session['user']
    role = user.get('role', 'patient')
    
    # Enhanced: Check for verification status from callback
    just_verified = request.args.get('verified') == 'true'
    
    # Create authenticated client for dashboard data
    if 'access_token' in session:
        auth_client = create_client(
            supabase_url=os.getenv('SUPABASE_URL'),
            supabase_key=os.getenv('SUPABASE_ANON_KEY')
        )
        auth_client.auth.set_session(session['access_token'], session['refresh_token'])
    else:
        auth_client = supabase
    
    # Enhanced: Get role-specific data
    dashboard_data = get_dashboard_data(user, auth_client)
    
    # Enhanced: Add verification success message
    success_message = None
    if just_verified:
        success_message = f"Welcome! Your email has been verified and you're logged in as a {role}."
    
    return render_template('dashboard.html', 
                         user=user, 
                         role=role,
                         data=dashboard_data,
                         success_message=success_message)

# ============================================================================
# SLEEP STUDY BOOKING ROUTES (DDL-Compliant)
# ============================================================================

@app.route('/book-sleep-study')
def book_sleep_study():
    """
    Main booking page that initializes the multi-step booking flow.
    
    Returns:
        str: Rendered booking page template
        Response: Redirect to auth if not authenticated
    """
    if 'user' not in session:
        return redirect(url_for('auth'))
    
    # Initialize booking session data
    session['booking_data'] = {
        'step': 1,
        'appointment': {},
        'personal_details': {},
        'referral': {},
        'epworth_responses': {},
        'osa50_responses': {}
    }
    session.modified = True
    
    return render_template('book-sleep-study.html')

@app.route('/htmx/book-study-form')
def htmx_book_study_form():
    """
    HTMX endpoint to load initial booking form in main content area.
    
    Returns:
        str: Rendered step 1 booking template
        tuple: (error_message, status_code) if unauthorized
    """
    if 'user' not in session:
        return "Unauthorized", 401
    
    # Initialize booking session
    session['booking_data'] = {
        'step': 1,
        'appointment': {},
        'personal_details': {},
        'referral': {},
        'epworth_responses': {},
        'osa50_responses': {}
    }
    session.modified = True
    
    return render_template('fragments/booking/step-1-intro.html')

@app.route('/htmx/booking/step/<int:step>')
def htmx_booking_step(step):
    """
    HTMX endpoint to load a specific booking step with context data.
    
    Args:
        step (int): Step number (1-7) in the booking flow
        
    Returns:
        str: Rendered step template with context data
        tuple: (error_message, status_code) if unauthorized or invalid step
    """
    if 'user' not in session:
        return "Unauthorized", 401

    if 'booking_data' not in session:
        # Initialize booking session automatically if missing
        session['booking_data'] = {
            'step': step,
            'appointment': {},
            'personal_details': {},
            'referral': {},
            'epworth_responses': {},
            'osa50_responses': {}
        }
        session.modified = True

    booking_data = session['booking_data']

    # Validate step progression - prevent skipping required steps
    if step > 2 and not booking_data.get('appointment', {}).get('date'):
        # Redirect to step 2 if appointment not selected
        return render_template('fragments/booking/step-2-time-selection.html',
                             **get_booking_step_context(2),
                             error="Please select an appointment time before proceeding.")
    
    if step > 3 and not booking_data.get('personal_details', {}).get('full_name'):
        # Redirect to step 3 if personal details not completed
        return render_template('fragments/booking/step-3-personal-details.html',
                             **get_booking_step_context(3),
                             error="Please complete your personal details before proceeding.")

    # Update current step
    session['booking_data']['step'] = step
    session.modified = True

    template_map = {
        1: 'fragments/booking/step-1-intro.html',
        2: 'fragments/booking/step-2-time-selection.html', 
        3: 'fragments/booking/step-3-personal-details.html',
        4: 'fragments/booking/step-4-referral-upload.html',
        5: 'fragments/booking/step-5-epworth.html',
        6: 'fragments/booking/step-6-osa50.html',
        7: 'fragments/booking/step-7-confirmation.html'
    }

    template = template_map.get(step)
    if not template:
        return "Invalid step", 400

    # Get additional data needed for the step
    context = get_booking_step_context(step)

    return render_template(template, **context)

@app.route('/htmx/booking/save-step', methods=['POST'])
def htmx_save_booking_step():
    """
    HTMX endpoint to save current step data and advance to next step.
    
    Form Data:
        Varies by step - appointment details, personal info, survey responses
        
    Returns:
        str: Rendered next step template
        tuple: (error_message, status_code) if unauthorized
    """
    if 'user' not in session:
        return "Unauthorized", 401
    
    if 'booking_data' not in session:
        return "Session expired", 400
    
    current_step = session['booking_data']['step']
    
    # Save step data based on current step
    if current_step == 2:  # Time selection
        slot_id = request.form.get('appointment_time')
        # Parse slot_id format: "2025-06-19-14"
        if slot_id:
            date_part, time_part = slot_id.rsplit('-', 1)
            time_formatted = f"{time_part}:00"
            session['booking_data']['appointment'] = {
                'date': date_part,
                'time': time_formatted,
                'slot_id': slot_id
            }
        else:
            return "Please select an appointment time", 400
    
    elif current_step == 3:  # Personal details
        session['booking_data']['personal_details'] = {
            'full_name': request.form.get('fullName'),
            'date_of_birth': request.form.get('dateOfBirth'),
            'phone_number': request.form.get('phoneNumber'),
            'email': request.form.get('email', '')
        }
    
    elif current_step == 5:  # Epworth questionnaire
        epworth_responses = {}
        for i in range(1, 9):  # 8 questions
            epworth_responses[f'q{i}'] = int(request.form.get(f'ep_q{i}', 0))
        session['booking_data']['epworth_responses'] = epworth_responses
    
    elif current_step == 6:  # OSA-50 questionnaire  
        osa50_responses = {}
        for i in range(1, 6):  # 5 questions
            osa50_responses[f'q{i}'] = request.form.get(f'osa_q{i}')
        session['booking_data']['osa50_responses'] = osa50_responses
    
    session.modified = True
    
    # Advance to next step
    next_step = current_step + 1
    if next_step > 7:
        next_step = 7
    
    return htmx_booking_step(next_step)

@app.route('/htmx/booking/upload-referral', methods=['POST'])
def htmx_upload_referral():
    """
    Simple HTMX-friendly file upload with healthcare security.
    
    The hybrid approach: HTMX simplicity + healthcare-grade security.
    Returns HTML fragments (pure HTMX style) with secure cloud storage.
    """
    if 'user' not in session:
        return "Unauthorized", 401

    # Simple validation - HTMX style
    if 'referralDocument' not in request.files:
        return render_template('fragments/booking/upload-error.html', 
                             error="No file selected")

    file = request.files['referralDocument']
    if file.filename == '':
        return render_template('fragments/booking/upload-error.html',
                             error="No file selected")

    # Simple file type validation
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf'}
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        return render_template('fragments/booking/upload-error.html',
                             error="Invalid file type. Please use PDF, JPG, PNG, or GIF.")

    try:
        # Healthcare security: user-specific folder with UUID
        user_id = session['user']['id']
        unique_filename = f"{uuid.uuid4()}-{file.filename}"
        file_path = f"{user_id}/{unique_filename}"  # RLS policy expects: {user_id}/{filename}
        
        # Simple Supabase upload using helper function
        file_url = upload_file_to_supabase(file, file_path, 'referrals')
        
        # Store in session for booking completion
        if 'booking_data' not in session:
            session['booking_data'] = {}
        
        session['booking_data']['referral'] = {
            'filename': file.filename,
            'file_path': file_path,
            'file_url': file_url,
            'uploaded_at': datetime.utcnow().isoformat()
        }
        session.modified = True
        
        # Return success HTML (HTMX way)
        return render_template('fragments/booking/upload-success.html',
                             filename=file.filename)
        
    except Exception as e:
        # Return error HTML (HTMX way)
        return render_template('fragments/booking/upload-error.html',
                             error=str(e))

@app.route('/htmx/booking/submit', methods=['POST'])
def htmx_submit_booking():
    """
    HTMX endpoint for final booking submission with DDL-compliant database operations.
    
    Creates records in multiple tables:
    - sleep_studies: Main study record with required foreign keys
    - patient_profiles: Extended patient information
    - survey_responses: Epworth and OSA-50 questionnaire results
    - referrals: Uploaded referral document links
    
    Returns:
        str: Success template with study details or error template
        tuple: (error_template, status_code) if submission fails
    """
    if 'user' not in session:
        return "Unauthorized", 401
    
    booking_data = session.get('booking_data', {})
    user = session['user']
    
    try:
        # Validate required booking data
        if not booking_data.get('appointment') or not booking_data['appointment'].get('date'):
            return render_template('fragments/booking/booking-error.html',
                                 error="Please complete the appointment time selection (Step 2) before submitting."), 400
        
        if not booking_data.get('personal_details'):
            return render_template('fragments/booking/booking-error.html',
                                 error="Please complete your personal details (Step 3) before submitting."), 400
        
        # Get required manager and doctor assignments
        # In production, implement proper assignment logic based on availability/organization
        default_manager = get_default_staff_member('staff')
        default_doctor = get_default_staff_member('doctor')
        
        # Temporary fallback for testing - use current user if no staff available
        if not default_manager:
            default_manager = {'id': user['id']}
        if not default_doctor:
            default_doctor = {'id': user['id']}
        
        # Create the main sleep study record (DDL compliant)
        study_id = str(uuid.uuid4())
        
        study_data = {
            'id': study_id,
            'patient_id': user['id'],
            'manager_id': default_manager['id'],  # Required by DDL
            'doctor_id': default_doctor['id'],    # Required by DDL
            'device_id': None,  # Will be assigned later by staff
            'current_state': 'booked',
            'start_date': booking_data['appointment']['date'],  # Required by DDL
            'end_date': None,  # Will be set when study completes
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Create authenticated client using user's session token
        if 'access_token' in session:
            auth_client = create_client(
                supabase_url=os.getenv('SUPABASE_URL'),
                supabase_key=os.getenv('SUPABASE_ANON_KEY')
            )
            # Set the user's session for proper authentication
            auth_client.auth.set_session(session['access_token'], session['refresh_token'])
        else:
            auth_client = supabase
        
        # Insert sleep study using authenticated client
        result = auth_client.table('sleep_studies').insert(study_data).execute()
        
        # Store patient profile details if provided
        if booking_data.get('personal_details'):
            upsert_patient_profile(user['id'], booking_data['personal_details'])
        
        # Store Epworth survey response
        if booking_data.get('epworth_responses'):
            epworth_score = sum(booking_data['epworth_responses'].values())
            survey_data = {
                'id': str(uuid.uuid4()),
                'sleep_study_id': study_id,
                'type': 'epworth',
                'answers': booking_data['epworth_responses'],
                'score': epworth_score,
                'created_at': datetime.utcnow().isoformat()
            }
            auth_client.table('survey_responses').insert(survey_data).execute()
        
        # Store OSA-50 survey response  
        if booking_data.get('osa50_responses'):
            osa50_score = sum(1 for v in booking_data['osa50_responses'].values() if v == 'yes')
            survey_data = {
                'id': str(uuid.uuid4()),
                'sleep_study_id': study_id,
                'type': 'osa50',
                'answers': booking_data['osa50_responses'],
                'score': osa50_score,
                'created_at': datetime.utcnow().isoformat()
            }
            auth_client.table('survey_responses').insert(survey_data).execute()
        
        # Store referral document
        if booking_data.get('referral', {}).get('file_url'):
            referral_data = {
                'id': str(uuid.uuid4()),
                'sleep_study_id': study_id,
                'file_url': booking_data['referral']['file_url'],
                'created_at': datetime.utcnow().isoformat()
            }
            auth_client.table('referrals').insert(referral_data).execute()
        
        # Clear booking session data
        session.pop('booking_data', None)
        session.modified = True
        
        # Return success confirmation
        return render_template('fragments/booking/booking-success.html',
                             study_id=study_id,
                             appointment_date=booking_data['appointment']['date'])
    
    except Exception as e:
        import traceback
        error_details = f"Booking submission error: {str(e)}\n"
        error_details += f"Traceback: {traceback.format_exc()}\n"
        error_details += f"Booking data: {booking_data}\n"
        
        # Write debug info to file
        with open('booking_error_debug.txt', 'w') as f:
            f.write(error_details)
            
        return render_template('fragments/booking/booking-error.html',
                             error=str(e)), 500

# ============================================================================
# HTMX FRAGMENT ROUTES
# ============================================================================

@app.route('/htmx/studies')
def htmx_studies():
    """
    HTMX fragment to load studies list based on user role and permissions.
    
    Returns:
        str: Rendered studies list template
        tuple: (error_message, status_code) if unauthorized
    """
    if 'user' not in session:
        return "Unauthorized", 401
    
    user = session['user']
    
    # Create authenticated client for database queries
    if 'access_token' in session:
        auth_client = create_client(
            supabase_url=os.getenv('SUPABASE_URL'),
            supabase_key=os.getenv('SUPABASE_ANON_KEY')
        )
        auth_client.auth.set_session(session['access_token'], session['refresh_token'])
    else:
        auth_client = supabase
    
    studies = get_user_studies(user, auth_client)
    
    return render_template('fragments/studies_list.html', studies=studies)

@app.route('/htmx/create-study', methods=['POST'])
def htmx_create_study():
    """
    HTMX fragment to create a new study (staff/admin functionality).
    
    Form Data:
        patient_id (str): ID of the patient for the study
        notes (str): Optional notes for the study
        
    Returns:
        str: Updated studies list template
        tuple: (error_message, status_code) if creation fails
    """
    if 'user' not in session:
        return "Unauthorized", 401
    
    user = session['user']
    patient_id = request.form.get('patient_id')
    notes = request.form.get('notes', '')
    
    try:
        # Get required assignments for DDL compliance
        default_manager = get_default_staff_member('staff')
        default_doctor = get_default_staff_member('doctor')
        
        if not default_manager or not default_doctor:
            return f"Error: No available staff to assign", 500
        
        study_data = {
            'id': str(uuid.uuid4()),
            'patient_id': patient_id,
            'manager_id': default_manager['id'],
            'doctor_id': default_doctor['id'],
            'current_state': 'booked',
            'start_date': (datetime.utcnow() + timedelta(days=7)).date().isoformat(),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('sleep_studies').insert(study_data).execute()
        
        # Return updated studies list
        studies = get_user_studies(user)
        return render_template('fragments/studies_list.html', studies=studies)
        
    except Exception as e:
        return f"Error creating study: {str(e)}", 400

# ============================================================================
# BOOKING HELPER FUNCTIONS (DDL-Compliant)
# ============================================================================

def get_booking_step_context(step):
    """
    Get additional context data required for each booking step.
    
    Args:
        step (int): Current step number in the booking flow
        
    Returns:
        dict: Context data including current step, user info, and step-specific data
    """
    context = {
        'current_step': step,
        'total_steps': 7,
        'booking_data': session.get('booking_data', {}),
        'user': session.get('user', {})
    }
    
    if step == 2:  # Time selection - load available slots
        context['available_slots'] = get_available_appointment_slots()
    elif step == 3:  # Personal details - pre-fill user data
        user_profile = get_patient_profile(session['user']['id'])
        if user_profile:
            context['user_profile'] = user_profile
    elif step == 5:  # Epworth questionnaire
        context['epworth_questions'] = get_epworth_questions()
    elif step == 6:  # OSA-50 questionnaire  
        context['osa50_questions'] = get_osa50_questions()
    
    return context

def get_patient_profile(user_id):
    """
    Retrieve patient profile from patient_profiles table.
    
    Args:
        user_id (str): UUID of the user/patient
        
    Returns:
        dict|None: Patient profile data or None if not found
    """
    try:
        result = supabase.table('patient_profiles').select('*').eq('user_id', user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error fetching patient profile: {e}")
        return None

def upsert_patient_profile(user_id, personal_details):
    """
    Create or update patient profile in patient_profiles table.
    
    Args:
        user_id (str): UUID of the user/patient
        personal_details (dict): Personal information from booking form
        
    Returns:
        None
    """
    try:
        profile_data = {
            'user_id': user_id,
            'patient_details': personal_details,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Try to update first, then insert if not exists
        existing = get_patient_profile(user_id)
        if existing:
            supabase.table('patient_profiles').update(profile_data).eq('user_id', user_id).execute()
        else:
            profile_data['created_at'] = datetime.utcnow().isoformat()
            supabase.table('patient_profiles').insert(profile_data).execute()
    except Exception as e:
        print(f"Error upserting patient profile: {e}")

def get_default_staff_member(role):
    """
    Get a default staff member for study assignment (simplified for demo).
    
    In production, this would implement proper assignment logic based on:
    - Availability schedules
    - Workload balancing
    - Organization membership
    - Specialization areas
    
    Args:
        role (str): Role type ('staff' or 'doctor')
        
    Returns:
        dict|None: Staff member record or None if none available
    """
    try:
        result = supabase.table('app_users').select('id').eq('role', role).limit(1).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error fetching default {role}: {e}")
        return None

def get_available_appointment_slots():
    """
    Generate available appointment time slots for the next 2 weeks.
    
    In production, this would:
    - Query actual scheduling system
    - Check staff availability
    - Consider facility capacity
    - Exclude holidays and closures
    
    Returns:
        list: Available appointment slots with dates and times
    """
    slots = []
    base_date = datetime.now() + timedelta(days=7)  # Start from next week
    
    for i in range(14):  # Next 2 weeks
        date = base_date + timedelta(days=i)
        if date.weekday() < 5:  # Monday-Friday only
            for hour in [9, 11, 14, 16]:  # Available times
                slots.append({
                    'id': f"{date.strftime('%Y-%m-%d')}-{hour:02d}",
                    'date': date.strftime('%Y-%m-%d'),
                    'time': f"{hour:02d}:00",
                    'display_date': date.strftime('%A, %B %d'),
                    'display_time': f"{hour:02d}:00"
                })
    
    return slots

def get_epworth_questions():
    """
    Get the standard Epworth Sleepiness Scale questionnaire items.
    
    The Epworth Sleepiness Scale is a widely used questionnaire for measuring
    daytime sleepiness. Scores range from 0-24, with higher scores indicating
    greater sleepiness.
    
    Returns:
        list: Epworth questionnaire items with IDs and text
    """
    return [
        {"id": "ep_q1", "text": "Sitting and reading"},
        {"id": "ep_q2", "text": "Watching TV"},
        {"id": "ep_q3", "text": "Sitting, inactive in a public place"},
        {"id": "ep_q4", "text": "As a passenger in a car for an hour without a break"},
        {"id": "ep_q5", "text": "Lying down to rest in the afternoon when circumstances permit"},
        {"id": "ep_q6", "text": "Sitting and talking to someone"},
        {"id": "ep_q7", "text": "Sitting quietly after a lunch without alcohol"},
        {"id": "ep_q8", "text": "In a car, while stopped for a few minutes in the traffic"}
    ]

def get_osa50_questions():
    """
    Get the OSA-50 sleep apnea screening questionnaire items.
    
    The OSA-50 is a validated screening tool for obstructive sleep apnea.
    A score of 3 or more "yes" answers suggests high risk for OSA.
    
    Returns:
        list: OSA-50 questionnaire items with IDs and text
    """
    return [
        {"id": "osa_q1", "text": "Do you snore loudly (louder than talking or loud enough to be heard through closed doors)?"},
        {"id": "osa_q2", "text": "Do you often feel tired, fatigued, or sleepy during daytime?"},
        {"id": "osa_q3", "text": "Has anyone observed you stop breathing during your sleep?"},
        {"id": "osa_q4", "text": "Do you have or are you being treated for high blood pressure?"},
        {"id": "osa_q5", "text": "Is your BMI more than 35 kg/m²?"}
    ]

def upload_file_to_supabase(file, file_path, bucket):
    """
    Upload file using authenticated user with proper RLS policies.
    
    Args:
        file: Flask file object
        file_path (str): Destination path in bucket
        bucket (str): Storage bucket name
        
    Returns:
        str: Public URL of uploaded file
    """
    try:
        # Get bucket name
        bucket_name = os.getenv('NEXT_PUBLIC_REFERRALS_BUCKET', bucket)
        
        # Create authenticated client using user's session token
        if 'access_token' in session:
            auth_client = create_client(
                supabase_url=os.getenv('SUPABASE_URL'),
                supabase_key=os.getenv('SUPABASE_ANON_KEY')
            )
            # Set the user's session for proper authentication
            auth_client.auth.set_session(session['access_token'], session['refresh_token'])
        else:
            # Fallback to unauthenticated client (will likely fail with RLS)
            auth_client = supabase
        
        # Read file content
        file.seek(0)
        file_content = file.read()
        
        # Upload using authenticated user (proper RLS)
        auth_client.storage.from_(bucket_name).upload(file_path, file_content)
        
        # Get public URL
        public_url = auth_client.storage.from_(bucket_name).get_public_url(file_path)
        return public_url
        
    except Exception as e:
        raise Exception(f"Upload error: {str(e)}")
    finally:
        if hasattr(file, 'seek'):
            file.seek(0)

# ============================================================================
# HELPER FUNCTIONS (Updated for DDL Compliance)
# ============================================================================

def get_user_profile(user_id):
    """
    Get user profile from app_users table.
    
    Args:
        user_id (str): UUID of the user
        
    Returns:
        dict|None: User profile data or None if not found
    """
    try:
        result = supabase.table('app_users').select('*').eq('id', user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error fetching user profile: {e}")
        return None

def get_dashboard_data(user, client=None):
    """
    Get role-specific dashboard data for the current user.
    
    Args:
        user (dict): Current user session data
        client: Authenticated Supabase client (optional)
        
    Returns:
        dict: Dashboard data tailored to user's role and permissions
    """
    if client is None:
        client = supabase
        
    role = user.get('role', 'patient')
    data = {}
    
    if role == 'patient':
        data['studies'] = get_patient_studies(user['id'], client)
    elif role == 'staff':
        # Staff can see studies for their organization
        org_studies = get_organization_studies_for_staff(user['id'], client)
        data['organization_studies'] = org_studies
    elif role == 'doctor':
        data['assigned_studies'] = get_doctor_studies(user['id'], client)
    elif role == 'admin':
        data['all_studies'] = get_all_studies(client)
    
    return data

def get_user_studies(user, client=None):
    """
    Get studies list based on user role and permissions.
    
    Args:
        user (dict): Current user session data
        client: Authenticated Supabase client (optional)
        
    Returns:
        list: Studies accessible to the user based on their role
    """
    if client is None:
        client = supabase
        
    role = user.get('role', 'patient')
    
    if role == 'patient':
        return get_patient_studies(user['id'], client)
    elif role == 'staff':
        return get_organization_studies_for_staff(user['id'], client)
    elif role == 'doctor':
        return get_doctor_studies(user['id'], client)
    else:
        return get_all_studies(client)

def get_patient_studies(patient_id, client=None):
    """
    Get all studies for a specific patient (DDL compliant).
    
    Args:
        patient_id (str): UUID of the patient
        client: Authenticated Supabase client (optional)
        
    Returns:
        list: Sleep studies for the patient
    """
    if client is None:
        client = supabase
        
    try:
        result = client.table('sleep_studies').select('*').eq('patient_id', patient_id).execute()
        return result.data
    except Exception as e:
        print(f"Error fetching patient studies: {e}")
        return []

def get_organization_studies_for_staff(staff_user_id):
    """
    Get studies for organizations where the staff member has membership.
    
    Args:
        staff_user_id (str): UUID of the staff user
        
    Returns:
        list: Studies for the staff member's organization(s)
    """
    try:
        # First get the staff member's organization memberships
        memberships = supabase.table('staff_memberships').select('organization_id').eq('user_id', staff_user_id).execute()
        
        if not memberships.data:
            return []
        
        # Get organization IDs
        org_ids = [membership['organization_id'] for membership in memberships.data]
        
        # For now, return all studies (would need organization_id in sleep_studies table for proper filtering)
        # This is a limitation of the current DDL - sleep_studies doesn't have organization_id
        result = supabase.table('sleep_studies').select('*').execute()
        return result.data
    except Exception as e:
        print(f"Error fetching organization studies: {e}")
        return []

def get_doctor_studies(doctor_id):
    """
    Get studies assigned to a specific doctor (DDL compliant).
    
    Args:
        doctor_id (str): UUID of the doctor
        
    Returns:
        list: Studies assigned to the doctor
    """
    try:
        result = supabase.table('sleep_studies').select('*').eq('doctor_id', doctor_id).execute()
        return result.data
    except Exception as e:
        print(f"Error fetching doctor studies: {e}")
        return []

def get_all_studies():
    """
    Get all studies in the system (admin access only).
    
    Returns:
        list: All sleep studies
    """
    try:
        result = supabase.table('sleep_studies').select('*').execute()
        return result.data
    except Exception as e:
        print(f"Error fetching all studies: {e}")
        return []

# ============================================================================
# DEBUG ENDPOINTS (Remove in production)
# ============================================================================

@app.route('/debug/booking-session')
def debug_booking_session():
    """
    Debug endpoint to view current booking session data.
    Remove or secure this endpoint in production.
    """
    if 'user' not in session:
        return "Unauthorized", 401
    
    booking_data = session.get('booking_data', {})
    return {
        'user': session.get('user', {}),
        'booking_data': booking_data,
        'session_keys': list(session.keys())
    }

@app.route('/debug/reset-booking', methods=['POST'])
def debug_reset_booking():
    """
    Debug endpoint to reset booking session data.
    Remove or secure this endpoint in production.
    """
    if 'user' not in session:
        return "Unauthorized", 401
    
    session.pop('booking_data', None)
    session.modified = True
    return "Booking session reset successfully"

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with custom template."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with custom template."""
    return render_template('500.html'), 500

# ============================================================================
# DEVELOPMENT SERVER
# ============================================================================

# ============================================================================
# ROLE-SPECIFIC DASHBOARD HTMX ENDPOINTS
# ============================================================================

@app.route('/htmx/patient/my-studies')
def htmx_patient_my_studies():
    """
    HTMX endpoint to load patient's sleep studies in mobile-friendly card format.
    
    Returns:
        str: Rendered patient studies cards fragment
        tuple: (error_message, status_code) if unauthorized
    """
    if 'user' not in session:
        return "Unauthorized", 401
    
    user = session['user']
    if user.get('role') != 'patient':
        return "Access denied", 403
    
    try:
        # Get patient's studies with related data
        if 'access_token' in session:
            auth_client = create_client(
                supabase_url=os.getenv('SUPABASE_URL'),
                supabase_key=os.getenv('SUPABASE_ANON_KEY')
            )
            auth_client.auth.set_session(session['access_token'], session['refresh_token'])
        else:
            auth_client = supabase
        
        # Get studies with join data for patient cards
        studies_result = auth_client.table('sleep_studies').select(
            '*, devices(device_details), survey_responses(type, score, answers)'
        ).eq('patient_id', user['id']).order('created_at', desc=True).execute()
        
        patient_studies = []
        for study in studies_result.data:
            # Get device name if assigned
            device_name = None
            if study.get('devices') and study['devices'].get('device_details'):
                device_name = study['devices']['device_details'].get('name', 'Device')
            
            # Get assessment scores
            epworth_score = None
            osa50_score = None
            for response in study.get('survey_responses', []):
                if response['type'] == 'epworth':
                    epworth_score = response['score']
                elif response['type'] == 'osa50':
                    osa50_score = response['score']
            
            patient_studies.append({
                'id': study['id'],
                'current_state': study['current_state'],
                'start_date': study['start_date'],
                'device_name': device_name,
                'epworth_score': epworth_score,
                'osa50_score': osa50_score
            })
        
        return render_template('fragments/patient/my-studies-cards.html', 
                             patient_studies=patient_studies)
        
    except Exception as e:
        print(f"Error loading patient studies: {e}")
        return f"<div class='text-center py-8 text-red-600'>Error loading studies: {str(e)}</div>", 500

@app.route('/htmx/patient/studies/<study_id>/confirm-return', methods=['POST'])
def htmx_patient_confirm_return(study_id):
    """
    HTMX endpoint for patient to confirm device return.
    
    Args:
        study_id (str): UUID of the sleep study
        
    Returns:
        str: Updated study card fragment
        tuple: (error_message, status_code) if unauthorized or error
    """
    if 'user' not in session:
        return "Unauthorized", 401
    
    user = session['user']
    if user.get('role') != 'patient':
        return "Access denied", 403
    
    try:
        # Create authenticated client
        if 'access_token' in session:
            auth_client = create_client(
                supabase_url=os.getenv('SUPABASE_URL'),
                supabase_key=os.getenv('SUPABASE_ANON_KEY')
            )
            auth_client.auth.set_session(session['access_token'], session['refresh_token'])
        else:
            auth_client = supabase
        
        # Update study state to 'review' and mark device as available
        # First get the study to check ownership and get device_id
        study_result = auth_client.table('sleep_studies').select('*, devices(*)').eq('id', study_id).eq('patient_id', user['id']).single().execute()
        
        if not study_result.data:
            return "<div class='text-red-600 p-4'>Study not found or access denied</div>", 404
        
        study = study_result.data
        
        # Update study state to review
        auth_client.table('sleep_studies').update({
            'current_state': 'review',
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', study_id).execute()
        
        # Update device status to available if device was assigned
        if study.get('device_id'):
            auth_client.table('devices').update({
                'status': 'available',
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', study['device_id']).execute()
        
        # Return updated study card
        updated_study = {
            'id': study['id'],
            'current_state': 'review',
            'start_date': study['start_date'],
            'device_name': study.get('devices', {}).get('device_details', {}).get('name') if study.get('devices') else None
        }
        
        return render_template('fragments/patient/my-studies-cards.html', 
                             patient_studies=[updated_study])
        
    except Exception as e:
        print(f"Error confirming device return: {e}")
        return f"<div class='text-red-600 p-4'>Error: {str(e)}</div>", 500

@app.route('/htmx/staff/dashboard')
def htmx_staff_dashboard():
    """
    HTMX endpoint to load staff organization dashboard.
    
    Returns:
        str: Rendered staff dashboard fragment
        tuple: (error_message, status_code) if unauthorized
    """
    if 'user' not in session:
        return "Unauthorized", 401
    
    user = session['user']
    if user.get('role') != 'staff':
        return "Access denied", 403
    
    try:
        # Get organization data for staff dashboard
        # This would include pending actions, device status, etc.
        dashboard_data = {
            'pending_actions': [],  # Implement based on business logic
            'devices': {
                'available': 5,  # Get from database
                'assigned': 3,   # Get from database
                'utilization_percent': 60
            },
            'pending_count': 0,
            'week_bookings': 12,
            'capacity_status': 'Normal',
            'over_capacity': False
        }
        
        return render_template('fragments/staff/organization-dashboard.html', **dashboard_data)
        
    except Exception as e:
        print(f"Error loading staff dashboard: {e}")
        return f"<div class='text-center py-8 text-red-600'>Error loading dashboard: {str(e)}</div>", 500

@app.route('/htmx/doctor/dashboard')
def htmx_doctor_dashboard():
    """
    HTMX endpoint to load doctor clinical dashboard.
    
    Returns:
        str: Rendered doctor dashboard fragment
        tuple: (error_message, status_code) if unauthorized
    """
    if 'user' not in session:
        return "Unauthorized", 401
    
    user = session['user']
    if user.get('role') != 'doctor':
        return "Access denied", 403
    
    try:
        # Create authenticated client
        if 'access_token' in session:
            auth_client = create_client(
                supabase_url=os.getenv('SUPABASE_URL'),
                supabase_key=os.getenv('SUPABASE_ANON_KEY')
            )
            auth_client.auth.set_session(session['access_token'], session['refresh_token'])
        else:
            auth_client = supabase
        
        # Get assigned studies for review
        studies_result = auth_client.table('sleep_studies').select(
            '*, patient_profiles(*), survey_responses(type, score, answers), sleep_data_files(*), referrals(*)'
        ).eq('doctor_id', user['id']).order('created_at', desc=True).execute()
        
        assigned_studies = []
        pending_studies = []
        recent_completed = []
        
        for study in studies_result.data:
            # Get patient info
            patient_name = "Patient"  # Default
            if study.get('patient_profiles') and study['patient_profiles'].get('patient_details'):
                patient_details = study['patient_profiles']['patient_details']
                patient_name = patient_details.get('full_name', 'Patient')
            
            # Get assessment scores
            epworth_score = None
            osa50_score = None
            for response in study.get('survey_responses', []):
                if response['type'] == 'epworth':
                    epworth_score = response['score']
                elif response['type'] == 'osa50':
                    osa50_score = response['score']
            
            study_data = {
                'id': study['id'],
                'patient_name': patient_name,
                'current_state': study['current_state'],
                'start_date': study['start_date'],
                'epworth_score': epworth_score or 0,
                'osa50_score': osa50_score or 0,
                'has_referrals': bool(study.get('referrals')),
                'has_sleep_data': bool(study.get('sleep_data_files')),
                'priority': 'high' if (epworth_score or 0) > 15 or (osa50_score or 0) >= 3 else 'normal'
            }
            
            assigned_studies.append(study_data)
            
            if study['current_state'] == 'review':
                pending_studies.append(study_data)
            elif study['current_state'] == 'completed':
                recent_completed.append(study_data)
        
        dashboard_data = {
            'assigned_studies': assigned_studies,
            'pending_studies': pending_studies[:3],  # Show top 3
            'recent_completed': recent_completed[:3],
            'studies_count': {
                'review': len(pending_studies),
                'completed': len(recent_completed)
            }
        }
        
        return render_template('fragments/doctor/clinical-dashboard.html', **dashboard_data)
        
    except Exception as e:
        print(f"Error loading doctor dashboard: {e}")
        return f"<div class='text-center py-8 text-red-600'>Error loading dashboard: {str(e)}</div>", 500

# ============================================================================
# DEVELOPMENT SERVER
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, port=port, host='127.0.0.1')

# Database seeding CLI command
@app.cli.command("seed-database")
def seed_database_command():
    """Create comprehensive test data for the sleep study app."""
    print("🌱 Seeding database with test data...")
    
    try:
        # Import and run the seeding script
        import seed_database
        seed_database.main()
        print("✅ Database seeding completed successfully!")
    except Exception as e:
        print(f"❌ Database seeding failed: {e}")
        return 1
    
    return 0

@app.cli.command("clear-database")
def clear_database_command():
    """Clear all test data from the database."""
    print("🧹 Clearing all test data...")
    
    try:
        import seed_database
        seed_database.clear_existing_data()
        print("✅ Database cleared successfully!")
    except Exception as e:
        print(f"❌ Database clearing failed: {e}")
        return 1
    
    return 0 