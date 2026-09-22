-- Capture the Moment schema.
-- Run this in the Supabase SQL editor once per project.
--
-- Access model: only the service_role key (used by Vercel functions) can
-- read/write this table. RLS is enabled with no anon or authenticated
-- policies, so browser clients using the anon key see nothing.

create extension if not exists "pgcrypto";

create table if not exists public.photos (
    id             uuid primary key default gen_random_uuid(),
    drive_file_id  text        not null,
    drive_thumb_id text        not null,
    caption        text        not null default '',
    captured_by    text        not null default '',
    created_at     timestamptz not null default now(),
    is_hidden      boolean     not null default false,
    ip_hash        text        not null default '',
    user_agent     text        not null default ''
);

create index if not exists photos_visible_by_time_idx
    on public.photos (created_at desc)
    where is_hidden = false;

create index if not exists photos_ip_hash_time_idx
    on public.photos (ip_hash, created_at desc);

alter table public.photos enable row level security;

-- No policies for anon/authenticated => rows are invisible to browser
-- clients. The service_role key bypasses RLS by design, which is what the
-- Vercel functions use.
