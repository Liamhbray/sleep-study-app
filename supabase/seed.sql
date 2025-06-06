-- =============================================================================
-- Sleep Study App - Development Seed Data
-- =============================================================================
-- This file is automatically executed after migrations when running:
-- - supabase start
-- - supabase db reset
-- 
-- Creates sample data for development and testing including:
-- - Healthcare organizations
-- - Users for each role (admin, doctor, staff, patient)
-- - Devices, studies, and related records
-- =============================================================================

-- Clear existing data (for development only)
delete from public.doctor_reports;
delete from public.sleep_data_files;
delete from public.survey_responses;
delete from public.referrals;
delete from public.sleep_studies;
delete from public.devices;
delete from public.staff_memberships;
delete from public.patient_profiles;
delete from public.app_users;
delete from public.organizations;
delete from auth.users where email like '%@melbournesleep.com.au' 
  or email like '%@sydneysleep.org.au' 
  or email like '%@brisbanesleep.health'
  or email like '%patient%@gmail.com';

-- =============================================================================
-- ORGANIZATIONS
-- =============================================================================

insert into public.organizations (id, name, organization_details, opening_hours, max_concurrent_studies) values
(
  '10000000-0000-0000-0000-000000000001',
  'Melbourne Sleep Clinic',
  '{
    "address": "123 Collins Street, Melbourne VIC 3000",
    "phone": "+61 3 9123 4567",
    "email": "contact@melbournesleep.com.au",
    "license_number": "HSC-VIC-2024-001",
    "specializations": ["Sleep Apnea", "Insomnia", "Narcolepsy"]
  }',
  '{
    "monday": {"open": "08:00", "close": "18:00"},
    "tuesday": {"open": "08:00", "close": "18:00"},
    "wednesday": {"open": "08:00", "close": "18:00"},
    "thursday": {"open": "08:00", "close": "18:00"},
    "friday": {"open": "08:00", "close": "17:00"},
    "saturday": {"open": null, "close": null},
    "sunday": {"open": null, "close": null}
  }',
  15
),
(
  '20000000-0000-0000-0000-000000000002',
  'Sydney Sleep Research Center',
  '{
    "address": "456 George Street, Sydney NSW 2000",
    "phone": "+61 2 9987 6543",
    "email": "info@sydneysleep.org.au",
    "license_number": "HSC-NSW-2024-002",
    "specializations": ["Sleep Research", "CPAP Therapy", "Sleep Disorders"]
  }',
  '{
    "monday": {"open": "07:00", "close": "19:00"},
    "tuesday": {"open": "07:00", "close": "19:00"},
    "wednesday": {"open": "07:00", "close": "19:00"},
    "thursday": {"open": "07:00", "close": "19:00"},
    "friday": {"open": "07:00", "close": "18:00"},
    "saturday": {"open": "09:00", "close": "14:00"},
    "sunday": {"open": null, "close": null}
  }',
  20
),
(
  '30000000-0000-0000-0000-000000000003',
  'Brisbane Sleep Health Institute',
  '{
    "address": "789 Queen Street, Brisbane QLD 4000",
    "phone": "+61 7 3456 7890",
    "email": "hello@brisbanesleep.health",
    "license_number": "HSC-QLD-2024-003",
    "specializations": ["Pediatric Sleep Medicine", "Adult Sleep Disorders", "Sleep Surgery"]
  }',
  '{
    "monday": {"open": "06:00", "close": "20:00"},
    "tuesday": {"open": "06:00", "close": "20:00"},
    "wednesday": {"open": "06:00", "close": "20:00"},
    "thursday": {"open": "06:00", "close": "20:00"},
    "friday": {"open": "06:00", "close": "18:00"},
    "saturday": {"open": "08:00", "close": "16:00"},
    "sunday": {"open": null, "close": null}
  }',
  25
);

-- =============================================================================
-- AUTH USERS (from auth.users table)
-- =============================================================================

