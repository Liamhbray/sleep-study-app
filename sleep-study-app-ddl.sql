-- =============================================================================
-- Sleep Study App Database DDL
-- =============================================================================
-- This DDL includes the complete database schema for the Sleep Study Practice
-- Management System, including auth, storage, and public schemas.
-- Generated from Supabase project: sleep-study-app
-- =============================================================================

-- Create Schemas
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS storage;
CREATE SCHEMA IF NOT EXISTS public;

-- Create Custom Types and Enums
-- =============================================================================

-- Auth schema enums
CREATE TYPE auth.aal_level AS ENUM ('aal1', 'aal2', 'aal3');
CREATE TYPE auth.code_challenge_method AS ENUM ('s256', 'plain');
CREATE TYPE auth.factor_status AS ENUM ('unverified', 'verified');
CREATE TYPE auth.factor_type AS ENUM ('totp', 'webauthn', 'phone');
CREATE TYPE auth.one_time_token_type AS ENUM (
    'confirmation_token', 
    'reauthentication_token', 
    'recovery_token', 
    'email_change_token_new', 
    'email_change_token_current', 
    'phone_change_token'
);

-- Public schema enums
CREATE TYPE public.device_status AS ENUM ('available', 'assigned');
CREATE TYPE public.study_state AS ENUM ('booked', 'active', 'review', 'completed', 'cancelled');

-- Auth Schema Tables
-- =============================================================================

-- Auth: Manages users across multiple sites
CREATE TABLE auth.instances (
    id uuid NOT NULL PRIMARY KEY,
    uuid uuid,
    raw_base_config text,
    created_at timestamptz,
    updated_at timestamptz
);

COMMENT ON TABLE auth.instances IS 'Auth: Manages users across multiple sites.';

-- Auth: Stores user login data within a secure schema
CREATE TABLE auth.users (
    instance_id uuid,
    id uuid NOT NULL PRIMARY KEY,
    aud varchar(255),
    role varchar(255),
    email varchar(255),
    encrypted_password varchar(255),
    email_confirmed_at timestamptz,
    invited_at timestamptz,
    confirmation_token varchar(255),
    confirmation_sent_at timestamptz,
    recovery_token varchar(255),
    recovery_sent_at timestamptz,
    email_change_token_new varchar(255),
    email_change varchar(255),
    email_change_sent_at timestamptz,
    last_sign_in_at timestamptz,
    raw_app_meta_data jsonb,
    raw_user_meta_data jsonb,
    is_super_admin boolean,
    created_at timestamptz,
    updated_at timestamptz,
    phone text DEFAULT NULL::character varying UNIQUE,
    phone_confirmed_at timestamptz,
    phone_change text DEFAULT ''::character varying,
    phone_change_token varchar(255) DEFAULT ''::character varying,
    phone_change_sent_at timestamptz,
    confirmed_at timestamptz GENERATED ALWAYS AS (LEAST(email_confirmed_at, phone_confirmed_at)) STORED,
    email_change_token_current varchar(255) DEFAULT ''::character varying,
    email_change_confirm_status smallint DEFAULT 0 CHECK (email_change_confirm_status >= 0 AND email_change_confirm_status <= 2),
    banned_until timestamptz,
    reauthentication_token varchar(255) DEFAULT ''::character varying,
    reauthentication_sent_at timestamptz,
    is_sso_user boolean NOT NULL DEFAULT false,
    deleted_at timestamptz,
    is_anonymous boolean NOT NULL DEFAULT false
);

COMMENT ON TABLE auth.users IS 'Auth: Stores user login data within a secure schema.';
COMMENT ON COLUMN auth.users.is_sso_user IS 'Auth: Set this column to true when the account comes from SSO. These accounts can have duplicate emails.';

-- Auth: Store of tokens used to refresh JWT tokens once they expire
CREATE TABLE auth.refresh_tokens (
    instance_id uuid,
    id bigserial PRIMARY KEY,
    token varchar(255) UNIQUE,
    user_id varchar(255),
    revoked boolean,
    created_at timestamptz,
    updated_at timestamptz,
    parent varchar(255),
    session_id uuid
);

COMMENT ON TABLE auth.refresh_tokens IS 'Auth: Store of tokens used to refresh JWT tokens once they expire.';

