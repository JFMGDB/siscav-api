-- Tabelas principais

-- users
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  hashed_password TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- authorized_plates
CREATE TABLE IF NOT EXISTS authorized_plates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plate TEXT NOT NULL,
  normalized_plate TEXT NOT NULL UNIQUE,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- access_logs
CREATE TABLE IF NOT EXISTS access_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "timestamp" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  plate_string_detected TEXT NOT NULL,
  status access_status NOT NULL,
  image_storage_key TEXT NOT NULL,
  authorized_plate_id UUID REFERENCES authorized_plates(id) ON DELETE SET NULL
);
