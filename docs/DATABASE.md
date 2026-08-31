# 🗄️ Database Architecture & Storage Justification Audit

**Release**: `v16.0.0-rc1`  
**Standard**: Justified Multi-Model Storage Architecture

---

## 📊 Infrastructure Component Matrix

| Database Engine | Purpose & Responsibility | Data Types Stored | Runtime Dependency | Performance Justification | Failure Behavior & Resilience | Validated Alternative |
|:---|:---|:---|:---:|:---|:---|:---|
| **PostgreSQL 15+** | Master relational database & system of record | Users, Auth, Profiles, RBAC, Roles, Career Twin Snapshots, Skill Evidence, Interventions, Credentials, MNC Interviews | **Critical P0** | ACID guarantees, foreign key constraints, complex joins, sub-millisecond indexed lookups | Connection pooling with retry; transactions rollback on error; read replicas supportable | MySQL / SQLite (test environment only) |
| **Redis 7+** | In-memory cache, session store & distributed rate limiter | Revoked JWT blacklist, active token sessions, Leaky-Bucket rate limiting counters, Celery task queues | **Critical P1** | Sub-millisecond latency ($<1\text{ms}$), atomic increments (`INCR`), TTL auto-expiration | In-memory fallback / fail-open rate limiting with structured logging if Redis is temporarily unreachable | Memcached / KeyDB |
| **MongoDB 7+** | High-volume unstructured telemetry & audit logs | E2E synthetic journey logs, raw webhook payloads, unparsed resume documents, telemetry receipts | **Secondary P2** | Flexible schema, JSON document ingestion, high-throughput append-only audit trail | Async worker DLQ (Dead Letter Queue); failures buffered in local memory spool without blocking core API requests | PostgreSQL JSONB |
| **Qdrant Vector DB** | Semantic vector search & similarity matching | 384D dense embeddings for skills, job descriptions, resume semantic segments | **Secondary P2** | Cosine similarity HNSW indexing for sub-10ms nearest-neighbor role matching | Fallback to deterministic Bigram / Jaccard keyword matching and exact token overlap | pgvector / Pinecone |

---

## 🔍 Elimination & Redundancy Analysis

1. **Why not consolidate MongoDB into PostgreSQL JSONB?**
   - High-velocity raw webhook logging and candidate journey event streams can produce significant write volume. MongoDB isolates unstructured event append latency from relational OLTP transactions. However, for single-node deployments, PostgreSQL JSONB serves as a valid drop-in alternative.
2. **Why not consolidate Redis into PostgreSQL?**
   - Rate limiting on every HTTP request and microsecond JWT revocation verification requires sub-millisecond execution. Offloading token blacklists to Redis prevents relational connection saturation under peak concurrency ($N=100$ concurrent requests).
3. **Why Qdrant?**
   - HNSW indexing enables scalable semantic matching between candidate evidence atoms and multi-thousand JD requirement corpuses.

---

## 🛡️ Data Rights & Zero-Trust Storage Invariants

- **Row-Level Tenant Isolation**: All relational entities mandate explicit `user_id` or `organization_id` predicates.
- **Cryptographic Signatures**: Credentials and webhooks use **HMAC-SHA256 authenticated integrity protection**.
- **Password Security**: Passwords hashed with **Argon2id** (configured with $m=65536, t=3, p=4$), designed to increase resistance to GPU/ASIC-assisted password cracking.
