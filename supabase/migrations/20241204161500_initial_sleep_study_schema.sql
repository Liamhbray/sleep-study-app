/*
  Migration: Sleep Study Management System Schema
  Description: Creates the complete database schema for a sleep study management application
  Author: Sleep Study App
  Created: 2024-12-04 16:15:00 UTC
  
  Tables created:
  - organizations: Healthcare organizations managing sleep studies
  - app_users: Application users with role-based access
  - staff_memberships: Links staff to organizations with roles
  - patient_profiles: Extended patient information and medical details
  - devices: Sleep monitoring devices owned by organizations
  - sleep_studies: Individual sleep study cases and their lifecycle
  - referrals: Medical referral documents for sleep studies
  - survey_responses: Patient survey data and scoring
  - sleep_data_files: Raw sleep monitoring data files
  - doctor_reports: Final medical reports from doctors
  
  Security: All tables have RLS enabled with role-based access policies
  Storage: Integration with Supabase Storage buckets for file management
*/

-- =============================================
-- CUSTOM ENUMS
-- =============================================

-- Device status enum
create type public.device_status as enum ('available', 'assigned');

-- Sleep study state enum  
create type public.study_state as enum ('booked', 'active', 'review', 'completed', 'cancelled');

-- =============================================
-- ORGANIZATIONS TABLE
-- =============================================

create table public.organizations (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  organization_details jsonb,
  opening_hours jsonb,
  max_concurrent_studies integer default 10,
  created_at timestamptz default now() not null,
  updated_at timestamptz default now() not null
);

comment on table public.organizations is 'Healthcare organizations that manage sleep studies, devices, and staff';

-- Enable RLS
alter table public.organizations enable row level security;

-- RLS Policies for organizations
create policy "Organizations are viewable by staff members"
  on public.organizations
  for select
  to authenticated
  using (
    id in (
      select organization_id 
      from public.staff_memberships 
      where user_id = (select auth.uid())
    )
  );

create policy "Organizations can be updated by admin staff"
  on public.organizations
  for update
  to authenticated
  using (
    id in (
      select organization_id 
      from public.staff_memberships 
      where user_id = (select auth.uid()) 
      and (role_details->>'role')::text = 'admin'
    )
  )
  with check (
    id in (
      select organization_id 
      from public.staff_memberships 
      where user_id = (select auth.uid()) 
      and (role_details->>'role')::text = 'admin'
    )
  );

create policy "Organizations can be inserted by authenticated users"
  on public.organizations
  for insert
  to authenticated
  with check (true);

-- =============================================
-- APP USERS TABLE  
-- =============================================

create table public.app_users (
  id uuid default gen_random_uuid() primary key,
  role text not null check (role in ('patient', 'staff', 'doctor', 'admin')),
  created_at timestamptz default now() not null,
  
  -- Link to auth.users
  constraint app_users_id_fkey foreign key (id) references auth.users(id) on delete cascade
);

comment on table public.app_users is 'Application users with role-based access - extends auth.users';

-- Enable RLS
alter table public.app_users enable row level security;

-- RLS Policies for app_users
create policy "Users can view their own app user record"
  on public.app_users
  for select
  to authenticated
  using ((select auth.uid()) = id);

create policy "Users can insert their own app user record"
  on public.app_users
  for insert
  to authenticated
  with check ((select auth.uid()) = id);

create policy "Staff can view app users in their organization"
  on public.app_users
  for select
  to authenticated
  using (
    (select auth.uid()) in (
      select user_id 
      from public.staff_memberships sm
      where sm.organization_id in (
        select organization_id 
        from public.staff_memberships 
        where user_id = id
      )
    )
  );

-- =============================================
-- STAFF MEMBERSHIPS TABLE
-- =============================================

create table public.staff_memberships (
  id uuid default gen_random_uuid() primary key,
  user_id uuid not null references public.app_users(id) on delete cascade,
  organization_id uuid not null references public.organizations(id) on delete cascade,
  role_details jsonb not null,
  created_at timestamptz default now() not null,
  
  -- Ensure unique user per organization
  unique(user_id, organization_id)
);

