# Database Seeding Guide

This guide explains how to populate your sleep study app with comprehensive test data for development and testing.

## Overview

The seeding system creates:
- **3 Healthcare Organizations** (Melbourne, Sydney, Brisbane)
- **12 Authenticated Users** across all roles with passwords
- **4 Patient Profiles** with detailed medical histories  
- **8 Staff Memberships** linking users to organizations
- **6 Sleep Monitoring Devices** across all locations
- **4 Sleep Studies** in various states
- **Sample Data** (surveys, referrals, reports)

## Usage Options

### 1. Python Script (Direct)
```bash
# Run the seeding script directly
python seed_database.py
```

### 2. Flask CLI Commands
```bash
# Seed the database
flask seed-database

# Clear all test data
flask clear-database
```

### 3. From Python Code
```python
import seed_database

# Seed the database
seed_database.main()

# Just clear data
seed_database.clear_existing_data()
```

## Test User Credentials

After seeding, you'll have these login credentials:

### Patients
- **John Smith**: `john.smith@email.com` / `patient123!`
- **Sarah Johnson**: `sarah.johnson@email.com` / `patient456!`
- **Robert Chen**: `robert.chen@email.com` / `patient789!`
- **Emma Williams**: `emma.williams@email.com` / `patient012!`

### Staff
- **Alice Brown**: `alice.brown@melbournesleep.com.au` / `staff123!`
- **David Taylor**: `david.taylor@sydneysleep.com.au` / `staff456!`
- **Maria Garcia**: `maria.garcia@brisbanesleep.com.au` / `staff789!`

### Doctors  
- **Dr. Michael Sleep**: `dr.michael.sleep@melbournesleep.com.au` / `doctor123!`
- **Dr. Sarah Respiratory**: `dr.sarah.respiratory@sydneysleep.com.au` / `doctor456!`
- **Dr. James Pulmonary**: `dr.james.pulmonary@brisbanesleep.com.au` / `doctor789!`

### Admins
- **Melbourne Admin**: `admin.mel@melbournesleep.com.au` / `admin123!`
- **Sydney Admin**: `admin.syd@sydneysleep.com.au` / `admin456!`

## Features

- ✅ **Pre-confirmed users** - No email verification needed
- ✅ **Realistic test data** - Medical histories, insurance details, etc.
- ✅ **Multi-organization setup** - Test cross-organization workflows
- ✅ **Various study states** - Booked, active, completed, review
- ✅ **Sample relationships** - Patient-doctor assignments, device usage
- ✅ **File placeholders** - Referrals, sleep data, reports

## Architecture Alignment

This seeding approach aligns with your app's principles:
- **Python-based** - No JavaScript dependencies
- **Flask integrated** - CLI commands work with your Flask app
- **MCP compatible** - Uses Supabase MCP tools for database operations
- **HTMX friendly** - Creates data that works with your HTMX workflows

## Safety

- Clears existing test data before seeding
- Uses transactions where possible
- Provides detailed logging and error handling
- Only affects your remote Supabase database (no local dependencies) 