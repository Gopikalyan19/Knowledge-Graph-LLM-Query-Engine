-- Run this in Supabase SQL Editor before starting the backend.

create table if not exists documents (
  id uuid primary key default gen_random_uuid(),
  doc_id text unique not null,
  filename text not null,
  status text default 'pending',
  chunk_count int default 0,
  entity_count int default 0,
  created_at timestamptz default now()
);

create table if not exists query_history (
  id uuid primary key default gen_random_uuid(),
  question text not null,
  cypher_query text,
  answer text,
  created_at timestamptz default now()
);

alter table documents enable row level security;
alter table query_history enable row level security;

-- The backend uses SUPABASE_SERVICE_ROLE_KEY, so RLS will not block backend inserts.
-- Do not expose the service role key in frontend code.