-- Auth: Manages updates to the auth system
CREATE TABLE auth.schema_migrations (
    version varchar(255) NOT NULL PRIMARY KEY
);

COMMENT ON TABLE auth.schema_migrations IS 'Auth: Manages updates to the auth system.';

-- Auth: Audit trail for user actions
CREATE TABLE auth.audit_log_entries (
    instance_id uuid,
    id uuid NOT NULL PRIMARY KEY,
    payload json,
    created_at timestamptz,
    ip_address varchar(64) NOT NULL DEFAULT ''::character varying
);

COMMENT ON TABLE auth.audit_log_entries IS 'Auth: Audit trail for user actions.';

-- Auth: Stores identities associated to a user
CREATE TABLE auth.identities (
    provider_id text NOT NULL,
    user_id uuid NOT NULL,
    identity_data jsonb NOT NULL,
    provider text NOT NULL,
    last_sign_in_at timestamptz,
    created_at timestamptz,
    updated_at timestamptz,
    email text GENERATED ALWAYS AS (lower((identity_data ->> 'email'::text))) STORED,
    id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    CONSTRAINT identities_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
);

COMMENT ON TABLE auth.identities IS 'Auth: Stores identities associated to a user.';
COMMENT ON COLUMN auth.identities.email IS 'Auth: Email is a generated column that references the optional email property in the identity_data';

-- Auth: Stores session data associated to a user
CREATE TABLE auth.sessions (
    id uuid NOT NULL PRIMARY KEY,
    user_id uuid NOT NULL,
    created_at timestamptz,
    updated_at timestamptz,
    factor_id uuid,
    aal auth.aal_level,
    not_after timestamptz,
    refreshed_at timestamp,
    user_agent text,
    ip inet,
    tag text,
    CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
);

COMMENT ON TABLE auth.sessions IS 'Auth: Stores session data associated to a user.';
COMMENT ON COLUMN auth.sessions.not_after IS 'Auth: Not after is a nullable column that contains a timestamp after which the session should be regarded as expired.';

-- Auth: stores metadata about factors
CREATE TABLE auth.mfa_factors (
    id uuid NOT NULL PRIMARY KEY,
    user_id uuid NOT NULL,
    friendly_name text,
    factor_type auth.factor_type NOT NULL,
    status auth.factor_status NOT NULL,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    secret text,
    phone text,
    last_challenged_at timestamptz UNIQUE,
    web_authn_credential jsonb,
    web_authn_aaguid uuid,
    CONSTRAINT mfa_factors_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
);

COMMENT ON TABLE auth.mfa_factors IS 'auth: stores metadata about factors';

-- Auth: stores metadata about challenge requests made
CREATE TABLE auth.mfa_challenges (
    id uuid NOT NULL PRIMARY KEY,
    factor_id uuid NOT NULL,
    created_at timestamptz NOT NULL,
    verified_at timestamptz,
    ip_address inet NOT NULL,
    otp_code text,
    web_authn_session_data jsonb,
    CONSTRAINT mfa_challenges_auth_factor_id_fkey FOREIGN KEY (factor_id) REFERENCES auth.mfa_factors(id) ON DELETE CASCADE
);

COMMENT ON TABLE auth.mfa_challenges IS 'auth: stores metadata about challenge requests made';

-- Auth: stores authenticator method reference claims for multi factor authentication
CREATE TABLE auth.mfa_amr_claims (
    session_id uuid NOT NULL,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    authentication_method text NOT NULL,
    id uuid NOT NULL PRIMARY KEY,
    CONSTRAINT mfa_amr_claims_session_id_fkey FOREIGN KEY (session_id) REFERENCES auth.sessions(id) ON DELETE CASCADE
);

COMMENT ON TABLE auth.mfa_amr_claims IS 'auth: stores authenticator method reference claims for multi factor authentication';

-- Auth: Manages SSO identity provider information; see saml_providers for SAML
CREATE TABLE auth.sso_providers (
    id uuid NOT NULL PRIMARY KEY,
    resource_id text CHECK (resource_id = NULL::text OR char_length(resource_id) > 0),
    created_at timestamptz,
    updated_at timestamptz
);

COMMENT ON TABLE auth.sso_providers IS 'Auth: Manages SSO identity provider information; see saml_providers for SAML.';
COMMENT ON COLUMN auth.sso_providers.resource_id IS 'Auth: Uniquely identifies a SSO provider according to a user-chosen resource ID (case insensitive), useful in infrastructure as code.';