insert into auth.users (
  id, 
  email, 
  email_confirmed_at, 
  raw_user_meta_data,
  aud,
  role,
  created_at,
  updated_at
) values
-- Admin Users
(
  'a0000000-0000-0000-0000-000000000001',
  'admin@melbournesleep.com.au',
  now(),
  '{"first_name": "Sarah", "last_name": "Administrator", "phone": "+61 400 123 456"}',
  'authenticated',
  'authenticated',
  now(),
  now()
),
(
  'a0000000-0000-0000-0000-000000000002',
  'admin@sydneysleep.org.au',
  now(),
  '{"first_name": "Michael", "last_name": "Director", "phone": "+61 400 234 567"}',
  'authenticated',
  'authenticated',
  now(),
  now()
),
-- Doctor Users
(
  'd0000000-0000-0000-0000-000000000001',
  'dr.smith@melbournesleep.com.au',
  now(),
  '{"first_name": "Dr. Emma", "last_name": "Smith", "phone": "+61 400 345 678", "medical_license": "MED-VIC-123456", "specialization": "Sleep Medicine"}',
  'authenticated',
  'authenticated',
  now(),
  now()
),
(
  'd0000000-0000-0000-0000-000000000002',
  'dr.jones@sydneysleep.org.au',
  now(),
  '{"first_name": "Dr. James", "last_name": "Jones", "phone": "+61 400 456 789", "medical_license": "MED-NSW-789012", "specialization": "Sleep Research"}',
  'authenticated',
  'authenticated',
  now(),
  now()
),
(
  'd0000000-0000-0000-0000-000000000003',
  'dr.wong@brisbanesleep.health',
  now(),
  '{"first_name": "Dr. Lisa", "last_name": "Wong", "phone": "+61 400 567 890", "medical_license": "MED-QLD-345678", "specialization": "Pediatric Sleep Medicine"}',
  'authenticated',
  'authenticated',
  now(),
  now()
),
-- Staff Users
(
  '11111111-1111-1111-1111-111111111111',
  'nurse.johnson@melbournesleep.com.au',
  now(),
  '{"first_name": "Jennifer", "last_name": "Johnson", "phone": "+61 400 678 901", "nursing_license": "NUR-VIC-567890"}',
  'authenticated',
  'authenticated',
  now(),
  now()
),
(
  '22222222-2222-2222-2222-222222222222',
  'tech.brown@sydneysleep.org.au',
  now(),
  '{"first_name": "Robert", "last_name": "Brown", "phone": "+61 400 789 012", "certification": "Sleep Technology Certified"}',
  'authenticated',
  'authenticated',
  now(),
  now()
),
(
  '33333333-3333-3333-3333-333333333333',
  'coordinator.davis@brisbanesleep.health',
  now(),
  '{"first_name": "Amanda", "last_name": "Davis", "phone": "+61 400 890 123", "role_title": "Study Coordinator"}',
  'authenticated',
  'authenticated',
  now(),
  now()
),
-- Patient Users  
(
  '44444444-4444-4444-4444-444444444444',
  'patient1@gmail.com',
  now(),
  '{"first_name": "John", "last_name": "Smith", "phone": "+61 400 111 111"}',
  'authenticated',
  'authenticated',
  now(),
  now()
),
(
  '55555555-5555-5555-5555-555555555555',
  'patient2@gmail.com',
  now(),
  '{"first_name": "Mary", "last_name": "Wilson", "phone": "+61 400 222 222"}',
  'authenticated',
  'authenticated',
  now(),
  now()
),
(
  '66666666-6666-6666-6666-666666666666',
  'patient3@gmail.com',
  now(),
  '{"first_name": "David", "last_name": "Brown", "phone": "+61 400 333 333"}',
  'authenticated',
  'authenticated',
  now(),
  now()
),
(
  '77777777-7777-7777-7777-777777777777',
  'patient4@gmail.com',
  now(),
  '{"first_name": "Sarah", "last_name": "Davis", "phone": "+61 400 444 444"}',
  'authenticated',
  'authenticated',
  now(),
  now()
),
(
  '88888888-8888-8888-8888-888888888888',
  'patient5@gmail.com',
  now(),
  '{"first_name": "Michael", "last_name": "Johnson", "phone": "+61 400 555 555"}',
  'authenticated',
  'authenticated',
  now(),
  now()
);

-- =============================================================================
-- APP USERS (links to auth.users)
-- =============================================================================

insert into public.app_users (id, role) values
-- Admin Users
('a0000000-0000-0000-0000-000000000001', 'admin'),
('a0000000-0000-0000-0000-000000000002', 'admin'),
-- Doctor Users
('d0000000-0000-0000-0000-000000000001', 'doctor'),
('d0000000-0000-0000-0000-000000000002', 'doctor'),
('d0000000-0000-0000-0000-000000000003', 'doctor'),
-- Staff Users
('11111111-1111-1111-1111-111111111111', 'staff'),
('22222222-2222-2222-2222-222222222222', 'staff'),
('33333333-3333-3333-3333-333333333333', 'staff'),
-- Patient Users
('44444444-4444-4444-4444-444444444444', 'patient'),
('55555555-5555-5555-5555-555555555555', 'patient'),
('66666666-6666-6666-6666-666666666666', 'patient'),
('77777777-7777-7777-7777-777777777777', 'patient'),
('88888888-8888-8888-8888-888888888888', 'patient');

