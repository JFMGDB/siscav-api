-- Security hardening for api_only architecture (FastAPI + SQLAlchemy, no PostgREST client).
-- Run after tables exist. Order: REVOKE grants, enable RLS, lock down default privileges, move pg_trgm.

-- 1) Remove immediate exposure via Supabase API roles
REVOKE ALL ON TABLE public.users FROM anon, authenticated;
REVOKE ALL ON TABLE public.authorized_plates FROM anon, authenticated;
REVOKE ALL ON TABLE public.access_logs FROM anon, authenticated;
REVOKE ALL ON TABLE public.alembic_version FROM anon, authenticated;

-- 2) RLS deny-by-default (no policies for anon/authenticated)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.authorized_plates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.access_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alembic_version ENABLE ROW LEVEL SECURITY;

-- 3) Default privileges (https://supabase.com/docs/guides/api/securing-your-api)
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
  REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLES FROM anon, authenticated, service_role;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
  REVOKE EXECUTE ON FUNCTIONS FROM anon, authenticated, service_role;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
  REVOKE USAGE, SELECT ON SEQUENCES FROM anon, authenticated, service_role;

-- 4) Move pg_trgm out of public (pgcrypto should already live in extensions)
CREATE SCHEMA IF NOT EXISTS extensions;

DROP INDEX IF EXISTS public.idx_access_logs_plate_trgm;

ALTER EXTENSION pg_trgm SET SCHEMA extensions;

CREATE INDEX IF NOT EXISTS idx_access_logs_plate_trgm
  ON public.access_logs USING GIN (plate_string_detected extensions.gin_trgm_ops);