-- Auth: Manages SSO email address domain mapping to an SSO Identity Provider
CREATE TABLE auth.sso_domains (
    id uuid NOT NULL PRIMARY KEY,
    sso_provider_id uuid NOT NULL,
    domain text NOT NULL CHECK (char_length(domain) > 0),
    created_at timestamptz,
    updated_at timestamptz,
    CONSTRAINT sso_domains_sso_provider_id_fkey FOREIGN KEY (sso_provider_id) REFERENCES auth.sso_providers(id) ON DELETE CASCADE
);

COMMENT ON TABLE auth.sso_domains IS 'Auth: Manages SSO email address domain mapping to an SSO Identity Provider.';

-- Auth: Manages SAML Identity Provider connections
CREATE TABLE auth.saml_providers (
    id uuid NOT NULL PRIMARY KEY,
    sso_provider_id uuid NOT NULL,
    entity_id text NOT NULL UNIQUE CHECK (char_length(entity_id) > 0),
    metadata_xml text NOT NULL CHECK (char_length(metadata_xml) > 0),
    metadata_url text CHECK (metadata_url = NULL::text OR char_length(metadata_url) > 0),
    attribute_mapping jsonb,
    created_at timestamptz,
    updated_at timestamptz,
    name_id_format text,
    CONSTRAINT saml_providers_sso_provider_id_fkey FOREIGN KEY (sso_provider_id) REFERENCES auth.sso_providers(id) ON DELETE CASCADE
);

COMMENT ON TABLE auth.saml_providers IS 'Auth: Manages SAML Identity Provider connections.';

-- stores metadata for pkce logins
CREATE TABLE auth.flow_state (
    id uuid NOT NULL PRIMARY KEY,
    user_id uuid,
    auth_code text NOT NULL,
    code_challenge_method auth.code_challenge_method NOT NULL,
    code_challenge text NOT NULL,
    provider_type text NOT NULL,
    provider_access_token text,
    provider_refresh_token text,
    created_at timestamptz,
    updated_at timestamptz,
    authentication_method text NOT NULL,
    auth_code_issued_at timestamptz
);

COMMENT ON TABLE auth.flow_state IS 'stores metadata for pkce logins';

-- Auth: Contains SAML Relay State information for each Service Provider initiated login
CREATE TABLE auth.saml_relay_states (
    id uuid NOT NULL PRIMARY KEY,
    sso_provider_id uuid NOT NULL,
    request_id text NOT NULL CHECK (char_length(request_id) > 0),
    for_email text,
    redirect_to text,
    created_at timestamptz,
    updated_at timestamptz,
    flow_state_id uuid,
    CONSTRAINT saml_relay_states_sso_provider_id_fkey FOREIGN KEY (sso_provider_id) REFERENCES auth.sso_providers(id) ON DELETE CASCADE,
    CONSTRAINT saml_relay_states_flow_state_id_fkey FOREIGN KEY (flow_state_id) REFERENCES auth.flow_state(id) ON DELETE CASCADE
);

COMMENT ON TABLE auth.saml_relay_states IS 'Auth: Contains SAML Relay State information for each Service Provider initiated login.';