-- =============================================================================
-- PATIENT PROFILES
-- =============================================================================

insert into public.patient_profiles (user_id, patient_details) values
(
  '44444444-4444-4444-4444-444444444444',
  '{
    "date_of_birth": "1975-06-15",
    "gender": "male",
    "height_cm": 180,
    "weight_kg": 85,
    "medical_history": {
      "existing_conditions": ["Hypertension", "Sleep Apnea"],
      "medications": ["Blood pressure medication"],
      "allergies": ["None known"]
    },
    "insurance_details": {
      "provider": "Medicare",
      "policy_number": "123456789",
      "expiry_date": "2025-12-31"
    },
    "emergency_contact": {
      "name": "Jane Smith",
      "relationship": "spouse",
      "phone": "+61 400 111 222"
    }
  }'
),
(
  '55555555-5555-5555-5555-555555555555',
  '{
    "date_of_birth": "1982-03-22",
    "gender": "female", 
    "height_cm": 165,
    "weight_kg": 70,
    "medical_history": {
      "existing_conditions": ["Insomnia", "Anxiety"],
      "medications": ["Sleep aids"],
      "allergies": ["Latex"]
    },
    "insurance_details": {
      "provider": "Bupa",
      "policy_number": "987654321",
      "expiry_date": "2026-06-30"
    },
    "emergency_contact": {
      "name": "Robert Wilson",
      "relationship": "spouse",
      "phone": "+61 400 222 333"
    }
  }'
),
(
  '66666666-6666-6666-6666-666666666666',
  '{
    "date_of_birth": "1968-11-08",
    "gender": "male",
    "height_cm": 175,
    "weight_kg": 90,
    "medical_history": {
      "existing_conditions": ["Diabetes", "Heart Disease"],
      "medications": ["Diabetes medication", "Heart medication"],
      "allergies": ["Shellfish"]
    },
    "insurance_details": {
      "provider": "Medibank",
      "policy_number": "456789123",
      "expiry_date": "2025-09-15"
    },
    "emergency_contact": {
      "name": "Lisa Brown",
      "relationship": "daughter",
      "phone": "+61 400 333 444"
    }
  }'
),
(
  '77777777-7777-7777-7777-777777777777',
  '{
    "date_of_birth": "1990-01-30",
    "gender": "female",
    "height_cm": 170,
    "weight_kg": 65,
    "medical_history": {
      "existing_conditions": ["Narcolepsy"],
      "medications": ["Stimulants"],
      "allergies": ["None known"]
    },
    "insurance_details": {
      "provider": "HCF",
      "policy_number": "789123456",
      "expiry_date": "2026-03-31"
    },
    "emergency_contact": {
      "name": "Tom Davis",
      "relationship": "parent",
      "phone": "+61 400 444 555"
    }
  }'
),
(
  '88888888-8888-8888-8888-888888888888',
  '{
    "date_of_birth": "1985-09-12",
    "gender": "male",
    "height_cm": 185,
    "weight_kg": 95,
    "medical_history": {
      "existing_conditions": ["Sleep Apnea", "Obesity"],
      "medications": ["CPAP therapy"],
      "allergies": ["Nuts"]
    },
    "insurance_details": {
      "provider": "NIB",
      "policy_number": "321654987",
      "expiry_date": "2025-11-20"
    },
    "emergency_contact": {
      "name": "Emma Johnson",
      "relationship": "sister",
      "phone": "+61 400 555 666"
    }
  }'
);

-- =============================================================================
-- STAFF MEMBERSHIPS (link staff to organizations)
-- =============================================================================

