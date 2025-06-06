/*
  Migration: Fix app_users RLS policies and table structure
  Description: Fixes the app_users table structure and RLS policies to allow proper user registration
  Author: Sleep Study App
  Created: 2025-01-17 14:30:00 UTC
  
  Changes:
  - Remove default gen_random_uuid() from app_users.id column since it should match auth.uid()
  - Fix buggy staff visibility policy that had incorrect self-reference
  - Ensure RLS policies work correctly for user registration flow
  
  Rationale:
  The app_users.id should be explicitly set to auth.uid() during user registration, 
  not auto-generated, as it needs to match the authenticated user's ID for RLS policies to work.
*/

-- =============================================
-- FIX APP_USERS TABLE STRUCTURE
-- =============================================

-- Remove the default value from app_users.id column
-- This column should be explicitly set to auth.uid() during user registration
alter table public.app_users 
alter column id drop default;

-- =============================================
-- FIX BUGGY RLS POLICIES
-- =============================================

-- Drop the existing buggy staff visibility policy
drop policy if exists "Staff can view app users in their organization" on public.app_users;

-- Recreate the staff visibility policy with correct logic
-- This policy allows staff members to view other app_users who are in the same organization
create policy "Staff can view app users in their organization"
  on public.app_users
  for select
  to authenticated
  using (
    -- Allow if the current user is staff and the target user is in the same organization
    (select auth.uid()) in (
      select sm1.user_id 
      from public.staff_memberships sm1
      where sm1.organization_id in (
        select sm2.organization_id 
        from public.staff_memberships sm2
        where sm2.user_id = app_users.id
      )
    )
  );

-- =============================================
-- VERIFY EXISTING POLICIES ARE CORRECT
-- =============================================

-- The existing policies should work correctly now:
-- 1. "Users can view their own app user record" - uses auth.uid() = id
-- 2. "Users can insert their own app user record" - uses auth.uid() = id in with_check
-- 3. The new staff visibility policy above

-- Note: Applications must now explicitly set app_users.id = auth.uid() when inserting records
-- since the default value has been removed. 