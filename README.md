# Sleep Study Management System - Complete Documentation

## Table of Contents

- [System Overview](#system-overview)
- [Why HTMX for Healthcare?](#why-htmx-for-healthcare)
- [Quick Start Guide](#quick-start-guide)
- [Architecture & Technology Stack](#architecture--technology-stack)
- [Database Schema Compliance](#database-schema-compliance)
- [Flask Application Structure](#flask-application-structure)
- [Booking Flow Documentation](#booking-flow-documentation)
- [System Workflows & User Journeys](#system-workflows--user-journeys)
- [Template System](#template-system)
- [HTMX Integration Patterns](#htmx-integration-patterns)
- [API Endpoints Documentation](#api-endpoints-documentation)
- [Authentication & Authorization](#authentication--authorization)
- [Error Handling & Validation](#error-handling--validation)
- [File Upload System](#file-upload-system)
- [Survey & Assessment Tools](#survey--assessment-tools)
- [Development Setup](#development-setup)
- [Database Seeding & Test Data](#database-seeding--test-data)
- [Production Deployment](#production-deployment)
- [Testing Strategy](#testing-strategy)
- [Security Considerations](#security-considerations)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting Guide](#troubleshooting-guide)

---

## System Overview

### Purpose
A comprehensive healthcare platform for managing sleep study appointments, patient assessments, and medical workflows. Built with **Flask**, **HTMX**, and **Supabase** for optimal performance and compliance with healthcare standards.

### Core Features
- **Multi-step sleep study booking flow**: 7-step guided process for appointment scheduling
- **Role-based access control**: Patient, Staff, Doctor, Admin permission levels
- **Secure file upload**: Medical referral document management with validation
- **Standardized assessments**: Epworth Sleepiness Scale and OSA-50 questionnaires
- **Real-time UI updates**: HTMX-powered seamless user experience
- **DDL-compliant operations**: Strict adherence to database schema requirements
- **Healthcare privacy compliance**: HIPAA-ready data handling and storage

### Target Users
1. **Patients**: Book appointments, complete assessments, upload referrals
2. **Staff**: Manage bookings, coordinate studies, handle administrative tasks
3. **Doctors**: Review assessments, manage assigned studies, clinical oversight
4. **Administrators**: System management, organization oversight, reporting

---

## Why HTMX for Healthcare?

This system demonstrates how **HTMX** is ideal for healthcare applications:

### **Compliance & Audit Benefits**
- ✅ **Server-side controlled**: Every action hits the server = complete audit trail
- ✅ **No client-side state**: Reduces data manipulation risks
- ✅ **Simplified security**: All business logic stays on the server
- ✅ **Better for compliance**: HIPAA-friendly architecture

### **Healthcare UX Benefits**
- ⚡ **Instant updates**: Forms submit without page reloads
- 🔄 **Real-time data**: Studies list updates automatically
- 📱 **Progressive enhancement**: Works even with limited JavaScript
- 🎯 **Focused interactions**: No complex SPA state management

### **Technical Advantages**
- **Minimal bundle size**: ~14KB vs 200KB+ for React apps
- **Server-first architecture**: Perfect for healthcare compliance
- **Reduced complexity**: Less moving parts = fewer security vulnerabilities
- **Better SEO**: Server-rendered HTML by default

---

## Quick Start Guide

### 1. Installation
```bash
# Clone and setup
git clone <repository-url>
cd sleep-study-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env.local

# Edit .env.local with your Supabase credentials
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
FLASK_SECRET_KEY=your_secure_secret_key_for_sessions
```

### 3. Database Setup
```sql
-- Execute in Supabase SQL Editor
-- 1. Run the DDL script (sleep-study-app-ddl.sql)
-- 2. Set up Row Level Security policies
-- 3. Create storage buckets for file uploads
```

### 4. Database Seeding (Optional but Recommended)
```bash
# Create comprehensive test data with pre-confirmed users
python seed_database.py

# This creates 12 test users across all roles with realistic data
# See Database Seeding section for login credentials
```

### 5. Run Application
```bash
python app.py
# Visit: http://127.0.0.1:3001
```

### 6. Test the System
```bash
# Login with pre-seeded accounts (no email verification needed):
# Patient: john.smith@email.com / patient123!
# Staff: alice.brown@melbournesleep.com.au / staff123!
# Doctor: dr.michael.sleep@melbournesleep.com.au / doctor123!
# Admin: admin.mel@melbournesleep.com.au / admin123!

# Or create your own accounts:
# - Register new accounts with different roles  
# - Book a sleep study as a patient
# - Upload sample referral documents
# - Complete Epworth Scale and OSA-50 assessments
```

---

## Architecture & Technology Stack

```
Frontend: HTMX + Tailwind CSS + Lucide Icons
Backend:  Flask (Python) + Supabase SDK
Database: PostgreSQL (via Supabase)
Auth:     Supabase Auth + Flask Sessions
Storage:  Supabase Storage (file uploads)
```

### Backend Framework
```python
# Flask Application Structure
"""
A modular Flask application with:
- Session-based authentication via Supabase Auth
- HTMX endpoint handlers for dynamic UI updates
- PostgreSQL database operations via Supabase SDK
- Multi-step form handling with session persistence
- File upload integration with Supabase Storage
"""
```

### Frontend Technologies
- **HTML Templates**: Jinja2 templating with component-based fragments
- **CSS Framework**: Tailwind CSS for utility-first styling
- **JavaScript Enhancement**: HTMX for server-driven interactivity
- **Icons**: Lucide icons for consistent visual language
- **Progressive Enhancement**: Works without JavaScript, enhanced with it

### Database & Storage
- **Database**: PostgreSQL via Supabase with real-time capabilities
- **Authentication**: Supabase Auth with JWT tokens
- **File Storage**: Supabase Storage with security policies
- **Schema**: DDL-compliant structure with proper foreign key relationships

---

## Database Schema Compliance

### Database Entity Relationship Diagram

The following ERD provides a comprehensive view of the database schema with organizational constraints and multi-tenant security:

erDiagram
    auth_users {
        uuid id PK
        string email
        string encrypted_password
        timestamptz email_confirmed_at
        timestamptz created_at 
    }
    organizations {
        uuid id PK
        string name
        jsonb organization_details
        jsonb opening_hours
        int max_concurrent_studies
        timestamptz created_at
        timestamptz updated_at
    }
    app_users {
        uuid id PK "FK to auth_users"
        string role "patient|staff|doctor|admin"
        timestamptz created_at
    }
    organization_memberships {
        uuid id PK
        uuid user_id FK
        uuid organization_id FK
        jsonb role_details "title, department, permissions, etc"
        timestamptz created_at
    }
    patient_profiles {
        uuid user_id PK "FK to app_users"
        jsonb patient_details
        timestamptz created_at
        timestamptz updated_at
    }
    devices {
        uuid id PK
        uuid organization_id FK
        jsonb device_details
        device_status status
        timestamptz created_at
        timestamptz updated_at
    }
    sleep_studies {
        uuid id PK
        uuid organization_id FK "NEW: organizational context"
        uuid patient_id FK
        uuid manager_id FK "staff from same org"
        uuid doctor_id FK "doctor from same org"
        uuid device_id FK "device from same org"
        study_state current_state
        date start_date
        date end_date
        timestamptz created_at
        timestamptz updated_at
    }
    referrals {
        uuid id PK
        uuid sleep_study_id FK
        string file_url
        timestamptz created_at
    }
    survey_responses {
        uuid id PK
        uuid sleep_study_id FK
        string type
        jsonb answers
        int score
        timestamptz created_at
    }
    sleep_data_files {
        uuid id PK
        uuid sleep_study_id FK
        string file_url
        timestamptz created_at
    }
    doctor_reports {
        uuid id PK
        uuid sleep_study_id FK
        string file_url
        timestamptz created_at
    }
    device_status {
        string available
        string assigned
    }
    study_state {
        string booked
        string active
        string review
        string completed
        string cancelled
    }
    storage_buckets {
        string referrals_bucket
        string sleep_data_bucket
        string reports_bucket
    }

    %% Core Identity & Auth
    auth_users ||--|| app_users : "extends"
    
    %% Organization Structure
    organizations ||--o{ organization_memberships : "has_members"
    app_users ||--o{ organization_memberships : "member_of"
    
    %% Organization Ownership
    organizations ||--o{ devices : "owns"
    organizations ||--o{ sleep_studies : "manages"
    
    %% User Profiles
    app_users ||--o| patient_profiles : "patient_details"
    
    %% Sleep Studies with Organizational Constraints
    app_users ||--o{ sleep_studies : "patient"
    app_users ||--o{ sleep_studies : "manager_same_org"
    app_users ||--o{ sleep_studies : "doctor_same_org"
    devices ||--o{ sleep_studies : "assigned_same_org"
    
    %% Study Documents & Data
    sleep_studies ||--o{ referrals : "has"
    sleep_studies ||--o{ survey_responses : "has"
    sleep_studies ||--o{ sleep_data_files : "produces"
    sleep_studies ||--o{ doctor_reports : "results_in"
    
    %% File Storage
    referrals }o--|| storage_buckets : "stored_in"
    sleep_data_files }o--|| storage_buckets : "stored_in"
    doctor_reports }o--|| storage_buckets : "stored_in"

### Core Tables Overview

#### app_users
```sql
-- Primary user accounts table
CREATE TABLE app_users (
    id UUID PRIMARY KEY,  -- Supabase Auth user ID
    role TEXT NOT NULL CHECK (role IN ('patient', 'staff', 'doctor', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### sleep_studies
```sql
-- Main sleep study records (DDL compliant with organizational context)
CREATE TABLE sleep_studies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES app_users(id),
    manager_id UUID NOT NULL REFERENCES app_users(id),  -- Required assignment
    doctor_id UUID NOT NULL REFERENCES app_users(id),   -- Required assignment
    device_id UUID REFERENCES devices(id),              -- Optional, assigned later
    organization_id UUID NOT NULL REFERENCES organizations(id), -- NEW: Multi-tenant context
    current_state TEXT NOT NULL DEFAULT 'booked',
    start_date DATE NOT NULL,                           -- Required for scheduling
    end_date DATE,                                      -- Set when study completes
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### organization_memberships (formerly staff_memberships)
```sql
-- Links users (staff, doctors, admins) to organizations with role details and permissions
CREATE TABLE organization_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES app_users(id),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    role_details JSONB NOT NULL,                        -- Position, permissions, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### Key Relationships
- **patient_profiles**: Extended patient information storage
- **organization_memberships**: Organization membership for staff, doctors, and admins
- **survey_responses**: Epworth Scale and OSA-50 questionnaire results
- **referrals**: Medical referral document links and metadata
- **devices**: Sleep monitoring equipment owned by organizations
- **doctor_reports**: Final medical reports for completed studies

### Recent Schema Updates (January 2025)
- ✅ **Table Renamed**: `staff_memberships` → `organization_memberships` for clarity
- ✅ **Enhanced Organizational Context**: Added `organization_id` to `sleep_studies` for proper multi-tenant isolation
- ✅ **Updated RLS Policies**: Comprehensive Row Level Security policies aligned with MVP workflows
- ✅ **Staff Administrative Powers**: Staff can now help patients manage bookings (phone/in-person support)

### Schema Constraints
1. **Foreign Key Integrity**: All references properly maintained with CASCADE options
2. **Role Validation**: Enum constraints on user roles and study states
3. **Required Fields**: Non-null constraints on critical data
4. **Date Validation**: Proper timestamp handling for scheduling
5. **Multi-Tenant Security**: RLS policies enforce organizational boundaries
6. **Administrative Support**: Staff can assist patients across their organization

### Applied Migrations (11 total)
- **20250604093002** - Initial schema with tables and enums
- **20250604093038** - Advanced RLS policies and performance indexes
- **20250605022757** - Fixed app_users RLS policies
- **20250605023039** - Fixed app_users signup RLS policy
- **20250605023654** - Fixed signup RLS timing issue
- **20250605023814** - Fixed auth_users permission error
- **20250605052546** - Fixed staff_memberships infinite recursion
- **20250605080225** - Allowed patient booking creation
- **20250606020241** - Updated RLS policies for staff admin permissions
- **20250606042044** - Fixed organizational structure v2 (MAJOR: renamed tables & added org context)
- **20250606043247** - Aligned RLS policies with updated schema and MVP workflows

### Row Level Security (RLS) Policies

Our comprehensive RLS policies enable the complete MVP workflow while maintaining strict security boundaries:

#### **Patient Self-Service Capabilities**
```sql
-- Patients can view and manage their own data
CREATE POLICY "Patients can view their own sleep studies" ON sleep_studies FOR SELECT
USING (auth.uid() = patient_id);

-- Patients can create their own bookings
CREATE POLICY "Patients can create their own sleep studies" ON sleep_studies FOR INSERT
WITH CHECK (auth.uid() = patient_id);
```

#### **Staff Administrative Powers**
```sql
-- Staff can view all studies in their organization
CREATE POLICY "Organization members can view studies in their org" ON sleep_studies FOR SELECT
USING (
    auth.uid() = patient_id OR
    organization_id IN (
        SELECT organization_id FROM organization_memberships WHERE user_id = auth.uid()
    )
);

-- Staff can help patients create and manage studies
CREATE POLICY "Organization members can create studies in their org" ON sleep_studies FOR INSERT
WITH CHECK (
    auth.uid() = patient_id OR
    organization_id IN (
        SELECT organization_id FROM organization_memberships WHERE user_id = auth.uid()
    )
);
```

#### **Healthcare Support Scenarios Enabled**
- 🔸 **Phone Support**: Staff can walk elderly patients through booking
- 🔸 **In-Person Assistance**: Complete forms together with patients  
- 🔸 **Family Help**: Assist family members managing patient care
- 🔸 **Administrative Support**: Handle complex multi-step processes

#### **Multi-Tenant Security**
- ✅ **Organizational Isolation**: Users can only access data within their organization(s)
- ✅ **Cross-Organization Prevention**: Complete data isolation between organizations
- ✅ **Role-Based Access**: Different permissions for patients, staff, doctors, and admins
- ✅ **Audit Trail**: All access logged through RLS policy enforcement

---

## Flask Application Structure

### Application Initialization
```python
def create_app():
    """
    Application factory pattern for Flask app creation.
    
    Handles:
    - Environment configuration loading
    - Supabase client initialization
    - Error handler registration
    - Route blueprint registration
    """
```

### Features by Role

#### **Patient**
- Book new sleep studies (7-step process)
- Complete medical assessments
- Upload referral documents
- Track study progress
- View results and reports

#### **Staff**
- **Administrative Powers**: Help patients manage bookings (phone/in-person support)
- **Organization Studies**: View and manage all studies within their organization
- **Patient Assistance**: Create accounts and complete forms on behalf of patients
- **Device Management**: Assign and track sleep monitoring equipment
- **Workflow Coordination**: Manage study states and handoffs between roles
- **Multi-Step Support**: Handle complex booking processes for patients needing help

#### **Doctor**
- Review assigned studies
- Complete clinical assessments
- Create medical reports
- Manage patient care plans

#### **Admin**
- System oversight and configuration
- User and organization management
- Analytics and reporting
- Security monitoring

### Core Route Categories

#### Authentication Routes
```python
@app.route('/auth/signin', methods=['POST'])
def signin():
    """
    Handle user sign-in with email and password authentication.
    
    Process:
    1. Validate user credentials via Supabase Auth
    2. Store user session data including role and permissions
    3. Retrieve additional profile information from app_users table
    4. Handle organization membership for staff users
    
    Returns:
        Response: Redirect to dashboard on success, auth page with error on failure
    """
```

#### Booking System Routes
```python
@app.route('/htmx/booking/submit', methods=['POST'])
def htmx_submit_booking():
    """
    HTMX endpoint for final booking submission with DDL-compliant database operations.
    
    Creates records in multiple tables:
    - sleep_studies: Main study record with required foreign keys
    - patient_profiles: Extended patient information
    - survey_responses: Epworth and OSA-50 questionnaire results
    - referrals: Uploaded referral document links
    
    Validation:
    - Checks for required staff assignments
    - Validates form data completeness
    - Ensures proper session state
    
    Returns:
        str: Success template with study details or error template
    """
```

### Session Management
```python
def manage_booking_session():
    """
    Multi-step form session management strategy.
    
    Structure:
    session['booking_data'] = {
        'step': int,              # Current step (1-7)
        'appointment': dict,      # Time slot selection
        'personal_details': dict, # Patient information
        'referral': dict,         # File upload metadata
        'epworth_responses': dict, # Assessment answers
        'osa50_responses': dict   # Screening answers
    }
    
    Benefits:
    - Preserves user progress across steps
    - Enables back/forward navigation
    - Provides data for confirmation step
    - Handles partial completion gracefully
    """
```

---

## Booking Flow Documentation

### Step-by-Step Process

#### Step 1: Introduction
```html
<!-- Purpose: Welcome user and explain the booking process -->
<template name="step-1-intro">
    Features:
    - Process overview with estimated completion time
    - Feature highlights (scheduling, referral upload, assessments)
    - Clear call-to-action to begin booking
    - Progress indicator initialization
</template>
```

#### Step 2: Time Selection
```python
def get_available_appointment_slots():
    """
    Generate available appointment time slots for the next 2 weeks.
    
    Production Implementation:
    - Query actual scheduling system
    - Check staff availability calendars
    - Consider facility capacity constraints
    - Exclude holidays and facility closures
    - Handle timezone considerations
    
    Demo Implementation:
    - Generate slots for business days (Monday-Friday)
    - Provide 4 time slots per day (9 AM, 11 AM, 2 PM, 4 PM)
    - Start from next week to allow preparation time
    
    Returns:
        list: Available appointment slots with display formatting
    """
```

#### Step 3: Personal Details
```python
def collect_patient_information():
    """
    Collect and validate patient personal information.
    
    Required Fields:
    - Full Name: Legal name for medical records
    - Date of Birth: Age verification and medical history
    - Phone Number: Contact for appointment coordination
    
    Optional Fields:
    - Email Address: Digital communication preferences
    
    Validation:
    - Client-side: HTML5 validation for immediate feedback
    - Server-side: Data sanitization and format checking
    - Database: Secure storage with encryption at rest
    
    Pre-filling:
    - Retrieves existing patient profile data if available
    - Maintains user-entered data across navigation
    """
```

#### Step 4: Referral Upload
```python
def handle_referral_upload():
    """
    Secure medical referral document upload process.
    
    Supported Formats:
    - JPG/JPEG: Scanned referral images
    - PNG: Digital referral screenshots
    - GIF: Animated medical documents (rare)
    - PDF: Digital referral documents
    
    Security Measures:
    - File type validation via extension and MIME type
    - File size limits (implementation needed)
    - Virus scanning (production requirement)
    - Secure upload to Supabase Storage bucket
    
    Storage Strategy:
    - User-specific folder structure: /referrals/{user_id}/
    - UUID-prefixed filenames to prevent conflicts
    - Public URL generation for authorized access
    """
```

#### Step 5: Epworth Sleepiness Scale
```python
def epworth_assessment():
    """
    Implementation of the standardized Epworth Sleepiness Scale.
    
    Clinical Significance:
    The Epworth Sleepiness Scale is a validated questionnaire used worldwide
    to measure daytime sleepiness. It consists of 8 situations where patients
    rate their likelihood of dozing from 0-3.
    
    Scoring:
    - Total Score Range: 0-24
    - 0-10: Normal daytime sleepiness
    - 11-15: Moderate daytime sleepiness
    - 16-24: Severe daytime sleepiness (high risk for sleep disorders)
    
    Questions:
    1. Sitting and reading
    2. Watching TV
    3. Sitting inactive in public place
    4. As passenger in car for 1 hour
    5. Lying down to rest in afternoon
    6. Sitting and talking to someone
    7. Sitting quietly after lunch (no alcohol)
    8. In car stopped in traffic
    """
```

#### Step 6: OSA-50 Screening
```python
def osa50_screening():
    """
    Implementation of the OSA-50 sleep apnea screening tool.
    
    Clinical Purpose:
    The OSA-50 is a validated 5-question screening tool for obstructive sleep apnea.
    It helps identify patients at high risk who would benefit from sleep studies.
    
    Scoring:
    - Yes/No responses for each question
    - Score: Number of "Yes" responses (0-5)
    - Risk Assessment:
      * 0-2 "Yes": Lower risk for OSA
      * 3-5 "Yes": Higher risk for OSA (requires evaluation)
    
    Questions:
    1. Loud snoring (louder than talking/through closed doors)
    2. Frequent tired/fatigued/sleepy during daytime
    3. Observed breathing cessation during sleep
    4. High blood pressure or being treated for it
    5. BMI greater than 35 kg/m²
    """
```

#### Step 7: Confirmation & Submission
```python
def booking_confirmation():
    """
    Final review and submission step with comprehensive validation.
    
    Review Components:
    - Appointment details with date/time confirmation
    - Personal information summary with edit options
    - Referral upload status and file verification
    - Assessment results with clinical interpretation
    - Important pre-study information and instructions
    
    Submission Process:
    1. Validate all required data is present
    2. Obtain explicit user consent for data processing
    3. Create sleep study record with proper foreign key assignments
    4. Store patient profile information
    5. Save assessment responses for clinical review
    6. Link referral documents to study record
    7. Clear session data to prevent duplicate submissions
    8. Generate confirmation with unique study identifier
    
    Error Handling:
    - Database transaction rollback on any failure
    - Detailed error messages for user guidance
    - Fallback options for partial data recovery
    """
```

---

## System Workflows & User Journeys

### Patient Workflow

The patient journey encompasses the complete lifecycle from initial onboarding through study completion and results access:

```python
def patient_journey_overview():
    """
    Complete patient workflow from registration to results.
    
    Key Phases:
    1. Initial Onboarding: Account creation and profile setup
    2. Sleep Study Booking: Multi-step booking process with assessments
    3. Active Study Period: Home-based sleep monitoring
    4. Results & Follow-up: Report access and care coordination
    
    Database Interactions:
    - auth_users: Supabase authentication 
    - app_users: Role assignment and permissions
    - patient_profiles: Extended medical information
    - sleep_studies: Study records with organizational context
    - referrals: Medical referral document management
    - survey_responses: Assessment questionnaire data
    - doctor_reports: Final clinical reports
    """
```

sequenceDiagram
    participant P as Patient
    participant System as Sleep Study System
    participant Staff as Staff Member
    participant Doctor as Doctor

    Note over P: INITIAL ONBOARDING
    P->>System: Visit Website/App
    P->>System: Sign Up "auth.users"
    P->>System: Create App User Record "app_users"
    P->>System: Complete Patient Profile "patient_profiles"
    
    Note over P: SLEEP STUDY BOOKING
    P->>System: Access Dashboard
    alt No Active Study
        P->>System: Browse Available Services
        P->>System: Select Sleep Study Type
        P->>System: Choose Preferred Dates
        P->>System: Upload Medical Referral "referrals"
        P->>System: Complete Pre-Study Surveys "survey_responses"
        P->>System: Submit Booking Request
    else Has Active Study
        P->>System: Check Study Status
        P->>System: View Study Timeline
    end
    
    Note over P: ACTIVE STUDY PERIOD
    P->>P: Conduct Sleep Study at Home
    
    Note over P: RESULTS
    System->>P: Notify Results Available
    P->>System: Access Dashboard
    P->>System: Download Medical Report
    P->>System: View Study Summary

### Staff Workflow

Staff members serve as healthcare coordinators, managing the administrative and operational aspects of sleep studies with enhanced patient assistance capabilities:

```python
def staff_administrative_workflow():
    """
    Enhanced staff workflow with patient assistance capabilities.
    
    Core Responsibilities:
    1. Daily Operations: Dashboard monitoring and queue management
    2. Patient Assistance: Help with bookings and form completion
    3. Study Management: Device assignment and state transitions
    4. Device Lifecycle: Equipment tracking and data collection
    
    Enhanced RLS Capabilities (January 2025):
    - Staff can create patient accounts (phone/in-person support)
    - Complete forms on behalf of patients (family assistance)
    - Manage all studies within their organization
    - Handle complex multi-step processes for patients needing help
    
    Database Operations:
    - organization_memberships: Staff role and permissions
    - devices: Equipment assignment and status tracking
    - sleep_studies: Study creation and state management
    - sleep_data_files: Upload of monitoring results
    """
```

sequenceDiagram
    participant Staff as Staff Member
    participant System as Sleep Study System
    participant P as Patient

    Note over Staff: DAILY OPERATIONS
    Staff->>System: Login to Dashboard
    Staff->>System: View Organization Overview
    Staff->>System: Check Pending Bookings
    Staff->>System: Review Device Availability
    
    Note over Staff: PATIENT ASSISTANCE     
    Staff->>System: Access Patient Profile "patient_profiles"
    alt New Patient
        Staff->>System: Create Patient Account "app_users"
        Staff->>System: Complete Profile on Behalf "patient_profiles"
    end
    alt New Sleep Study
        Staff->>System: Create Sleep Study "sleep_studies"
        Staff->>System: Complete Surveys with Patient "survey_responses"
        Staff->>System: Upload Referral Documents "referrals"
    end

    Note over Staff: STUDY MANAGEMENT
    Staff->>System: Review Booking Queue
    Staff->>System: Check Available Devices "devices status: available"
    Staff->>System: Assign Device to Study "devices: status=assigned"
    Staff->>System: Update Study State "booked → active"
    
    Note over Staff: DEVICE LIFECYCLE
    Staff->>System: Mark Device Available "devices: status=available"
    Staff->>System: Upload Sleep Data Files "sleep_data_files"
    Staff->>System: Update Study State "active → review"
    Staff->>System: Assign Study for Review "sleep_study: doctor_id"

### Doctor Workflow

Doctors provide clinical oversight and medical interpretation of sleep study results within their assigned organizational context:

```python
def doctor_clinical_workflow():
    """
    Clinical workflow for sleep study review and reporting.
    
    Clinical Responsibilities:
    1. Study Review: Comprehensive analysis of sleep data
    2. Medical Assessment: Integration with patient history
    3. Report Generation: Clinical findings and recommendations
    4. Care Coordination: Follow-up planning and referrals
    
    Organizational Context:
    - Doctors only see studies from their assigned organizations
    - RLS policies enforce strict organizational boundaries
    - Multi-organization doctors have appropriate access scope
    
    Database Operations:
    - sleep_studies: Studies assigned for clinical review
    - patient_profiles: Medical history and clinical context
    - referrals: Original medical referral documents
    - survey_responses: Pre-study assessment data
    - sleep_data_files: Raw monitoring data analysis
    - doctor_reports: Final clinical report generation
    """
```

sequenceDiagram
    participant Doctor as Doctor
    participant System as Sleep Study System
    participant P as Patient

    Note over Doctor: DOCTOR WORKFLOW
    Doctor->>System: Login to Clinical Portal
    Doctor->>System: View Assigned Studies Dashboard
    Doctor->>System: Check Studies in "review" State
    
    Note over Doctor: STUDY REVIEW
    loop For Each Study
        Doctor->>System: Open Study Details "sleep_studies"
        Doctor->>System: Review Patient Profile "patient_profiles"
        Doctor->>System: Download Medical Referral "referrals"
        Doctor->>System: Review Pre-Study Surveys "survey_responses"
        
        Note over Doctor: DATA ANALYSIS
        Doctor->>System: Download Sleep Data Files "sleep_data_files"
        Doctor->>System: Upload Final Report "doctor_reports"
        Doctor->>System: Update Study State "review → completed"
    end

### Workflow Integration Benefits

The integrated workflow system provides several key advantages:

#### **Healthcare Support Scenarios**
- 🔸 **Phone Support**: Staff can walk elderly patients through the complete booking process
- 🔸 **In-Person Assistance**: Complete forms together during office visits
- 🔸 **Family Help**: Assist family members managing patient care
- 🔸 **Complex Cases**: Handle multi-step processes for patients with special needs

#### **Organizational Efficiency**
- ⚡ **Streamlined Handoffs**: Clear state transitions between roles
- 📊 **Real-time Visibility**: Dashboard updates across all user types
- 🔄 **Device Optimization**: Efficient equipment utilization tracking
- 📋 **Queue Management**: Systematic study progression monitoring

#### **Clinical Quality**
- 🏥 **Comprehensive Data**: Complete patient context for clinical decisions
- 📝 **Standardized Assessments**: Consistent pre-study evaluations
- 🔍 **Detailed Analysis**: Multi-source data integration for diagnosis
- 📊 **Audit Trail**: Complete workflow history for compliance

---

## Template System

### Base Template Architecture
```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- HTMX Integration -->
    <script src="https://unpkg.com/htmx.org@1.9.12"></script>
    
    <!-- Tailwind CSS Framework -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    
    <!-- Healthcare Theme Configuration -->
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        'patient': { 50: '#eff6ff', 600: '#2563eb', 700: '#1d4ed8' },
                        'staff': { 50: '#f0fdf4', 600: '#059669', 700: '#047857' },
                        'doctor': { 50: '#faf5ff', 600: '#7c3aed', 700: '#6d28d9' },
                        'admin': { 50: '#fffbeb', 600: '#d97706', 700: '#b45309' }
                    }
                }
            }
        }
    </script>
</head>
<body>
    <!-- Navigation, Content, Footer -->
</body>
</html>
```

### Fragment-Based Components
```html
<!-- templates/fragments/booking/ structure -->
step-1-intro.html           # Welcome and process overview
step-2-time-selection.html  # Appointment time picker
step-3-personal-details.html # Patient information form
step-4-referral-upload.html # File upload interface
step-5-epworth.html         # Epworth Scale questionnaire
step-6-osa50.html          # OSA-50 screening tool
step-7-confirmation.html    # Review and submission
booking-success.html        # Confirmation page
booking-error.html         # Error handling
upload-success.html        # File upload success
upload-error.html          # File upload errors
```

---

## HTMX Integration Patterns

### **Key HTMX Patterns Used**

#### **Lazy Loading**
```html
<!-- Load content when element becomes visible -->
<div hx-get="/htmx/studies" hx-trigger="load" hx-indicator="#loading">
    <div id="loading">Loading studies...</div>
</div>
```

#### **Form Submissions**
```html
<!-- Submit form and replace target content -->
<form hx-post="/htmx/booking/save-step" 
      hx-target="#booking-content"
      hx-swap="innerHTML"
      hx-indicator="#step-loading">
    <!-- Form fields -->
</form>
```

#### **Progress Bar Updates**
```html
<!-- Out-of-band swap for progress indication -->
<div hx-swap-oob="innerHTML:#progress-container">
    <div class="w-full bg-gray-200 rounded-full h-2">
        <div class="bg-patient-600 h-2 rounded-full" style="width: 42%"></div>
    </div>
</div>
```

#### **Conditional Actions**
```html
<!-- Confirm dialog before action -->
<button hx-post="/htmx/study/123/start" 
        hx-confirm="Start this study?"
        hx-target="#study-status">
    Start Study
</button>
```

#### **Loading Indicators**
```html
<!-- Global loading indicator -->
<div id="loading-indicator" 
     class="htmx-indicator fixed top-4 right-4 bg-blue-600 text-white px-4 py-2 rounded">
    <div class="flex items-center space-x-2">
        <div class="spinner"></div>
        <span>Loading...</span>
    </div>
</div>
```

#### **Real-time Updates**
```html
<!-- Poll for updates every 30 seconds -->
<div hx-get="/htmx/studies/status" 
     hx-trigger="every 30s"
     hx-target="#studies-list">
    <!-- Studies list content -->
</div>
```

### **Navigation**
```html
<!-- Seamless step navigation -->
<button hx-get="/htmx/booking/step/2" 
        hx-target="#booking-content"
        hx-swap="innerHTML"
        hx-push-url="false">
    Next Step
</button>
```

---

## API Endpoints Documentation

### Authentication Endpoints

#### POST /auth/signin
```python
"""
User authentication endpoint.

Request Body:
    email (str): User's email address
    password (str): User's password

Response:
    Success: Redirect to /dashboard
    Error: Rendered auth.html with error message

Session Storage:
    user: {id, email, role}
    access_token: JWT token for API calls
    refresh_token: Token refresh capability
"""
```

#### POST /auth/signup
```python
"""
User registration endpoint with role assignment.

Request Body:
    email (str): New user's email
    password (str): Secure password
    role (str): Account type (patient/staff/doctor/admin)
    organization_id (str, optional): For staff accounts

Database Operations:
    1. Create auth account via Supabase Auth
    2. Insert user profile in app_users table
    3. Create staff membership if applicable

Response:
    Success: Confirmation message
    Error: Registration error details
"""
```

### Booking System Endpoints

#### GET /book-sleep-study
```python
"""
Main booking page initialization.

Purpose:
    - Initialize booking session data
    - Render main booking template
    - Set up progress tracking

Session Initialization:
    booking_data: {
        step: 1,
        appointment: {},
        personal_details: {},
        referral: {},
        epworth_responses: {},
        osa50_responses: {}
    }
"""
```

#### GET /htmx/booking/step/<int:step>
```python
"""
Dynamic step loading endpoint.

Parameters:
    step (int): Target step number (1-7)

Context Loading:
    - Step 2: Available appointment slots
    - Step 3: Existing patient profile data
    - Step 5: Epworth questionnaire items
    - Step 6: OSA-50 questionnaire items
    - Step 7: Complete booking summary

Response:
    HTML fragment for requested step
"""
```

#### POST /htmx/booking/save-step
```python
"""
Step data persistence endpoint.

Processing Logic:
    - Validates current step data
    - Updates session with form data
    - Advances to next step automatically
    - Handles step-specific validation

Data Handling:
    Step 2: Appointment time selection
    Step 3: Personal information
    Step 5: Epworth Scale responses
    Step 6: OSA-50 screening responses

Error Handling:
    - Form validation errors
    - Session state corruption
    - Database connectivity issues
"""
```

#### POST /htmx/booking/upload-referral
```python
"""
File upload endpoint for medical referrals.

Validation:
    - File presence check
    - Extension validation (.jpg, .png, .gif, .pdf)
    - File size limits (configurable)
    - MIME type verification

Storage Process:
    1. Generate unique file path with UUID
    2. Upload to Supabase Storage bucket
    3. Store metadata in session
    4. Return success/error response

Security:
    - User-specific folder isolation
    - Filename sanitization
    - Access control via storage policies
"""
```

#### POST /htmx/booking/submit
```python
"""
Final booking submission with full database transaction.

Transaction Steps:
    1. Validate complete booking data
    2. Assign default manager and doctor
    3. Create sleep_studies record
    4. Upsert patient_profiles
    5. Store survey_responses (Epworth & OSA-50)
    6. Link referral documents
    7. Clear session data

Error Recovery:
    - Full transaction rollback on any failure
    - Detailed error reporting
    - Session preservation for retry attempts

Success Response:
    - Booking confirmation with study ID
    - Next steps information
    - Contact details for support
"""
```

---

## Authentication & Authorization

### Role-Based Access Control
```python
def check_user_permissions(required_role):
    """
    Decorator for route-level permission checking.
    
    Role Hierarchy:
    - patient: Book studies, view own records
    - staff: Manage bookings, coordinate studies
    - doctor: Clinical oversight, assigned studies
    - admin: Full system access, organization management
    
    Implementation:
    @check_user_permissions('staff')
    def staff_only_endpoint():
        pass
    """
```

### Session Management
```python
def manage_user_session():
    """
    Secure session handling with Supabase integration.
    
    Session Data:
    - user: {id, email, role}
    - access_token: API authentication
    - refresh_token: Session renewal
    - booking_data: Multi-step form state
    
    Security Features:
    - Automatic token refresh
    - Session timeout handling
    - Secure cookie configuration
    - Cross-site request forgery protection
    """
```

### Organization Membership
```python
def handle_staff_organizations():
    """
    Multi-organization staff membership management.
    
    Database Structure:
    staff_memberships: {
        user_id: Staff member UUID
        organization_id: Organization UUID
        role_details: JSON permissions object
    }
    
    Use Cases:
    - Staff working at multiple locations
    - Temporary assignments and rotations
    - Permission inheritance from organization
    """
```

---

## Error Handling & Validation

### Client-Side Validation
```javascript
// Form validation with immediate feedback
function validateBookingStep() {
    /*
    Validation Layers:
    1. HTML5 validation attributes (required, type, pattern)
    2. Custom JavaScript validation for complex rules
    3. Real-time feedback during user input
    4. Visual indicators for validation state
    
    Benefits:
    - Immediate user feedback
    - Reduced server requests
    - Better user experience
    - Accessibility compliance
    */
}
```

### Server-Side Validation
```python
def validate_booking_data(step_data, step_number):
    """
    Comprehensive server-side validation for each booking step.
    
    Validation Rules:
    Step 2: Date/time format, availability check, future date
    Step 3: Name format, phone validation, email format
    Step 4: File type, size limits, upload integrity
    Step 5: Response range (0-3), completeness check
    Step 6: Boolean responses, required questions
    Step 7: Consent confirmation, data completeness
    
    Error Response Format:
    {
        'field': 'field_name',
        'message': 'Human readable error',
        'code': 'ERROR_CODE'
    }
    """
```

### Database Error Handling
```python
def handle_database_operations():
    """
    Robust database operation error handling.
    
    Error Types:
    - Connection timeouts
    - Constraint violations
    - Foreign key failures
    - Transaction conflicts
    
    Recovery Strategies:
    - Automatic retry with exponential backoff
    - Graceful degradation for non-critical operations
    - User-friendly error messages
    - Logging for debugging and monitoring
    """
```

---

## File Upload System

### Upload Security
```python
def secure_file_upload():
    """
    Multi-layered file upload security implementation.
    
    Security Measures:
    1. File type validation via extension and MIME type
    2. File size limits to prevent abuse
    3. Filename sanitization to prevent path traversal
    4. User-specific storage isolation
    5. Virus scanning (production requirement)
    6. Access control via Supabase Storage policies
    
    Storage Strategy:
    Path: /referrals/{user_id}/{uuid}-{original_filename}
    Benefits: User isolation, conflict prevention, traceability
    """
```

### Storage Integration
```python
def supabase_storage_integration():
    """
    Supabase Storage integration for medical documents.
    
    Bucket Configuration:
    - referrals: Medical referral documents
    - sleep-data: Study result files (future)
    - reports: Generated reports and summaries
    
    Access Policies:
    - Users can only access their own files
    - Staff can access organization files
    - Doctors can access assigned patient files
    - Admins have full access with audit logging
    
    URL Generation:
    - Signed URLs for temporary access
    - Public URLs for persistent access
    - Expiration handling for security
    """
```

---

## Survey & Assessment Tools

### Epworth Sleepiness Scale
```python
class EpworthSleepinessScale:
    """
    Clinical implementation of the Epworth Sleepiness Scale.
    
    Clinical Background:
    Developed by Dr. Murray Johns in 1991, the Epworth Sleepiness Scale
    is the most widely used measure of daytime sleepiness. It has been
    validated in numerous studies and translated into many languages.
    
    Scoring Interpretation:
    0-5:   Lower Normal daytime sleepiness
    6-10:  Higher Normal daytime sleepiness  
    11-12: Mild excessive daytime sleepiness
    13-15: Moderate excessive daytime sleepiness
    16-24: Severe excessive daytime sleepiness
    
    Clinical Significance:
    Scores >10 suggest investigation for sleep disorders
    Scores >15 strongly suggest sleep apnea evaluation
    """
    
    def calculate_score(self, responses):
        """Calculate total Epworth score from user responses."""
        return sum(int(response) for response in responses.values())
    
    def interpret_score(self, total_score):
        """Provide clinical interpretation of Epworth score."""
        if total_score <= 10:
            return "Normal daytime sleepiness"
        elif total_score <= 15:
            return "Moderate daytime sleepiness"
        else:
            return "High daytime sleepiness - sleep study recommended"
```

### OSA-50 Screening Tool
```python
class OSA50Screening:
    """
    Implementation of the OSA-50 sleep apnea screening questionnaire.
    
    Clinical Purpose:
    The OSA-50 is a validated screening tool for obstructive sleep apnea (OSA)
    developed to identify patients who would benefit from polysomnography.
    It focuses on the most predictive symptoms and risk factors.
    
    Scoring:
    Each "Yes" response = 1 point
    Total possible score: 5 points
    
    Risk Stratification:
    0-2 points: Lower risk for OSA
    3-5 points: Higher risk for OSA (sleep study recommended)
    
    Validation:
    Sensitivity: 94% for detecting moderate-severe OSA
    Specificity: 31% (high sensitivity, lower specificity by design)
    """
    
    def calculate_risk_score(self, responses):
        """Calculate OSA-50 risk score from yes/no responses."""
        return sum(1 for response in responses.values() if response.lower() == 'yes')
    
    def assess_risk_level(self, score):
        """Determine OSA risk level based on score."""
        return "High risk" if score >= 3 else "Low risk"
```

---

## Development Setup

### Local Development
```bash
# 1. Virtual Environment Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Environment Configuration
cp .env.example .env.local
# Edit .env.local with your settings:
# NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
# NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
# FLASK_SECRET_KEY=your_secret_key

# 4. Database Setup
# Run sleep-study-app-ddl.sql in Supabase SQL Editor

# 5. Start Development Server
python app.py
# Access at: http://127.0.0.1:3001
```

### Environment Variables
```bash
# Required environment variables
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
FLASK_SECRET_KEY=your_secure_secret_key_for_sessions

# Optional development variables
FLASK_ENV=development
FLASK_DEBUG=True
```

### Database Setup
```sql
-- Execute in Supabase SQL Editor
-- 1. Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Create tables in dependency order
-- (Execute sleep-study-app-ddl.sql)

-- 3. Set up Row Level Security policies
-- (Follow create-rls-policies guidelines)

-- 4. Create storage buckets
INSERT INTO storage.buckets (id, name, public) 
VALUES ('referrals', 'referrals', false);

-- 5. Set up storage policies
-- (Allow authenticated users to upload/access their files)
```

---

## Database Seeding & Test Data

### Overview
The application includes a comprehensive seeding system that creates a complete test environment with realistic healthcare data for immediate development and testing.

### What Gets Created
```python
"""
Comprehensive test environment includes:
- 3 Healthcare Organizations (Melbourne, Sydney, Brisbane)
- 12 Authenticated Users with pre-confirmed email addresses
- 4 Patient Profiles with detailed medical histories
- 8 Staff Memberships linking users to organizations  
- 6 Sleep Monitoring Devices across all locations
- 4 Sleep Studies in various states (booked, active, completed, review)
- Sample Survey Responses (Epworth Scale, OSA-50)
- Placeholder file records for referrals and reports
"""
```

### Seeding Options

#### 1. Python Script (Direct)
```bash
# Run the comprehensive seeding script
python seed_database.py

# This creates all test data including authenticated users with passwords
```

#### 2. Flask CLI Commands
```bash
# Seed complete test environment
flask seed-database

# Clear all test data
flask clear-database
```

#### 3. From Python Code
```python
import seed_database

# Create complete test environment
seed_database.main()

# Just clear existing test data  
seed_database.clear_existing_data()
```

### Test User Credentials

After seeding, you'll have these **pre-confirmed** login credentials ready for immediate testing:

#### Patients
- **John Smith**: `john.smith@email.com` / `patient123!`
- **Sarah Johnson**: `sarah.johnson@email.com` / `patient456!`
- **Robert Chen**: `robert.chen@email.com` / `patient789!`
- **Emma Williams**: `emma.williams@email.com` / `patient012!`

#### Staff
- **Alice Brown**: `alice.brown@melbournesleep.com.au` / `staff123!`
- **David Taylor**: `david.taylor@sydneysleep.com.au` / `staff456!`
- **Maria Garcia**: `maria.garcia@brisbanesleep.com.au` / `staff789!`

#### Doctors  
- **Dr. Michael Sleep**: `dr.michael.sleep@melbournesleep.com.au` / `doctor123!`
- **Dr. Sarah Respiratory**: `dr.sarah.respiratory@sydneysleep.com.au` / `doctor456!`
- **Dr. James Pulmonary**: `dr.james.pulmonary@brisbanesleep.com.au` / `doctor789!`

#### Admins
- **Melbourne Admin**: `admin.mel@melbournesleep.com.au` / `admin123!`
- **Sydney Admin**: `admin.syd@sydneysleep.com.au` / `admin456!`

### Seeding Implementation Details

#### User Creation Process
```python
def create_users_with_auth():
    """
    Creates authenticated users using Supabase Auth Admin API.
    
    Process:
    1. Uses service role key for admin operations
    2. Creates users with pre-confirmed email addresses
    3. Sets up proper role assignments in app_users table
    4. Creates staff memberships for non-patient users
    5. Returns mapping of created users for relationship building
    
    Benefits:
    - No email verification required (email_confirm: True)
    - Immediate login capability for all test accounts
    - Proper foreign key relationships maintained
    - Realistic organizational structures
    """
```

#### Data Relationships
```python
def create_comprehensive_relationships():
    """
    Creates realistic healthcare data relationships.
    
    Organization Structure:
    - Melbourne: 1 admin, 1 staff, 1 doctor, 2 patients
    - Sydney: 1 admin, 1 staff, 1 doctor, 1 patient  
    - Brisbane: 1 staff, 1 doctor, 1 patient
    
    Medical Data:
    - Patient profiles with insurance, medical history, lifestyle
    - Sleep studies with proper patient-doctor-staff assignments
    - Assessment responses (Epworth Scale: 11 points, OSA-50: risk scores)
    - Device assignments and availability tracking
    """
```

#### Architecture Alignment
```markdown
✅ **Python-based**: No JavaScript dependencies for seeding
✅ **MCP compatible**: Uses Supabase MCP tools for database operations  
✅ **Flask integrated**: CLI commands work seamlessly with your app
✅ **HTMX friendly**: Creates data that works with HTMX workflows
✅ **Production patterns**: Follows same data patterns as production
```

### Development Workflow

#### 1. Initial Setup
```bash
# After cloning repository and setting up environment
python seed_database.py
# Creates complete test environment in ~30 seconds
```

#### 2. Development Testing
```bash
# Test different user roles immediately
# Login as patient: john.smith@email.com / patient123!
# Login as staff: alice.brown@melbournesleep.com.au / staff123!
# Login as doctor: dr.michael.sleep@melbournesleep.com.au / doctor123!
# Login as admin: admin.mel@melbournesleep.com.au / admin123!
```

#### 3. Reset for Clean Testing
```bash
# Clear all test data and reseed
flask clear-database && flask seed-database
```

### Advanced Seeding Features

#### Realistic Medical Data
```python
medical_profiles = {
    'conditions': ['hypertension', 'sleep_apnea', 'diabetes'],
    'medications': ['lisinopril', 'metformin', 'melatonin'],
    'allergies': ['penicillin', 'latex', 'shellfish'],
    'insurance': {
        'provider': 'Medibank Private',
        'policy_number': 'MB123456789',
        'coverage_type': 'hospital_extras'
    }
}
```

#### Clinical Assessment Data
```python
epworth_responses = {
    'q1_sitting_reading': 2,      # 0-3 scale
    'q2_watching_tv': 1,
    'total_score': 11,            # Indicates moderate sleepiness
    'clinical_interpretation': 'Moderate daytime sleepiness'
}

osa50_responses = {
    'loud_snoring': True,
    'daytime_fatigue': True,
    'breathing_cessation': False,
    'high_blood_pressure': True,
    'bmi_over_35': False,
    'total_score': 3,             # High risk threshold
    'risk_level': 'High risk for OSA'
}
```

#### Multi-State Sleep Studies
```python
study_states = {
    'booked': 'Future appointment scheduled',
    'active': 'Currently in progress', 
    'review': 'Awaiting doctor analysis',
    'completed': 'Finished with reports available'
}
```

### Security & Compliance

#### Data Protection
- All seeded data is **synthetic and HIPAA-compliant**
- No real patient information used
- Proper role-based access controls applied
- Audit trail maintained for all seeded operations

#### Production Safety
```python
def production_safety_checks():
    """
    Built-in safeguards prevent accidental production seeding.
    
    Safety Measures:
    - Requires explicit service role key configuration
    - Clears existing data before seeding (prevents conflicts)
    - Uses non-production email domains
    - Provides clear warnings about data replacement
    """
```

For complete seeding documentation, see [`SEEDING_GUIDE.md`](SEEDING_GUIDE.md).

---

## Production Deployment

### Server Configuration
```python
# Production WSGI configuration
def create_production_app():
    """
    Production-ready Flask application configuration.
    
    Security Enhancements:
    - SECRET_KEY from secure environment variable
    - Session cookie security flags
    - HTTPS enforcement
    - CSRF protection
    - Content Security Policy headers
    
    Performance Optimizations:
    - Database connection pooling
    - Static file serving via CDN
    - Response compression
    - Caching strategies
    """
```

### Gunicorn Deployment
```bash
# Install production server
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# With configuration file
gunicorn -c gunicorn.conf.py app:app
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

### Environment Variables (Production)
```bash
# Production environment variables
FLASK_ENV=production
FLASK_SECRET_KEY=<256-bit-secure-random-key>
NEXT_PUBLIC_SUPABASE_URL=<production-supabase-url>
NEXT_PUBLIC_SUPABASE_ANON_KEY=<production-anon-key>

# Optional production settings
DATABASE_POOL_SIZE=10
REDIS_URL=<redis-connection-string>
SENTRY_DSN=<error-tracking-dsn>
```

---

## Testing Strategy

### Unit Testing
```python
import pytest
from app import create_app

def test_booking_flow():
    """
    Test the complete booking flow end-to-end.
    
    Test Cases:
    1. User authentication and session management
    2. Each booking step validation and progression
    3. File upload functionality and security
    4. Assessment score calculations
    5. Database record creation and integrity
    6. Error handling and recovery
    
    Mock Strategy:
    - Mock Supabase client for database operations
    - Mock file upload for storage operations
    - Mock authentication for user sessions
    """
```

### Integration Testing
```python
def test_database_integration():
    """
    Test database operations with real Supabase instance.
    
    Test Environment:
    - Separate test database instance
    - Clean state before each test
    - Transaction rollback after tests
    
    Coverage:
    - User registration and profile creation
    - Sleep study creation with proper foreign keys
    - Survey response storage and retrieval
    - File metadata persistence
    """
```

---

## Security Considerations

### Data Protection
```python
def implement_data_protection():
    """
    Multi-layered data protection strategy.
    
    Encryption:
    - Encryption at rest via Supabase
    - Encryption in transit via HTTPS
    - Session data encryption
    - File upload encryption
    
    Access Control:
    - Role-based permissions
    - Row-level security policies
    - API rate limiting
    - Audit logging for sensitive operations
    
    Privacy:
    - Data minimization principles
    - Consent tracking and management
    - Right to deletion implementation
    - Data export capabilities
    """
```

---

## Performance Optimization

### Database Optimization
```sql
-- Index strategy for common queries
CREATE INDEX idx_sleep_studies_patient_id ON sleep_studies(patient_id);
CREATE INDEX idx_sleep_studies_doctor_id ON sleep_studies(doctor_id);
CREATE INDEX idx_sleep_studies_state ON sleep_studies(current_state);
CREATE INDEX idx_survey_responses_study_id ON survey_responses(sleep_study_id);

-- Query optimization examples
EXPLAIN ANALYZE SELECT * FROM sleep_studies 
WHERE patient_id = $1 AND current_state = 'booked';
```

## Troubleshooting Guide

### Common Issues

#### Authentication Problems
```python
def debug_authentication():
    """
    Common authentication issues and solutions.
    
    Issue: "Invalid credentials" error
    Solution: 
    - Verify Supabase URL and anon key
    - Check user exists in auth.users table
    - Validate password complexity requirements
    
    Issue: Session timeout
    Solution:
    - Implement token refresh mechanism
    - Check session configuration
    - Verify cookie security settings
    """
```

#### Booking Flow Issues
```python
def debug_booking_flow():
    """
    Troubleshooting booking process problems.
    
    Issue: Step progression fails
    Solution:
    - Check session data integrity
    - Validate form data completeness
    - Verify HTMX endpoint responses
    
    Issue: File upload failures
    Solution:
    - Check file size and type restrictions
    - Verify storage bucket permissions
    - Test network connectivity
    
    Issue: Database constraint violations
    Solution:
    - Verify foreign key relationships
    - Check required field completion
    - Validate data types and formats
    """
```

#### Performance Issues
```python
def debug_performance():
    """
    Performance troubleshooting methodology.
    
    Database Performance:
    - Analyze slow query logs
    - Check index usage with EXPLAIN
    - Monitor connection pool status
    - Review query optimization opportunities
    
    Application Performance:
    - Profile Python code execution
    - Monitor memory usage patterns
    - Check for N+1 query problems
    - Analyze request/response times
    
    Frontend Performance:
    - Measure page load times
    - Check network waterfall charts
    - Analyze JavaScript execution time
    - Review resource loading patterns
    """
```

### Error Codes Reference
```python
ERROR_CODES = {
    'AUTH_001': 'Invalid credentials provided',
    'AUTH_002': 'Session expired, please login again',
    'AUTH_003': 'Insufficient permissions for this action',
    
    'BOOK_001': 'Selected appointment time no longer available',
    'BOOK_002': 'Required fields missing in booking form',
    'BOOK_003': 'File upload failed - invalid file type',
    'BOOK_004': 'Assessment responses incomplete',
    'BOOK_005': 'Database error during booking creation',
    
    'SYS_001': 'Database connection unavailable',
    'SYS_002': 'External service temporarily unavailable',
    'SYS_003': 'Rate limit exceeded, please try again later'
}
```

### Debug Mode Configuration
```python
def enable_debug_mode():
    """
    Development debugging configuration.
    
    Debug Features:
    - Detailed error pages with stack traces
    - SQL query logging and timing
    - Session data inspection tools
    - Request/response logging
    - Performance profiling data
    
    Security Warning:
    Never enable debug mode in production as it exposes
    sensitive application internals and security vulnerabilities.
    """
```

---

**Last Updated**: June 2025  
**Version**: 1.1.0 (Enhanced RLS & Multi-Tenant Support)
**Technology Stack**: Flask + HTMX + Supabase + Advanced RLS Policies  