insert into public.staff_memberships (user_id, organization_id, role_details) values
-- Melbourne Sleep Clinic Staff
(
  'a0000000-0000-0000-0000-000000000001',
  '10000000-0000-0000-0000-000000000001',
  '{
    "role": "admin",
    "permissions": ["manage_users", "manage_studies", "manage_devices", "view_reports", "manage_organization"],
    "department": "Administration",
    "hire_date": "2020-01-15"
  }'
),
(
  'd0000000-0000-0000-0000-000000000001',
  '10000000-0000-0000-0000-000000000001',
  '{
    "role": "doctor",
    "permissions": ["view_studies", "create_reports", "view_patient_data"],
    "department": "Sleep Medicine",
    "hire_date": "2021-03-01"
  }'
),
(
  '11111111-1111-1111-1111-111111111111',
  '10000000-0000-0000-0000-000000000001',
  '{
    "role": "nurse",
    "permissions": ["manage_studies", "view_patient_data"],
    "department": "Patient Care",
    "hire_date": "2021-06-15"
  }'
),
-- Sydney Sleep Research Center Staff
(
  'a0000000-0000-0000-0000-000000000002',
  '20000000-0000-0000-0000-000000000002',
  '{
    "role": "admin",
    "permissions": ["manage_users", "manage_studies", "manage_devices", "view_reports", "manage_organization"],
    "department": "Administration",
    "hire_date": "2019-09-01"
  }'
),
(
  'd0000000-0000-0000-0000-000000000002',
  '20000000-0000-0000-0000-000000000002',
  '{
    "role": "doctor",
    "permissions": ["view_studies", "create_reports", "view_patient_data"],
    "department": "Research",
    "hire_date": "2020-02-15"
  }'
),
(
  '22222222-2222-2222-2222-222222222222',
  '20000000-0000-0000-0000-000000000002',
  '{
    "role": "technician",
    "permissions": ["manage_studies", "manage_devices"],
    "department": "Technical Services",
    "hire_date": "2022-01-10"
  }'
),
-- Brisbane Sleep Health Institute Staff
(
  'd0000000-0000-0000-0000-000000000003',
  '30000000-0000-0000-0000-000000000003',
  '{
    "role": "doctor",
    "permissions": ["view_studies", "create_reports", "view_patient_data"],
    "department": "Pediatric Sleep Medicine",
    "hire_date": "2021-08-20"
  }'
),
(
  '33333333-3333-3333-3333-333333333333',
  '30000000-0000-0000-0000-000000000003',
  '{
    "role": "coordinator",
    "permissions": ["manage_studies", "schedule_appointments"],
    "department": "Patient Coordination",
    "hire_date": "2022-05-01"
  }'
);

-- =============================================================================
-- DEVICES
-- =============================================================================

insert into public.devices (id, organization_id, device_details, status) values
-- Melbourne Sleep Clinic Devices
(
  '10000000-1111-1111-1111-111111111111',
  '10000000-0000-0000-0000-000000000001',
  '{
    "model": "ResMed AirSense 10",
    "serial_number": "RSM-2024-001",
    "type": "CPAP Machine",
    "manufacturer": "ResMed",
    "purchase_date": "2024-01-15",
    "warranty_expiry": "2027-01-15"
  }',
  'available'
),
(
  '10000000-1111-1111-1111-222222222222',
  '10000000-0000-0000-0000-000000000001',
  '{
    "model": "Philips DreamStation 2",
    "serial_number": "PHL-2024-002",
    "type": "Auto CPAP",
    "manufacturer": "Philips",
    "purchase_date": "2024-03-20",
    "warranty_expiry": "2027-03-20"
  }',
  'available'
),
-- Sydney Sleep Research Center Devices
(
  '20000000-2222-2222-2222-111111111111',
  '20000000-0000-0000-0000-000000000002',
  '{
    "model": "Embla Titanium",
    "serial_number": "EMB-2024-003",
    "type": "PSG System",
    "manufacturer": "Natus Medical",
    "purchase_date": "2024-02-10",
    "warranty_expiry": "2027-02-10"
  }',
  'available'
),
(
  '20000000-2222-2222-2222-222222222222',
  '20000000-0000-0000-0000-000000000002',
  '{
    "model": "WatchPAT ONE",
    "serial_number": "WP1-2024-004",
    "type": "Home Sleep Test",
    "manufacturer": "Itamar Medical",
    "purchase_date": "2024-04-05",
    "warranty_expiry": "2026-04-05"
  }',
  'assigned'
),
-- Brisbane Sleep Health Institute Devices
(
  '30000000-3333-3333-3333-111111111111',
  '30000000-0000-0000-0000-000000000003',
  '{
    "model": "Somnomedics DOMINO",
    "serial_number": "SMD-2024-005",
    "type": "Portable PSG",
    "manufacturer": "Somnomedics",
    "purchase_date": "2024-01-30",
    "warranty_expiry": "2027-01-30"
  }',
  'available'
);