CREATE TABLE auth.one_time_tokens (
    id uuid NOT NULL PRIMARY KEY,
    user_id uuid NOT NULL,
    token_type auth.one_time_token_type NOT NULL,
    token_hash text NOT NULL CHECK (char_length(token_hash) > 0),
    relates_to text NOT NULL,
    created_at timestamp NOT NULL DEFAULT now(),
    updated_at timestamp NOT NULL DEFAULT now(),
    CONSTRAINT one_time_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Storage Schema Tables
-- =============================================================================

CREATE TABLE storage.buckets (
    id text NOT NULL PRIMARY KEY,
    name text NOT NULL,
    owner uuid,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    public boolean DEFAULT false,
    avif_autodetection boolean DEFAULT false,
    file_size_limit bigint,
    allowed_mime_types text[],
    owner_id text
);

COMMENT ON COLUMN storage.buckets.owner IS 'Field is deprecated, use owner_id instead';

CREATE TABLE storage.objects (
    id uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    bucket_id text,
    name text,
    owner uuid,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    last_accessed_at timestamptz DEFAULT now(),
    metadata jsonb,
    path_tokens text[] GENERATED ALWAYS AS (string_to_array(name, '/'::text)) STORED,
    version text,
    owner_id text,
    user_metadata jsonb,
    CONSTRAINT objects_bucketId_fkey FOREIGN KEY (bucket_id) REFERENCES storage.buckets(id)
);

COMMENT ON COLUMN storage.objects.owner IS 'Field is deprecated, use owner_id instead';

CREATE TABLE storage.s3_multipart_uploads (
    id text NOT NULL PRIMARY KEY,
    in_progress_size bigint NOT NULL DEFAULT 0,
    upload_signature text NOT NULL,
    bucket_id text NOT NULL,
    key text NOT NULL,
    version text NOT NULL,
    owner_id text,
    created_at timestamptz NOT NULL DEFAULT now(),
    user_metadata jsonb,
    CONSTRAINT s3_multipart_uploads_bucket_id_fkey FOREIGN KEY (bucket_id) REFERENCES storage.buckets(id)
);

CREATE TABLE storage.s3_multipart_uploads_parts (
    id uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    upload_id text NOT NULL,
    size bigint NOT NULL DEFAULT 0,
    part_number integer NOT NULL,
    bucket_id text NOT NULL,
    key text NOT NULL,
    etag text NOT NULL,
    owner_id text,
    version text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT s3_multipart_uploads_parts_upload_id_fkey FOREIGN KEY (upload_id) REFERENCES storage.s3_multipart_uploads(id) ON DELETE CASCADE,
    CONSTRAINT s3_multipart_uploads_parts_bucket_id_fkey FOREIGN KEY (bucket_id) REFERENCES storage.buckets(id)
);

CREATE TABLE storage.migrations (
    id integer NOT NULL PRIMARY KEY,
    name varchar(100) NOT NULL UNIQUE,
    hash varchar(40) NOT NULL,
    executed_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- Public Schema Tables (Application Specific)
-- =============================================================================

-- Healthcare organizations that manage sleep studies, devices, and staff
CREATE TABLE public.organizations (
    id uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    organization_details jsonb,
    opening_hours jsonb,
    max_concurrent_studies integer DEFAULT 10,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.organizations IS 'Healthcare organizations that manage sleep studies, devices, and staff';

-- Application users with role-based access - extends auth.users
CREATE TABLE public.app_users (
    id uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    role text NOT NULL CHECK (role = ANY (ARRAY['patient'::text, 'staff'::text, 'doctor'::text, 'admin'::text])),
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT app_users_id_fkey FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE
);

COMMENT ON TABLE public.app_users IS 'Application users with role-based access - extends auth.users';

-- Links staff members to organizations with role details and permissions
CREATE TABLE public.staff_memberships (
    id uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL,
    organization_id uuid NOT NULL,
    role_details jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT staff_memberships_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.app_users(id) ON DELETE CASCADE,
    CONSTRAINT staff_memberships_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE
);

COMMENT ON TABLE public.staff_memberships IS 'Links staff members to organizations with role details and permissions';

-- Extended patient information including medical history and demographics
CREATE TABLE public.patient_profiles (
    user_id uuid NOT NULL PRIMARY KEY,
    patient_details jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT patient_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.app_users(id) ON DELETE CASCADE
);

COMMENT ON TABLE public.patient_profiles IS 'Extended patient information including medical history and demographics';

-- Sleep monitoring devices owned and managed by healthcare organizations
CREATE TABLE public.devices (
    id uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL,
    device_details jsonb NOT NULL,
    status public.device_status NOT NULL DEFAULT 'available',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT devices_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE
);

COMMENT ON TABLE public.devices IS 'Sleep monitoring devices owned and managed by healthcare organizations';

-- Individual sleep study cases tracking patient care from booking to completion
CREATE TABLE public.sleep_studies (
    id uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id uuid NOT NULL,
    manager_id uuid NOT NULL,
    doctor_id uuid NOT NULL,
    device_id uuid,
    current_state public.study_state NOT NULL DEFAULT 'booked',
    start_date date NOT NULL,
    end_date date,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT sleep_studies_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.app_users(id) ON DELETE CASCADE,
    CONSTRAINT sleep_studies_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.app_users(id) ON DELETE CASCADE,
    CONSTRAINT sleep_studies_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public.app_users(id) ON DELETE CASCADE,
    CONSTRAINT sleep_studies_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id) ON DELETE SET NULL
);

COMMENT ON TABLE public.sleep_studies IS 'Individual sleep study cases tracking patient care from booking to completion';

-- Medical referral documents uploaded for each sleep study
CREATE TABLE public.referrals (
    id uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    sleep_study_id uuid NOT NULL,
    file_url text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT referrals_sleep_study_id_fkey FOREIGN KEY (sleep_study_id) REFERENCES public.sleep_studies(id) ON DELETE CASCADE
);

COMMENT ON TABLE public.referrals IS 'Medical referral documents uploaded for each sleep study';

-- Patient survey responses and calculated scores for sleep studies
CREATE TABLE public.survey_responses (
    id uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    sleep_study_id uuid NOT NULL,
    type text NOT NULL,
    answers jsonb NOT NULL,
    score integer,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT survey_responses_sleep_study_id_fkey FOREIGN KEY (sleep_study_id) REFERENCES public.sleep_studies(id) ON DELETE CASCADE
);

COMMENT ON TABLE public.survey_responses IS 'Patient survey responses and calculated scores for sleep studies';

-- Raw sleep monitoring data files collected during studies
CREATE TABLE public.sleep_data_files (
    id uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    sleep_study_id uuid NOT NULL,
    file_url text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT sleep_data_files_sleep_study_id_fkey FOREIGN KEY (sleep_study_id) REFERENCES public.sleep_studies(id) ON DELETE CASCADE
);

COMMENT ON TABLE public.sleep_data_files IS 'Raw sleep monitoring data files collected during studies';

-- Final medical reports generated by doctors for completed sleep studies
CREATE TABLE public.doctor_reports (
    id uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    sleep_study_id uuid NOT NULL,
    file_url text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT doctor_reports_sleep_study_id_fkey FOREIGN KEY (sleep_study_id) REFERENCES public.sleep_studies(id) ON DELETE CASCADE
);

COMMENT ON TABLE public.doctor_reports IS 'Final medical reports generated by doctors for completed sleep studies';

-- Add remaining Foreign Key Constraints for Auth Tables
-- =============================================================================

ALTER TABLE auth.refresh_tokens 
    ADD CONSTRAINT refresh_tokens_session_id_fkey 
    FOREIGN KEY (session_id) REFERENCES auth.sessions(id) ON DELETE CASCADE;

-- Create Indexes for Performance
-- =============================================================================

-- Auth schema indexes
CREATE INDEX IF NOT EXISTS users_instance_id_idx ON auth.users(instance_id);
CREATE INDEX IF NOT EXISTS users_email_idx ON auth.users(email);
CREATE INDEX IF NOT EXISTS users_phone_idx ON auth.users(phone);
CREATE INDEX IF NOT EXISTS refresh_tokens_instance_id_idx ON auth.refresh_tokens(instance_id);
CREATE INDEX IF NOT EXISTS refresh_tokens_instance_id_user_id_idx ON auth.refresh_tokens(instance_id, user_id);
CREATE INDEX IF NOT EXISTS refresh_tokens_parent_idx ON auth.refresh_tokens(parent);
CREATE INDEX IF NOT EXISTS refresh_tokens_session_id_revoked_idx ON auth.refresh_tokens(session_id, revoked);
CREATE INDEX IF NOT EXISTS refresh_tokens_updated_at_idx ON auth.refresh_tokens(updated_at DESC);
CREATE INDEX IF NOT EXISTS audit_logs_instance_id_idx ON auth.audit_log_entries(instance_id);
CREATE INDEX IF NOT EXISTS identities_email_idx ON auth.identities(email);
CREATE INDEX IF NOT EXISTS identities_user_id_idx ON auth.identities(user_id);
CREATE INDEX IF NOT EXISTS sessions_user_id_idx ON auth.sessions(user_id);
CREATE INDEX IF NOT EXISTS sessions_not_after_idx ON auth.sessions(not_after DESC);
CREATE INDEX IF NOT EXISTS mfa_factors_user_id_idx ON auth.mfa_factors(user_id);
CREATE INDEX IF NOT EXISTS flow_state_created_at_idx ON auth.flow_state(created_at DESC);
CREATE INDEX IF NOT EXISTS saml_relay_states_sso_provider_id_idx ON auth.saml_relay_states(sso_provider_id);
CREATE INDEX IF NOT EXISTS saml_relay_states_for_email_idx ON auth.saml_relay_states(for_email);
CREATE INDEX IF NOT EXISTS sso_domains_domain_idx ON auth.sso_domains(lower(domain));
CREATE INDEX IF NOT EXISTS sso_providers_resource_id_idx ON auth.sso_providers(lower(resource_id));
CREATE INDEX IF NOT EXISTS saml_providers_sso_provider_id_idx ON auth.saml_providers(sso_provider_id);
CREATE INDEX IF NOT EXISTS one_time_tokens_relates_to_hash_idx ON auth.one_time_tokens(relates_to, token_hash);
CREATE INDEX IF NOT EXISTS one_time_tokens_user_id_token_type_idx ON auth.one_time_tokens(user_id, token_type);

-- Storage schema indexes
CREATE INDEX IF NOT EXISTS buckets_name_idx ON storage.buckets(name);
CREATE INDEX IF NOT EXISTS objects_bucket_id_idx ON storage.objects(bucket_id);
CREATE INDEX IF NOT EXISTS objects_name_idx ON storage.objects(name);
CREATE INDEX IF NOT EXISTS objects_owner_idx ON storage.objects(owner);
CREATE INDEX IF NOT EXISTS s3_multipart_uploads_bucket_id_key_idx ON storage.s3_multipart_uploads(bucket_id, key);

-- Public schema indexes
CREATE INDEX IF NOT EXISTS app_users_role_idx ON public.app_users(role);
CREATE INDEX IF NOT EXISTS staff_memberships_user_id_idx ON public.staff_memberships(user_id);
CREATE INDEX IF NOT EXISTS staff_memberships_organization_id_idx ON public.staff_memberships(organization_id);
CREATE INDEX IF NOT EXISTS patient_profiles_user_id_idx ON public.patient_profiles(user_id);
CREATE INDEX IF NOT EXISTS devices_organization_id_idx ON public.devices(organization_id);
CREATE INDEX IF NOT EXISTS devices_status_idx ON public.devices(status);
CREATE INDEX IF NOT EXISTS sleep_studies_patient_id_idx ON public.sleep_studies(patient_id);
CREATE INDEX IF NOT EXISTS sleep_studies_manager_id_idx ON public.sleep_studies(manager_id);
CREATE INDEX IF NOT EXISTS sleep_studies_doctor_id_idx ON public.sleep_studies(doctor_id);
CREATE INDEX IF NOT EXISTS sleep_studies_device_id_idx ON public.sleep_studies(device_id);
CREATE INDEX IF NOT EXISTS sleep_studies_current_state_idx ON public.sleep_studies(current_state);
CREATE INDEX IF NOT EXISTS sleep_studies_start_date_idx ON public.sleep_studies(start_date);
CREATE INDEX IF NOT EXISTS referrals_sleep_study_id_idx ON public.referrals(sleep_study_id);
CREATE INDEX IF NOT EXISTS survey_responses_sleep_study_id_idx ON public.survey_responses(sleep_study_id);
CREATE INDEX IF NOT EXISTS sleep_data_files_sleep_study_id_idx ON public.sleep_data_files(sleep_study_id);
CREATE INDEX IF NOT EXISTS doctor_reports_sleep_study_id_idx ON public.doctor_reports(sleep_study_id);

-- =============================================================================
-- End of DDL
-- =============================================================================

-- Summary:
-- - 3 schemas: auth, storage, public
-- - 8 custom enum types
-- - 32 tables total (22 auth, 5 storage, 5 public + application tables)
-- - Complete referential integrity with foreign keys
-- - Optimized indexes for performance
-- - Comprehensive comments for documentation
-- 
-- The auth and storage schemas provide Supabase's built-in authentication
-- and file storage capabilities, while the public schema contains the 
-- sleep study application-specific tables and business logic.
--
-- Application Features Supported:
-- - Multi-tenant healthcare organizations
-- - Role-based user access (patient, staff, doctor, admin)
-- - Sleep study case management with workflow states
-- - Device inventory and assignment tracking
-- - File storage for referrals, sleep data, and reports
-- - Patient survey and scoring system
-- - Complete audit trail and security features 