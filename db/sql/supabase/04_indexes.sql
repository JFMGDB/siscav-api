-- Índices recomendados

-- authorized_plates
CREATE INDEX IF NOT EXISTS idx_authorized_plates_plate_textpattern
  ON authorized_plates (plate text_pattern_ops);

-- access_logs
CREATE INDEX IF NOT EXISTS idx_access_logs_timestamp_desc
  ON access_logs ("timestamp" DESC);

CREATE INDEX IF NOT EXISTS idx_access_logs_status_timestamp_desc
  ON access_logs (status, "timestamp" DESC);

CREATE INDEX IF NOT EXISTS idx_access_logs_plate_textpattern
  ON access_logs (plate_string_detected text_pattern_ops);

CREATE INDEX IF NOT EXISTS idx_access_logs_authorized_plate_id
  ON access_logs (authorized_plate_id);

-- Opcional: busca por trechos com GIN/pg_trgm
CREATE INDEX IF NOT EXISTS idx_access_logs_plate_trgm
  ON access_logs USING GIN (plate_string_detected gin_trgm_ops);