comment on table public.staff_memberships is 'Links staff members to organizations with role details and permissions';

-- Enable RLS
alter table public.staff_memberships enable row level security;

-- RLS Policies for staff_memberships
create policy "Staff can view their own memberships"
  on public.staff_memberships
  for select
  to authenticated
  using ((select auth.uid()) = user_id);

create policy "Staff can view memberships in their organization"
  on public.staff_memberships
  for select
  to authenticated
  using (
    organization_id in (
      select organization_id 
      from public.staff_memberships 
      where user_id = (select auth.uid())
    )
  );

create policy "Admin staff can manage memberships in their organization"
  on public.staff_memberships
  for all
  to authenticated
  using (
    organization_id in (
      select organization_id 
      from public.staff_memberships 
      where user_id = (select auth.uid()) 
      and (role_details->>'role')::text = 'admin'
    )
  );

-- =============================================
-- PATIENT PROFILES TABLE
-- =============================================

create table public.patient_profiles (
  user_id uuid primary key references public.app_users(id) on delete cascade,
  patient_details jsonb not null,
  created_at timestamptz default now() not null,
  updated_at timestamptz default now() not null
);

comment on table public.patient_profiles is 'Extended patient information including medical history and demographics';

-- Enable RLS
alter table public.patient_profiles enable row level security;

-- RLS Policies for patient_profiles
create policy "Patients can view their own profile"
  on public.patient_profiles
  for select
  to authenticated
  using ((select auth.uid()) = user_id);

create policy "Patients can update their own profile"
  on public.patient_profiles
  for update
  to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy "Patients can insert their own profile"
  on public.patient_profiles
  for insert
  to authenticated
  with check ((select auth.uid()) = user_id);

create policy "Staff can view patient profiles for their studies"
  on public.patient_profiles
  for select
  to authenticated
  using (
    user_id in (
      select patient_id 
      from public.sleep_studies ss
      join public.staff_memberships sm on sm.user_id = (select auth.uid())
      where ss.manager_id = sm.user_id or ss.doctor_id = sm.user_id
    )
  );

-- =============================================
-- DEVICES TABLE
-- =============================================

create table public.devices (
  id uuid default gen_random_uuid() primary key,
  organization_id uuid not null references public.organizations(id) on delete cascade,
  device_details jsonb not null,
  status public.device_status default 'available' not null,
  created_at timestamptz default now() not null,
  updated_at timestamptz default now() not null
);

comment on table public.devices is 'Sleep monitoring devices owned and managed by healthcare organizations';

-- Enable RLS
alter table public.devices enable row level security;

-- RLS Policies for devices
create policy "Staff can view devices in their organization"
  on public.devices
  for select
  to authenticated
  using (
    organization_id in (
      select organization_id 
      from public.staff_memberships 
      where user_id = (select auth.uid())
    )
  );

create policy "Staff can manage devices in their organization"
  on public.devices
  for all
  to authenticated
  using (
    organization_id in (
      select organization_id 
      from public.staff_memberships 
      where user_id = (select auth.uid())
    )
  );

-- =============================================
-- SLEEP STUDIES TABLE
-- =============================================

create table public.sleep_studies (
  id uuid default gen_random_uuid() primary key,
  patient_id uuid not null references public.app_users(id),
  manager_id uuid not null references public.app_users(id),
  doctor_id uuid not null references public.app_users(id),
  device_id uuid references public.devices(id),
  current_state public.study_state default 'booked' not null,
  start_date date not null,
  end_date date,
  created_at timestamptz default now() not null,
  updated_at timestamptz default now() not null
);

comment on table public.sleep_studies is 'Individual sleep study cases tracking patient care from booking to completion';

-- Enable RLS
alter table public.sleep_studies enable row level security;

-- RLS Policies for sleep_studies
create policy "Patients can view their own sleep studies"
  on public.sleep_studies
  for select
  to authenticated
  using ((select auth.uid()) = patient_id);

