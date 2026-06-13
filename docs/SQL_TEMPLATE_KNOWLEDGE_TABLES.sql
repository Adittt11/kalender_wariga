CREATE TABLE IF NOT EXISTS knowledge_documents (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  source_filename TEXT NOT NULL,
  file_type TEXT NOT NULL,
  raw_text TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS knowledge_chunks (
  id SERIAL PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES knowledge_documents(id)
    ON DELETE CASCADE,
  category TEXT NOT NULL,
  chunk_index INTEGER NOT NULL,
  content TEXT NOT NULL,
  embedding TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Template isi kosong untuk referensi manual.
-- Jangan dijalankan kecuali benar-benar ingin membuat baris kosong.
--
-- INSERT INTO knowledge_documents
--   (title, category, source_filename, file_type, raw_text)
-- VALUES
--   ('', 'Penglukatan', '', 'text', ''),
--   ('', 'Pembayuhan', '', 'text', ''),
--   ('', 'Tenung', '', 'text', ''),
--   ('', 'Permata', '', 'text', ''),
--   ('', 'Lontar', '', 'text', ''),
--   ('', 'Wariga', '', 'text', ''),
--   ('', 'Pengetahuan Lain', '', 'text', '');
