#!/usr/bin/env python3
"""
Sleep Study App Database Seeding Script

This script creates a complete test environment with:
- 3 healthcare organizations 
- 13 authenticated users (patients, staff, doctors, admins) with passwords
- Patient profiles with medical histories
- Staff memberships linking users to organizations
- Sleep monitoring devices
- Sample sleep studies and survey responses

All users are pre-confirmed and can log in immediately for testing.
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv('.env.local')

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ Error: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in "
          ".env.local")
    sys.exit(1)

# Initialize Supabase client with service role for admin operations
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def clear_existing_data():
    """Clear all existing test data in reverse dependency order"""
    print("🧹 Clearing existing data...")
    
    try:
        # Delete in reverse dependency order
        supabase.table('doctor_reports').delete().neq(
            'id', '00000000-0000-0000-0000-000000000000').execute()
        supabase.table('sleep_data_files').delete().neq(
            'id', '00000000-0000-0000-0000-000000000000').execute()
        supabase.table('survey_responses').delete().neq(
            'id', '00000000-0000-0000-0000-000000000000').execute()
        supabase.table('referrals').delete().neq(
            'id', '00000000-0000-0000-0000-000000000000').execute()
        supabase.table('sleep_studies').delete().neq(
            'id', '00000000-0000-0000-0000-000000000000').execute()
        supabase.table('devices').delete().neq(
            'id', '00000000-0000-0000-0000-000000000000').execute()
        supabase.table('patient_profiles').delete().neq(
            'user_id', '00000000-0000-0000-0000-000000000000').execute()
        supabase.table('staff_memberships').delete().neq(
            'id', '00000000-0000-0000-0000-000000000000').execute()
        supabase.table('app_users').delete().neq(
            'id', '00000000-0000-0000-0000-000000000000').execute()
        supabase.table('organizations').delete().neq(
            'id', '00000000-0000-0000-0000-000000000000').execute()
        
        print("✅ Existing data cleared successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not clear some data: {e}")

def create_organizations():
    """Create healthcare organizations"""
    print("🏥 Creating healthcare organizations...")
    
    organizations = [
        {
            'id': '01234567-89ab-cdef-0123-456789abcdef',
            'name': 'Melbourne Sleep Health Centre',
            'organization_details': {
                'address': '123 Collins Street, Melbourne VIC 3000',
                'phone': '(03) 9123-4567',
                'email': 'contact@melbournesleep.com.au',
                'type': 'sleep_clinic',
                'services': ['in_lab_studies', 'home_studies', 'cpap_therapy']
            },
            'opening_hours': {
                'monday': {'open': '08:00', 'close': '18:00'},
                'tuesday': {'open': '08:00', 'close': '18:00'},
                'wednesday': {'open': '08:00', 'close': '18:00'},
                'thursday': {'open': '08:00', 'close': '18:00'},
                'friday': {'open': '08:00', 'close': '17:00'},
                'saturday': {'open': '09:00', 'close': '13:00'},
                'sunday': 'closed'
            },
            'max_concurrent_studies': 15
        },
        {
            'id': '12345678-9abc-def0-1234-56789abcdef0',
            'name': 'Sydney Sleep Solutions',
            'organization_details': {
                'address': '456 George Street, Sydney NSW 2000',
                'phone': '(02) 8234-5678',
                'email': 'info@sydneysleep.com.au',
                'type': 'sleep_clinic',
                'services': ['in_lab_studies', 'home_studies', 'sleep_surgery_consultation']
            },
            'opening_hours': {
                'monday': {'open': '07:30', 'close': '19:00'},
                'tuesday': {'open': '07:30', 'close': '19:00'},
                'wednesday': {'open': '07:30', 'close': '19:00'},
                'thursday': {'open': '07:30', 'close': '19:00'},
                'friday': {'open': '07:30', 'close': '18:00'},
                'saturday': {'open': '08:00', 'close': '14:00'},
                'sunday': 'closed'
            },
            'max_concurrent_studies': 20
        },
        {
            'id': '23456789-abcd-ef01-2345-6789abcdef01',
            'name': 'Brisbane Respiratory & Sleep Clinic',
            'organization_details': {
                'address': '789 Queen Street, Brisbane QLD 4000',
                'phone': '(07) 3345-6789',
                'email': 'appointments@brisbanesleep.com.au',
                'type': 'sleep_clinic',
                'services': ['in_lab_studies', 'home_studies', 'respiratory_therapy']
            },
            'opening_hours': {
                'monday': {'open': '08:00', 'close': '17:30'},
                'tuesday': {'open': '08:00', 'close': '17:30'},
                'wednesday': {'open': '08:00', 'close': '17:30'},
                'thursday': {'open': '08:00', 'close': '17:30'},
                'friday': {'open': '08:00', 'close': '16:30'},
                'saturday': 'closed',
                'sunday': 'closed'
            },
            'max_concurrent_studies': 12
        }
    ]
    
    result = supabase.table('organizations').insert(organizations).execute()
    print(f"✅ Created {len(result.data)} organizations")
    return {org['id']: org for org in organizations}

def create_users_with_auth():
    """Create authenticated users with passwords and app_users entries"""
    print("👥 Creating authenticated users...")
    
    users_data = [
        # Patients
        {
            'id': '34567890-bcde-f012-3456-789abcdef012',
            'email': 'john.smith@email.com',
            'password': 'patient123!',
            'role': 'patient',
            'user_metadata': {
                'first_name': 'John',
                'last_name': 'Smith',
                'role': 'patient'
            }
        },
        {
            'id': '45678901-cdef-0123-4567-89abcdef0123',
            'email': 'sarah.johnson@email.com',
            'password': 'patient456!',
            'role': 'patient',
            'user_metadata': {
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': 'patient'
            }
        },
        {
            'id': '56789012-def0-1234-5678-9abcdef01234',
            'email': 'robert.chen@email.com',
            'password': 'patient789!',
            'role': 'patient',
            'user_metadata': {
                'first_name': 'Robert',
                'last_name': 'Chen',
                'role': 'patient'
            }
        },
        {
            'id': '67890123-ef01-2345-6789-abcdef012345',
            'email': 'emma.williams@email.com',
            'password': 'patient012!',
            'role': 'patient',
            'user_metadata': {
                'first_name': 'Emma',
                'last_name': 'Williams',
                'role': 'patient'
            }
        },
        # Staff
        {
            'id': '78901234-f012-3456-789a-bcdef0123456',
            'email': 'alice.brown@melbournesleep.com.au',
            'password': 'staff123!',
            'role': 'staff',
            'user_metadata': {
                'first_name': 'Alice',
                'last_name': 'Brown',
                'role': 'staff'
            }
        },
        {
            'id': '89012345-0123-4567-89ab-cdef01234567',
            'email': 'david.taylor@sydneysleep.com.au',
            'password': 'staff456!',
            'role': 'staff',
            'user_metadata': {
                'first_name': 'David',
                'last_name': 'Taylor',
                'role': 'staff'
            }
        },
        {
            'id': '90123456-1234-5678-9abc-def012345678',
            'email': 'maria.garcia@brisbanesleep.com.au',
            'password': 'staff789!',
            'role': 'staff',
            'user_metadata': {
                'first_name': 'Maria',
                'last_name': 'Garcia',
                'role': 'staff'
            }
        },
        # Doctors
        {
            'id': 'a0123456-2345-6789-abcd-ef0123456789',
            'email': 'dr.michael.sleep@melbournesleep.com.au',
            'password': 'doctor123!',
            'role': 'doctor',
            'user_metadata': {
                'first_name': 'Dr. Michael',
                'last_name': 'Sleep',
                'role': 'doctor'
            }
        },
        {
            'id': 'b1234567-3456-789a-bcde-f01234567890',
            'email': 'dr.sarah.respiratory@sydneysleep.com.au',
            'password': 'doctor456!',
            'role': 'doctor',
            'user_metadata': {
                'first_name': 'Dr. Sarah',
                'last_name': 'Respiratory',
                'role': 'doctor'
            }
        },
        {
            'id': 'c2345678-4567-89ab-cdef-012345678901',
            'email': 'dr.james.pulmonary@brisbanesleep.com.au',
            'password': 'doctor789!',
            'role': 'doctor',
            'user_metadata': {
                'first_name': 'Dr. James',
                'last_name': 'Pulmonary',
                'role': 'doctor'
            }
        },
        # Admins
        {
            'id': 'd3456789-5678-9abc-def0-123456789012',
            'email': 'admin.mel@melbournesleep.com.au',
            'password': 'admin123!',
            'role': 'admin',
            'user_metadata': {
                'first_name': 'Melbourne',
                'last_name': 'Admin',
                'role': 'admin'
            }
        },
        {
            'id': 'e4567890-6789-abcd-ef01-234567890123',
            'email': 'admin.syd@sydneysleep.com.au',
            'password': 'admin456!',
            'role': 'admin',
            'user_metadata': {
                'first_name': 'Sydney',
                'last_name': 'Admin',
                'role': 'admin'
            }
        }
    ]
    
    created_users = {}
    
    for user_data in users_data:
        try:
            # Create auth user with email confirmation pre-set
            auth_response = supabase.auth.admin.create_user({
                'email': user_data['email'],
                'password': user_data['password'],
                'user_metadata': user_data['user_metadata'],
                'email_confirm': True  # Pre-confirm user
            })
            
            if auth_response.user:
                # Create corresponding app_users entry
                app_user_data = {
                    'id': auth_response.user.id,
                    'role': user_data['role']
                }
                
                supabase.table('app_users').insert(app_user_data).execute()
                
                created_users[user_data['id']] = {
                    'actual_id': auth_response.user.id,
                    'email': user_data['email'],
                    'password': user_data['password'],
                    'role': user_data['role'],
                    'name': f"{user_data['user_metadata']['first_name']} {user_data['user_metadata']['last_name']}"
                }
                
                print(f"✅ Created user: {user_data['email']} (ID: {auth_response.user.id})")
            else:
                print(f"❌ Failed to create user: {user_data['email']}")
                
        except Exception as e:
            print(f"❌ Error creating user {user_data['email']}: {e}")
    
    print(f"✅ Created {len(created_users)} authenticated users")
    return created_users

def create_patient_profiles(created_users):
    """Create patient profiles for patient users"""
    print("👤 Creating patient profiles...")
    
    patient_users = {k: v for k, v in created_users.items() if v['role'] == 'patient'}
    
    # Map emails to profile data
    profile_data_map = {
        'john.smith@email.com': {
            'first_name': 'John',
            'last_name': 'Smith',
            'date_of_birth': '1985-03-15',
            'gender': 'male',
            'phone': '(03) 9876-5432',
            'address': {
                'street': '45 Bourke Street',
                'suburb': 'Melbourne',
                'state': 'VIC',
                'postcode': '3000'
            },
            'emergency_contact': {
                'name': 'Jane Smith',
                'relationship': 'spouse',
                'phone': '(03) 9876-5433'
            },
            'medical_history': {
                'conditions': ['hypertension', 'mild_sleep_apnea'],
                'medications': ['lisinopril', 'melatonin'],
                'allergies': ['penicillin'],
                'previous_sleep_studies': False
            },
            'insurance': {
                'provider': 'Medibank Private',
                'policy_number': 'MB123456789',
                'coverage_type': 'hospital_extras'
            },
            'lifestyle': {
                'smoking': False,
                'alcohol_consumption': 'moderate',
                'exercise_frequency': '3_times_week',
                'caffeine_intake': 'moderate'
            }
        },
        'sarah.johnson@email.com': {
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'date_of_birth': '1978-07-22',
            'gender': 'female',
            'phone': '(02) 8765-4321',
            'address': {
                'street': '12 Pitt Street',
                'suburb': 'Sydney',
                'state': 'NSW',
                'postcode': '2000'
            },
            'emergency_contact': {
                'name': 'Michael Johnson',
                'relationship': 'husband',
                'phone': '(02) 8765-4322'
            },
            'medical_history': {
                'conditions': ['fibromyalgia', 'insomnia'],
                'medications': ['pregabalin', 'zolpidem'],
                'allergies': [],
                'previous_sleep_studies': True
            },
            'insurance': {
                'provider': 'BUPA',
                'policy_number': 'BP987654321',
                'coverage_type': 'comprehensive'
            },
            'lifestyle': {
                'smoking': False,
                'alcohol_consumption': 'low',
                'exercise_frequency': 'daily',
                'caffeine_intake': 'high'
            }
        },
        'robert.chen@email.com': {
            'first_name': 'Robert',
            'last_name': 'Chen',
            'date_of_birth': '1992-11-08',
            'gender': 'male',
            'phone': '(07) 3456-7890',
            'address': {
                'street': '88 Adelaide Street',
                'suburb': 'Brisbane',
                'state': 'QLD',
                'postcode': '4000'
            },
            'emergency_contact': {
                'name': 'Lisa Chen',
                'relationship': 'sister',
                'phone': '(07) 3456-7891'
            },
            'medical_history': {
                'conditions': ['anxiety', 'restless_leg_syndrome'],
                'medications': ['sertraline', 'ropinirole'],
                'allergies': ['shellfish'],
                'previous_sleep_studies': False
            },
            'insurance': {
                'provider': 'HCF',
                'policy_number': 'HCF555666777',
                'coverage_type': 'basic_plus'
            },
            'lifestyle': {
                'smoking': False,
                'alcohol_consumption': 'low',
                'exercise_frequency': 'occasionally',
                'caffeine_intake': 'very_high'
            }
        },
        'emma.williams@email.com': {
            'first_name': 'Emma',
            'last_name': 'Williams',
            'date_of_birth': '1969-04-30',
            'gender': 'female',
            'phone': '(03) 9234-5678',
            'address': {
                'street': '67 Flinders Lane',
                'suburb': 'Melbourne',
                'state': 'VIC',
                'postcode': '3000'
            },
            'emergency_contact': {
                'name': 'David Williams',
                'relationship': 'husband',
                'phone': '(03) 9234-5679'
            },
            'medical_history': {
                'conditions': ['type_2_diabetes', 'severe_sleep_apnea'],
                'medications': ['metformin', 'insulin'],
                'allergies': ['latex'],
                'previous_sleep_studies': True
            },
            'insurance': {
                'provider': 'NIB',
                'policy_number': 'NIB888999000',
                'coverage_type': 'top_hospital'
            },
            'lifestyle': {
                'smoking': True,
                'alcohol_consumption': 'moderate',
                'exercise_frequency': 'rarely',
                'caffeine_intake': 'low'
            }
        }
    }
    
    profiles = []
    for user_data in patient_users.values():
        if user_data['email'] in profile_data_map:
            profile = {
                'user_id': user_data['actual_id'],
                'patient_details': profile_data_map[user_data['email']]
            }
            profiles.append(profile)
    
    if profiles:
        result = supabase.table('patient_profiles').insert(profiles).execute()
        print(f"✅ Created {len(result.data)} patient profiles")
    
    return profiles

def create_staff_memberships(created_users, organizations):
    """Create staff memberships linking users to organizations"""
    print("🏢 Creating staff memberships...")
    
    # Get non-patient users
    staff_users = {k: v for k, v in created_users.items() if v['role'] != 'patient'}
    
    # Define membership mappings by email
    membership_map = {
        'alice.brown@melbournesleep.com.au': {
            'org_id': '01234567-89ab-cdef-0123-456789abcdef',
            'role_details': {
                'title': 'Senior Sleep Technician',
                'department': 'clinical_operations',
                'permissions': ['manage_studies', 'view_reports', 'schedule_appointments'],
                'contact': {
                    'email': 'alice.brown@melbournesleep.com.au',
                    'phone': '(03) 9123-4568',
                    'extension': '101'
                },
                'schedule': {
                    'full_time': True,
                    'shift_pattern': 'day_shift',
                    'on_call': True
                }
            }
        },
        'david.taylor@sydneysleep.com.au': {
            'org_id': '12345678-9abc-def0-1234-56789abcdef0',
            'role_details': {
                'title': 'Patient Coordinator',
                'department': 'patient_services',
                'permissions': ['schedule_appointments', 'manage_patient_records', 'billing_support'],
                'contact': {
                    'email': 'david.taylor@sydneysleep.com.au',
                    'phone': '(02) 8234-5679',
                    'extension': '201'
                },
                'schedule': {
                    'full_time': True,
                    'shift_pattern': 'day_shift',
                    'on_call': False
                }
            }
        },
        'maria.garcia@brisbanesleep.com.au': {
            'org_id': '23456789-abcd-ef01-2345-6789abcdef01',
            'role_details': {
                'title': 'Clinical Assistant',
                'department': 'clinical_operations',
                'permissions': ['assist_studies', 'equipment_maintenance', 'patient_preparation'],
                'contact': {
                    'email': 'maria.garcia@brisbanesleep.com.au',
                    'phone': '(07) 3345-6790',
                    'extension': '301'
                },
                'schedule': {
                    'full_time': False,
                    'shift_pattern': 'evening_shift',
                    'on_call': True
                }
            }
        },
        'dr.michael.sleep@melbournesleep.com.au': {
            'org_id': '01234567-89ab-cdef-0123-456789abcdef',
            'role_details': {
                'title': 'Sleep Medicine Specialist',
                'department': 'medical',
                'permissions': ['diagnose_studies', 'write_reports', 'manage_patients'],
                'contact': {
                    'email': 'dr.michael.sleep@melbournesleep.com.au',
                    'phone': '(03) 9123-4569',
                    'extension': '102'
                },
                'schedule': {
                    'full_time': True,
                    'shift_pattern': 'business_hours',
                    'on_call': True
                }
            }
        },
        'dr.sarah.respiratory@sydneysleep.com.au': {
            'org_id': '12345678-9abc-def0-1234-56789abcdef0',
            'role_details': {
                'title': 'Respiratory & Sleep Physician',
                'department': 'medical',
                'permissions': ['diagnose_studies', 'write_reports', 'surgical_consultation'],
                'contact': {
                    'email': 'dr.sarah.respiratory@sydneysleep.com.au',
                    'phone': '(02) 8234-5680',
                    'extension': '202'
                },
                'schedule': {
                    'full_time': True,
                    'shift_pattern': 'business_hours',
                    'on_call': False
                }
            }
        },
        'dr.james.pulmonary@brisbanesleep.com.au': {
            'org_id': '23456789-abcd-ef01-2345-6789abcdef01',
            'role_details': {
                'title': 'Pulmonologist',
                'department': 'medical',
                'permissions': ['diagnose_studies', 'write_reports', 'respiratory_therapy'],
                'contact': {
                    'email': 'dr.james.pulmonary@brisbanesleep.com.au',
                    'phone': '(07) 3345-6791',
                    'extension': '302'
                },
                'schedule': {
                    'full_time': True,
                    'shift_pattern': 'business_hours',
                    'on_call': True
                }
            }
        },
        'admin.mel@melbournesleep.com.au': {
            'org_id': '01234567-89ab-cdef-0123-456789abcdef',
            'role_details': {
                'title': 'Clinic Manager',
                'department': 'administration',
                'permissions': ['full_admin', 'user_management', 'financial_reports', 'system_configuration'],
                'contact': {
                    'email': 'admin.mel@melbournesleep.com.au',
                    'phone': '(03) 9123-4500',
                    'extension': '100'
                },
                'schedule': {
                    'full_time': True,
                    'shift_pattern': 'business_hours',
                    'on_call': True
                }
            }
        },
        'admin.syd@sydneysleep.com.au': {
            'org_id': '12345678-9abc-def0-1234-56789abcdef0',
            'role_details': {
                'title': 'Operations Director',
                'department': 'administration',
                'permissions': ['full_admin', 'user_management', 'financial_reports', 'multi_site_management'],
                'contact': {
                    'email': 'admin.syd@sydneysleep.com.au',
                    'phone': '(02) 8234-5600',
                    'extension': '200'
                },
                'schedule': {
                    'full_time': True,
                    'shift_pattern': 'business_hours',
                    'on_call': False
                }
            }
        }
    }
    
    memberships = []
    for user_data in staff_users.values():
        if user_data['email'] in membership_map:
            mapping = membership_map[user_data['email']]
            membership = {
                'user_id': user_data['actual_id'],
                'organization_id': mapping['org_id'],
                'role_details': mapping['role_details']
            }
            memberships.append(membership)
    
    if memberships:
        result = supabase.table('staff_memberships').insert(memberships).execute()
        print(f"✅ Created {len(result.data)} staff memberships")
    
    return memberships

def create_devices(organizations):
    """Create sleep monitoring devices"""
    print("🔬 Creating sleep monitoring devices...")
    
    devices = [
        # Melbourne devices
        {
            'organization_id': '01234567-89ab-cdef-0123-456789abcdef',
            'device_details': {
                'type': 'psg_system',
                'brand': 'Natus',
                'model': 'SleepWorks',
                'serial_number': 'NTS-2024-001',
                'location': 'Room 1',
                'capabilities': ['eeg', 'eog', 'emg', 'respiratory', 'cardiac'],
                'last_calibration': '2024-11-01',
                'next_maintenance': '2025-02-01'
            },
            'status': 'available'
        },
        {
            'organization_id': '01234567-89ab-cdef-0123-456789abcdef',
            'device_details': {
                'type': 'home_sleep_test',
                'brand': 'ResMed',
                'model': 'ApneaLink Air',
                'serial_number': 'RSM-2024-002',
                'location': 'Equipment Pool',
                'capabilities': ['respiratory', 'oxygen_saturation', 'pulse_rate'],
                'last_calibration': '2024-10-15',
                'next_maintenance': '2025-01-15'
            },
            'status': 'available'
        },
        # Sydney devices
        {
            'organization_id': '12345678-9abc-def0-1234-56789abcdef0',
            'device_details': {
                'type': 'psg_system',
                'brand': 'Compumedics',
                'model': 'Grael',
                'serial_number': 'CMP-2024-003',
                'location': 'Room A',
                'capabilities': ['eeg', 'eog', 'emg', 'respiratory', 'cardiac', 'video'],
                'last_calibration': '2024-11-10',
                'next_maintenance': '2025-02-10'
            },
            'status': 'available'
        },
        {
            'organization_id': '12345678-9abc-def0-1234-56789abcdef0',
            'device_details': {
                'type': 'cpap_machine',
                'brand': 'Philips',
                'model': 'DreamStation 2',
                'serial_number': 'PHL-2024-004',
                'location': 'Therapy Room',
                'capabilities': ['auto_pressure', 'ramp', 'humidification', 'data_recording'],
                'last_calibration': '2024-10-20',
                'next_maintenance': '2025-01-20'
            },
            'status': 'available'
        },
        # Brisbane devices
        {
            'organization_id': '23456789-abcd-ef01-2345-6789abcdef01',
            'device_details': {
                'type': 'home_sleep_test',
                'brand': 'Itamar Medical',
                'model': 'WatchPAT ONE',
                'serial_number': 'ITM-2024-005',
                'location': 'Equipment Pool',
                'capabilities': ['pat_signal', 'heart_rate', 'oxygen_saturation', 'sleep_position'],
                'last_calibration': '2024-11-05',
                'next_maintenance': '2025-02-05'
            },
            'status': 'available'
        },
        {
            'organization_id': '23456789-abcd-ef01-2345-6789abcdef01',
            'device_details': {
                'type': 'psg_system',
                'brand': 'Nihon Kohden',
                'model': 'Polymate Pro',
                'serial_number': 'NKD-2024-006',
                'location': 'Room 1',
                'capabilities': ['eeg', 'eog', 'emg', 'respiratory', 'cardiac'],
                'last_calibration': '2024-10-30',
                'next_maintenance': '2025-01-30'
            },
            'status': 'available'
        }
    ]
    
    result = supabase.table('devices').insert(devices).execute()
    print(f"✅ Created {len(result.data)} devices")
    return result.data

def create_sleep_studies(created_users, devices):
    """Create sample sleep studies"""
    print("🛏️ Creating sleep studies...")
    
    # Get user IDs by email for easier mapping
    user_email_map = {v['email']: v['actual_id'] for v in created_users.values()}
    
    # Get device IDs by serial number
    device_serial_map = {d['device_details']['serial_number']: d['id'] for d in devices}
    
    studies = [
        {
            'patient_id': user_email_map['john.smith@email.com'],
            'manager_id': user_email_map['alice.brown@melbournesleep.com.au'],
            'doctor_id': user_email_map['dr.michael.sleep@melbournesleep.com.au'],
            'device_id': device_serial_map['NTS-2024-001'],
            'current_state': 'completed',
            'start_date': '2024-11-15',
            'end_date': '2024-11-16'
        },
        {
            'patient_id': user_email_map['sarah.johnson@email.com'],
            'manager_id': user_email_map['david.taylor@sydneysleep.com.au'],
            'doctor_id': user_email_map['dr.sarah.respiratory@sydneysleep.com.au'],
            'device_id': device_serial_map['CMP-2024-003'],
            'current_state': 'active',
            'start_date': '2024-12-01',
            'end_date': None
        },
        {
            'patient_id': user_email_map['robert.chen@email.com'],
            'manager_id': user_email_map['maria.garcia@brisbanesleep.com.au'],
            'doctor_id': user_email_map['dr.james.pulmonary@brisbanesleep.com.au'],
            'device_id': device_serial_map['ITM-2024-005'],
            'current_state': 'booked',
            'start_date': '2024-12-15',
            'end_date': None
        },
        {
            'patient_id': user_email_map['emma.williams@email.com'],
            'manager_id': user_email_map['alice.brown@melbournesleep.com.au'],
            'doctor_id': user_email_map['dr.michael.sleep@melbournesleep.com.au'],
            'device_id': device_serial_map['RSM-2024-002'],
            'current_state': 'review',
            'start_date': '2024-11-25',
            'end_date': '2024-11-26'
        }
    ]
    
    result = supabase.table('sleep_studies').insert(studies).execute()
    print(f"✅ Created {len(result.data)} sleep studies")
    return result.data

def create_sample_data(sleep_studies, created_users):
    """Create sample survey responses and file records"""
    print("📊 Creating sample survey responses and file records...")
    
    user_email_map = {v['email']: v['actual_id'] for v in created_users.values()}
    
    # Find studies by patient email
    john_study = next(s for s in sleep_studies if s['patient_id'] == user_email_map['john.smith@email.com'])
    sarah_study = next(s for s in sleep_studies if s['patient_id'] == user_email_map['sarah.johnson@email.com'])
    
    # Survey responses
    surveys = [
        {
            'sleep_study_id': john_study['id'],
            'type': 'epworth_sleepiness_scale',
            'answers': {
                'q1_sitting_reading': 2,
                'q2_watching_tv': 1,
                'q3_sitting_inactive_public': 0,
                'q4_passenger_car_hour': 2,
                'q5_lying_down_afternoon': 3,
                'q6_sitting_talking': 0,
                'q7_sitting_quietly_lunch': 1,
                'q8_car_traffic_stopped': 2
            },
            'score': 11
        },
        {
            'sleep_study_id': sarah_study['id'],
            'type': 'pittsburgh_sleep_quality',
            'answers': {
                'bedtime': '23:30',
                'sleep_latency': 45,
                'wake_time': '07:00',
                'sleep_duration': 6,
                'sleep_efficiency': 85,
                'sleep_disturbances': 2,
                'sleep_medication': 3,
                'daytime_dysfunction': 2
            },
            'score': 8
        }
    ]
    
    supabase.table('survey_responses').insert(surveys).execute()
    
    # Sample file records (placeholders for real file uploads)
    referrals = [
        {
            'sleep_study_id': john_study['id'],
            'file_url': 'https://storage.example.com/referrals/john_smith_referral.pdf'
        }
    ]
    
    sleep_data = [
        {
            'sleep_study_id': john_study['id'],
            'file_url': 'https://storage.example.com/sleep_data/john_smith_study_data.edf'
        }
    ]
    
    reports = [
        {
            'sleep_study_id': john_study['id'],
            'file_url': 'https://storage.example.com/reports/john_smith_final_report.pdf'
        }
    ]
    
    supabase.table('referrals').insert(referrals).execute()
    supabase.table('sleep_data_files').insert(sleep_data).execute()
    supabase.table('doctor_reports').insert(reports).execute()
    
    print("✅ Created sample survey responses and file records")

def print_login_credentials(created_users):
    """Print all user credentials for testing"""
    print("\n" + "="*80)
    print("🔑 TEST USER LOGIN CREDENTIALS")
    print("="*80)
    
    # Group by role
    roles = {}
    for user_data in created_users.values():
        role = user_data['role']
        if role not in roles:
            roles[role] = []
        roles[role].append(user_data)
    
    for role, users in roles.items():
        print(f"\n{role.upper()}S:")
        print("-" * 40)
        for user in users:
            print(f"  Name: {user['name']}")
            print(f"  Email: {user['email']}")
            print(f"  Password: {user['password']}")
            print(f"  ID: {user['actual_id']}")
            print()
    
    print("="*80)
    print("All users are pre-confirmed and can log in immediately!")
    print("Use these credentials to test different user roles in your Flask app.")
    print("="*80)

def main():
    """Main seeding function"""
    print("🌱 Starting Sleep Study App Database Seeding...")
    print(f"🎯 Target: {SUPABASE_URL}")
    
    try:
        # Clear existing data
        clear_existing_data()
        
        # Create base data
        organizations = create_organizations()
        created_users = create_users_with_auth()
        
        if not created_users:
            print("❌ No users were created. Aborting seeding.")
            return
        
        # Create related data
        create_patient_profiles(created_users)
        create_staff_memberships(created_users, organizations)
        devices = create_devices(organizations)
        sleep_studies = create_sleep_studies(created_users, devices)
        create_sample_data(sleep_studies, created_users)
        
        # Print credentials
        print_login_credentials(created_users)
        
        print("\n🎉 Database seeding completed successfully!")
        print("Your sleep study app now has comprehensive test data.")
        
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 