create policy "Staff can view sleep studies they manage or oversee"
  on public.sleep_studies
  for select
  to authenticated
  using (
    (select auth.uid()) = manager_id or 
    (select auth.uid()) = doctor_id
  );

create policy "Managers can update their assigned sleep studies"
  on public.sleep_studies
  for update
  to authenticated
  using ((select auth.uid()) = manager_id)
  with check ((select auth.uid()) = manager_id);

create policy "Staff can create sleep studies in their organization"
  on public.sleep_studies
  for insert
  to authenticated
  with check (
    manager_id in (
      select user_id 
      from public.staff_memberships 
      where organization_id in (
        select organization_id 
        from public.staff_memberships 
        where user_id = (select auth.uid())
      )
    )
  );

-- =============================================
-- REFERRALS TABLE
-- =============================================

create table public.referrals (
  id uuid default gen_random_uuid() primary key,
  sleep_study_id uuid not null references public.sleep_studies(id) on delete cascade,
  file_url text not null,
  created_at timestamptz default now() not null
);

comment on table public.referrals is 'Medical referral documents uploaded for each sleep study';

-- Enable RLS
alter table public.referrals enable row level security;

-- RLS Policies for referrals
create policy "Patients can view referrals for their sleep studies"
  on public.referrals
  for select
  to authenticated
  using (
    sleep_study_id in (
      select id 
      from public.sleep_studies 
      where patient_id = (select auth.uid())
    )
  );

create policy "Staff can view referrals for studies they manage"
  on public.referrals
  for select
  to authenticated
  using (
    sleep_study_id in (
      select id 
      from public.sleep_studies 
      where manager_id = (select auth.uid()) or doctor_id = (select auth.uid())
    )
  );

create policy "Staff can manage referrals for studies they manage"
  on public.referrals
  for all
  to authenticated
  using (
    sleep_study_id in (
      select id 
      from public.sleep_studies 
      where manager_id = (select auth.uid())
    )
  );

-- =============================================
-- SURVEY RESPONSES TABLE
-- =============================================

create table public.survey_responses (
  id uuid default gen_random_uuid() primary key,
  sleep_study_id uuid not null references public.sleep_studies(id) on delete cascade,
  type text not null,
  answers jsonb not null,
  score integer,
  created_at timestamptz default now() not null
);

comment on table public.survey_responses is 'Patient survey responses and calculated scores for sleep studies';

-- Enable RLS
alter table public.survey_responses enable row level security;

-- RLS Policies for survey_responses
create policy "Patients can view their own survey responses"
  on public.survey_responses
  for select
  to authenticated
  using (
    sleep_study_id in (
      select id 
      from public.sleep_studies 
      where patient_id = (select auth.uid())
    )
  );

create policy "Patients can create survey responses for their studies"
  on public.survey_responses
  for insert
  to authenticated
  with check (
    sleep_study_id in (
      select id 
      from public.sleep_studies 
      where patient_id = (select auth.uid())
    )
  );

create policy "Staff can view survey responses for studies they manage"
  on public.survey_responses
  for select
  to authenticated
  using (
    sleep_study_id in (
      select id 
      from public.sleep_studies 
      where manager_id = (select auth.uid()) or doctor_id = (select auth.uid())
    )
  );

-- =============================================
-- SLEEP DATA FILES TABLE
-- =============================================

create table public.sleep_data_files (
  id uuid default gen_random_uuid() primary key,
  sleep_study_id uuid not null references public.sleep_studies(id) on delete cascade,
  file_url text not null,
  created_at timestamptz default now() not null
);

comment on table public.sleep_data_files is 'Raw sleep monitoring data files collected during studies';

-- Enable RLS
alter table public.sleep_data_files enable row level security;

