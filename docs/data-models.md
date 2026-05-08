# Data Models & Storage

## Core Tables (Postgres/Supabase)
- **users**: id, email, name, role, status, created_at
- **profiles**: user_id, headline, summary, location, preferences
- **resumes**: id, user_id, title, source, created_at
- **resume_versions**: id, resume_id, content, summary, created_at
- **job_postings**: id, external_id, source, title, company, location, raw_text
- **applications**: id, user_id, job_id, resume_version_id, status, submitted_at
- **cover_letters**: id, user_id, job_id, content
- **templates**: id, user_id, type, content, metadata
- **prompts**: id, name, content, version
- **consent_logs**: id, user_id, action, timestamp
- **audit_logs**: id, actor_id, action, resource, timestamp

## Vector Storage
- **memory_sources**: id, user_id, source_type, metadata
- **embeddings**: id, source_id, vector, chunk_text, created_at

## Queue + Cache
- **Redis** for short-lived workflow state.
- **RabbitMQ** for async automation and notification jobs.
