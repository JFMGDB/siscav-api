-- Script completo de setup do banco de dados Supabase
-- Execute este script no SQL Editor do Supabase Studio
-- Ordem de execução: Execute este arquivo completo de uma vez

-- ============================================
-- 1. HABILITAR EXTENSÕES
-- ============================================
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================
-- 2. CRIAR TIPOS ENUM
-- ============================================
CREATE TYPE access_status AS ENUM ('Authorized', 'Denied');

-- ============================================
-- 3. CRIAR TABELAS
-- ============================================

-- Tabela users
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  hashed_password TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tabela authorized_plates
CREATE TABLE IF NOT EXISTS authorized_plates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plate TEXT NOT NULL,
  normalized_plate TEXT NOT NULL UNIQUE,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tabela access_logs
CREATE TABLE IF NOT EXISTS access_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "timestamp" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  plate_string_detected TEXT NOT NULL,
  status access_status NOT NULL,
  image_storage_key TEXT NOT NULL,
  authorized_plate_id UUID REFERENCES authorized_plates(id) ON DELETE SET NULL
);

-- ============================================
-- 4. CRIAR ÍNDICES
-- ============================================

-- Índices para authorized_plates
CREATE INDEX IF NOT EXISTS idx_authorized_plates_normalized 
  ON authorized_plates(normalized_plate);

CREATE INDEX IF NOT EXISTS idx_authorized_plates_plate_textpattern
  ON authorized_plates (plate text_pattern_ops);

-- Índices para access_logs
CREATE INDEX IF NOT EXISTS idx_access_logs_timestamp_desc
  ON access_logs ("timestamp" DESC);

CREATE INDEX IF NOT EXISTS idx_access_logs_status
  ON access_logs (status);

CREATE INDEX IF NOT EXISTS idx_access_logs_status_timestamp_desc
  ON access_logs (status, "timestamp" DESC);

CREATE INDEX IF NOT EXISTS idx_access_logs_plate_textpattern
  ON access_logs (plate_string_detected text_pattern_ops);

CREATE INDEX IF NOT EXISTS idx_access_logs_authorized_plate_id
  ON access_logs (authorized_plate_id);

-- Índice opcional: busca fuzzy com pg_trgm (requer extensão pg_trgm)
CREATE INDEX IF NOT EXISTS idx_access_logs_plate_trgm
  ON access_logs USING GIN (plate_string_detected gin_trgm_ops);

-- ============================================
-- 5. VERIFICAÇÃO
-- ============================================
-- Execute estas queries para verificar se tudo foi criado corretamente:

-- Verificar tabelas
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- AND table_name IN ('users', 'authorized_plates', 'access_logs');

-- Verificar tipo ENUM
-- SELECT typname FROM pg_type WHERE typname = 'access_status';

-- Verificar extensões
-- SELECT extname FROM pg_extension WHERE extname IN ('pgcrypto', 'pg_trgm');

-- Verificar índices
-- SELECT indexname FROM pg_indexes 
-- WHERE schemaname = 'public' 
-- AND tablename IN ('users', 'authorized_plates', 'access_logs');