-- =============================================================================
-- SLEEP STUDIES
-- =============================================================================

insert into public.sleep_studies (
  id, 
  patient_id, 
  manager_id, 
  doctor_id, 
  device_id, 
  current_state, 
  start_date, 
  end_date
) values
(
  '10000000-1111-2222-3333-444444444444',
  '44444444-4444-4444-4444-444444444444',
  '11111111-1111-1111-1111-111111111111',
  'd0000000-0000-0000-0000-000000000001',
  '10000000-1111-1111-1111-111111111111',
  'active',
  '2024-12-01',
  '2024-12-08'
),
(
  '20000000-2222-3333-4444-555555555555',
  '55555555-5555-5555-5555-555555555555',
  '22222222-2222-2222-2222-222222222222',
  'd0000000-0000-0000-0000-000000000002',
  '20000000-2222-2222-2222-222222222222',
  'review',
  '2024-11-15',
  '2024-11-22'
),
(
  '30000000-3333-4444-5555-666666666666',
  '66666666-6666-6666-6666-666666666666',
  '33333333-3333-3333-3333-333333333333',
  'd0000000-0000-0000-0000-000000000003',
  null,
  'booked',
  '2024-12-15',
  null
),
(
  '10000000-4444-5555-6666-777777777777',
  '77777777-7777-7777-7777-777777777777',
  '11111111-1111-1111-1111-111111111111',
  'd0000000-0000-0000-0000-000000000001',
  '10000000-1111-1111-1111-222222222222',
  'completed',
  '2024-10-01',
  '2024-10-08'
),
(
  '20000000-5555-6666-7777-888888888888',
  '88888888-8888-8888-8888-888888888888',
  '22222222-2222-2222-2222-222222222222',
  'd0000000-0000-0000-0000-000000000002',
  null,
  'cancelled',
  '2024-11-01',
  null
);

-- =============================================================================
-- SAMPLE SURVEY RESPONSES
-- =============================================================================

insert into public.survey_responses (sleep_study_id, type, answers, score) values
(
  '10000000-1111-2222-3333-444444444444',
  'Epworth Sleepiness Scale',
  '{
    "q1_sitting_reading": 2,
    "q2_watching_tv": 1,
    "q3_sitting_inactive_public": 0,
    "q4_passenger_car": 3,
    "q5_lying_down_afternoon": 2,
    "q6_sitting_talking": 0,
    "q7_sitting_quietly_lunch": 1,
    "q8_car_stopped_traffic": 2
  }',
  11
),
(
  '20000000-2222-3333-4444-555555555555',
  'Pittsburgh Sleep Quality Index',
  '{
    "sleep_quality": 2,
    "sleep_latency": 1,
    "sleep_duration": 1,
    "sleep_efficiency": 0,
    "sleep_disturbances": 1,
    "use_sleep_medication": 0,
    "daytime_dysfunction": 2
  }',
  7
);

-- =============================================================================
-- SUMMARY
-- =============================================================================

-- Display summary of seeded data
do $$
declare
  org_count integer;
  user_count integer;
  patient_count integer;
  staff_count integer;
  device_count integer;
  study_count integer;
begin
  select count(*) into org_count from public.organizations;
  select count(*) into user_count from public.app_users;
  select count(*) into patient_count from public.app_users where role = 'patient';
  select count(*) into staff_count from public.staff_memberships;
  select count(*) into device_count from public.devices;
  select count(*) into study_count from public.sleep_studies;
  
  raise notice '=============================================================================';
  raise notice 'SEED DATA SUMMARY';
  raise notice '=============================================================================';
  raise notice 'Organizations: %', org_count;
  raise notice 'Total Users: %', user_count;
  raise notice 'Patient Profiles: %', patient_count;
  raise notice 'Staff Memberships: %', staff_count;
  raise notice 'Devices: %', device_count;
  raise notice 'Sleep Studies: %', study_count;
  raise notice '=============================================================================';
  raise notice 'Test Login Credentials:';
  raise notice 'Admin: admin@melbournesleep.com.au';
  raise notice 'Doctor: dr.smith@melbournesleep.com.au';
  raise notice 'Staff: nurse.johnson@melbournesleep.com.au';
  raise notice 'Patient: patient1@gmail.com';
  raise notice '=============================================================================';
end $$; 