-- RLS Policies for sleep_data_files  
create policy "Staff can view sleep data files for studies they manage"
  on public.sleep_data_files
  for select
  to authenticated
  using (
    sleep_study_id in (
      select id 
      from public.sleep_studies 
      where manager_id = (select auth.uid()) or doctor_id = (select auth.uid())
    )
  );

create policy "Staff can manage sleep data files for studies they manage"
  on public.sleep_data_files
  for all
  to authenticated
  using (
    sleep_study_id in (
      select id 
      from public.sleep_studies 
      where manager_id = (select auth.uid())
    )
  );

-- =============================================
-- DOCTOR REPORTS TABLE
-- =============================================

create table public.doctor_reports (
  id uuid default gen_random_uuid() primary key,
  sleep_study_id uuid not null references public.sleep_studies(id) on delete cascade,
  file_url text not null,
  created_at timestamptz default now() not null
);

comment on table public.doctor_reports is 'Final medical reports generated by doctors for completed sleep studies';

-- Enable RLS
alter table public.doctor_reports enable row level security;

-- RLS Policies for doctor_reports
create policy "Patients can view reports for their sleep studies"
  on public.doctor_reports
  for select
  to authenticated
  using (
    sleep_study_id in (
      select id 
      from public.sleep_studies 
      where patient_id = (select auth.uid())
    )
  );

create policy "Staff can view reports for studies they manage"
  on public.doctor_reports
  for select
  to authenticated
  using (
    sleep_study_id in (
      select id 
      from public.sleep_studies 
      where manager_id = (select auth.uid()) or doctor_id = (select auth.uid())
    )
  );

create policy "Doctors can manage reports for studies they oversee"
  on public.doctor_reports
  for all
  to authenticated
  using (
    sleep_study_id in (
      select id 
      from public.sleep_studies 
      where doctor_id = (select auth.uid())
    )
  );

-- =============================================
-- PERFORMANCE INDEXES
-- =============================================

-- Foreign key indexes
create index staff_memberships_user_id_idx on public.staff_memberships using btree (user_id);
create index staff_memberships_organization_id_idx on public.staff_memberships using btree (organization_id);
create index devices_organization_id_idx on public.devices using btree (organization_id);
create index sleep_studies_patient_id_idx on public.sleep_studies using btree (patient_id);
create index sleep_studies_manager_id_idx on public.sleep_studies using btree (manager_id);
create index sleep_studies_doctor_id_idx on public.sleep_studies using btree (doctor_id);
create index sleep_studies_device_id_idx on public.sleep_studies using btree (device_id);
create index referrals_sleep_study_id_idx on public.referrals using btree (sleep_study_id);
create index survey_responses_sleep_study_id_idx on public.survey_responses using btree (sleep_study_id);
create index sleep_data_files_sleep_study_id_idx on public.sleep_data_files using btree (sleep_study_id);
create index doctor_reports_sleep_study_id_idx on public.doctor_reports using btree (sleep_study_id);

-- Status and state indexes for filtering
create index devices_status_idx on public.devices using btree (status);
create index sleep_studies_current_state_idx on public.sleep_studies using btree (current_state);

-- Date indexes for time-based queries
create index sleep_studies_start_date_idx on public.sleep_studies using btree (start_date);
create index sleep_studies_created_at_idx on public.sleep_studies using btree (created_at);

-- =============================================
-- UPDATED_AT TRIGGER FUNCTION
-- =============================================

-- Function to automatically update updated_at timestamp
create or replace function public.update_updated_at()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
  -- Update the "updated_at" column on row modification
  new.updated_at := now();
  return new;
end;
$$;

-- Apply triggers to tables with updated_at columns
create trigger update_organizations_updated_at
  before update on public.organizations
  for each row
  execute function public.update_updated_at();

create trigger update_patient_profiles_updated_at
  before update on public.patient_profiles
  for each row
  execute function public.update_updated_at();

create trigger update_devices_updated_at
  before update on public.devices
  for each row
  execute function public.update_updated_at();

create trigger update_sleep_studies_updated_at
  before update on public.sleep_studies
  for each row
  execute function public.update_updated_at(); 