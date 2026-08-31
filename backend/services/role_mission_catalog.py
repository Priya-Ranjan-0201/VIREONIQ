"""
Comprehensive Multi-Role Daily Mission Intelligence Catalog
Provides rich, realistic missions for all 8 target roles:
  1. AI/ML Engineer
  2. Backend Engineer
  3. Full Stack Engineer
  4. Data Engineer
  5. DevOps / SRE
  6. Cloud Architect
  7. Mobile Engineer
  8. Cybersecurity Engineer

Each role includes:
  - Primary mission tasks (Set 1)
  - Alternate mission tasks (Set 2 for dynamic Refresh)
  - Concrete HOW, WHERE, WHEN, WHY, TARGET MNCS, STAR BLUEPRINTS & PROOF CRITERIA
"""

from typing import Dict, Any, Optional

TOP_25_MNCS = [
    "Google", "Amazon", "Meta", "Microsoft", "Uber", "Bloomberg", "Adobe",
    "Apple", "Netflix", "Salesforce", "Atlassian", "LinkedIn", "Goldman Sachs",
    "Oracle", "Stripe", "ByteDance", "PayPal", "Intuit", "ServiceNow", "Twilio",
    "Morgan Stanley", "Cisco", "Airbnb", "Databricks", "Spotify", "Snowflake"
]

def normalize_target_role(role: Optional[str]) -> str:
    """Normalizes any role string or alias into one of the 8 canonical roles."""
    if not role:
        return "Backend Engineer"
    r = role.strip().lower()
    if "data" in r:
        return "Data Engineer"
    if "devops" in r or "sre" in r or "site reliability" in r:
        return "DevOps / SRE"
    if "cloud" in r or "architect" in r or "solutions" in r:
        return "Cloud Architect"
    if "mobile" in r or "ios" in r or "android" in r or "flutter" in r or "react native" in r:
        return "Mobile Engineer"
    if "cyber" in r or "security" in r or "appsec" in r or "infosec" in r:
        return "Cybersecurity Engineer"
    if "full" in r or "stack" in r or "frontend" in r or "web" in r:
        return "Full Stack Engineer"
    if "ai" in r or "ml" in r or "machine" in r or "deep" in r or "vision" in r or "nlp" in r:
        return "AI/ML Engineer"
    return "Backend Engineer"


ROLE_MISSION_CATALOG: Dict[str, Dict[str, Any]] = {
    # ─── 1. AI/ML ENGINEER ──────────────────────────────────────────────────
    "AI/ML Engineer": {
        "active_plan_title": "14-Day AI/ML Engineer Accelerated Readiness Sprints",
        "rationale": "Targeting your highest-ROI bottlenecks in distributed systems, feature pipelines & algorithmic complexity.",
        "tasks": [
            {
                "task_id": "aiml_task_1",
                "title": "Solve LeetCode #560: Subarray Sum Equals K (O(N) Prefix Sum)",
                "task_type": "CODING_DRILL",
                "estimated_minutes": 25,
                "projected_delta": "+1.2",
                "status": "PENDING",
                "difficulty": "Medium • Tier-1 MNC Core",
                "why": "Strengthens your Arrays & Hash Map competency for Tier-1 MNC algorithmic screening.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–5: Constraints & Edge Cases", "detail": "Clarify: Can elements or k be negative? (Yes! Negative numbers invalidate sliding window). Space/time: N <= 2*10^4."},
                        {"phase": "Minute 5–12: Mathematical Formulation", "detail": "Prefix sum property: sum(i to j) = prefix[j] - prefix[i-1] = k => prefix[i-1] = prefix[j] - k. Maintain running sum in a hash map with frequency counts. Initialize prefix_map = {0: 1}."},
                        {"phase": "Minute 12–20: Clean Implementation", "detail": "Iterate once through nums. Add current num to running sum. Check if (running_sum - k) is in prefix_map. Increment count by its frequency. Update map."},
                        {"phase": "Minute 20–25: MNC Dry-Run & Edge Cases", "detail": "Trace edge cases: nums=[1, -1, 0], k=0; nums=[1], k=0. Confirm O(N) time and O(N) auxiliary space."}
                    ],
                    "optimal_approach": "Single-pass Prefix Sum with Hash Map frequency counter. O(N) Time, O(N) Space.",
                    "code_blueprint": "def subarraySum(nums: list[int], k: int) -> int:\n    count = 0\n    current_sum = 0\n    prefix_counts = {0: 1}\n    for num in nums:\n        current_sum += num\n        if (current_sum - k) in prefix_counts:\n            count += prefix_counts[current_sum - k]\n        prefix_counts[current_sum] = prefix_counts.get(current_sum, 0) + 1\n    return count",
                    "common_pitfalls": ["Using Two Pointers or Sliding Window (fails with negative numbers or zeroes).", "Forgetting base case prefix_counts = {0: 1}.", "Adding current_sum to map before checking (current_sum - k)."]
                },
                "where": {"platform": "LeetCode #560", "url": "https://leetcode.com/problems/subarray-sum-equals-k/", "mnc_companies": ["Google", "Meta", "Amazon", "Microsoft", "Uber", "Apple"], "recommended_tools": "LeetCode Scratchpad or VS Code + Python 3.12 / Java"},
                "when": {"recommended_time": "Morning (09:00 AM – 09:25 AM) — Peak algorithmic clarity", "duration_minutes": 25, "sprint_phase": "Day 1 of 14: Data Structures Foundation"},
                "proof_criteria": {"deliverable": "Accepted LeetCode submission screenshot or GitHub commit link with runtime >85% percentile.", "verification_method": "Paste submission URL or test in MNC Coding Studio"}
            },
            {
                "task_id": "aiml_task_2",
                "title": "Draft STAR Behavioral Story on Disagreement & Architecture Tradeoff",
                "task_type": "BEHAVIORAL_STAR",
                "estimated_minutes": 20,
                "projected_delta": "+0.8",
                "status": "PENDING",
                "difficulty": "Essential • Bar Raiser Round",
                "why": "Elevates Leadership & Cultural Alignment readiness score.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–5: Situation & Context", "detail": "Pick a real technical disagreement (e.g. streaming tokens directly via SSE vs buffered polling). Set project context, deadline, and stakes."},
                        {"phase": "Minute 5–10: Task & The Conflict", "detail": "State the challenge: Team lead preferred polling for simplicity, but client p99 TTFT was failing SLAs."},
                        {"phase": "Minute 10–15: Action with Concrete Data", "detail": "Built a 1-day benchmark comparing SSE with HTTP/2 multiplexing vs chunked REST under 2,000 concurrent queries. Presented findings neutrally."},
                        {"phase": "Minute 15–20: Result & Business Impact", "detail": "Team adopted SSE; TTFT dropped from 1.4s to 240ms, user perceived latency fell by 82%."}
                    ],
                    "optimal_approach": "STAR Framework (Situation, Task, Action, Result) with measurable metrics and 'Disagree and Commit' leadership principles.",
                    "code_blueprint": "Situation: In our LLM feature pipeline, team debated streaming tokens directly via SSE vs buffered polling.\nTask: As the AI/ML engineer, needed to achieve <300ms Time-To-First-Token without overwhelming backend connection pools.\nAction: Created a 1-day benchmark testing SSE with HTTP/2 multiplexing vs chunked REST under 2,000 concurrent simulated queries.\nResult: Team adopted SSE; TTFT dropped from 1.4s to 240ms, user perceived latency fell by 82%.",
                    "common_pitfalls": ["Sounding combative or presenting teammate as incompetent.", "Lacking concrete quantifiable metrics in Result phase.", "Focusing too much on Situation rather than YOUR personal actions."]
                },
                "where": {"platform": "Vireoniq Interview Twin Studio", "url": "/app/interview-simulator", "mnc_companies": ["Amazon", "Google", "Microsoft", "Meta", "Uber", "Apple"], "recommended_tools": "Vireoniq Voice Rehearsal Studio or Smartphone Voice Memos"},
                "when": {"recommended_time": "Afternoon (02:00 PM – 02:20 PM) — Communication focus", "duration_minutes": 20, "sprint_phase": "Day 1 of 14: Leadership & Behavioral Alignment"},
                "proof_criteria": {"deliverable": "Structured 4-bullet STAR written summary or 90-second audio recording rehearsal.", "verification_method": "Submit in Vireoniq Behavioral Studio for automated AI tone scoring"}
            },
            {
                "task_id": "aiml_task_3",
                "title": "Simulate Distributed Idempotency in Notification Microservices",
                "task_type": "SYSTEM_DESIGN",
                "estimated_minutes": 15,
                "projected_delta": "+1.5",
                "status": "COMPLETED",
                "difficulty": "Advanced • HLD & LLD Core",
                "why": "Directly addresses primary bottleneck in distributed systems resilience.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–3: Idempotency Contract", "detail": "Define API contract: Client transmits unique 'Idempotency-Key: UUIDv4' in header."},
                        {"phase": "Minute 3–7: Redis Distributed Lock & Cache", "detail": "Atomic check-and-set in Redis: SET idempotency:{key} 'PROCESSING' EX 300 NX."},
                        {"phase": "Minute 7–11: Transactional Outbox & DB Commit", "detail": "Execute business logic within single ACID transaction. Write to idempotency_records table."},
                        {"phase": "Minute 11–15: Failure Modes & Recovery", "detail": "Handle worker crash before completion (TTL expires, allows safe retry)."}
                    ],
                    "optimal_approach": "Header Idempotency Key + Redis Atomic SETNX (300s TTL) + Relational Outbox Pattern for ACID guarantees.",
                    "code_blueprint": "async def process_with_idempotency(idempotency_key: str, payload: dict):\n    is_new = await redis.set(f'idemp:{idempotency_key}', 'PROCESSING', ex=300, nx=True)\n    if not is_new:\n        cached = await redis.get(f'idemp:{idempotency_key}')\n        if cached != 'PROCESSING': return json.loads(cached)\n        raise HTTPException(409, 'Request currently in-flight')\n    try:\n        result = await execute_core_action(payload)\n        await redis.set(f'idemp:{idempotency_key}', json.dumps(result), ex=86400)\n        return result\n    except Exception as exc:\n        await redis.delete(f'idemp:{idempotency_key}')\n        raise exc",
                    "common_pitfalls": ["Non-atomic check-then-set allowing race condition.", "Infinite deadlock when worker dies without TTL.", "Returning error on duplicate instead of identical previous response."]
                },
                "where": {"platform": "System Design Sandbox / Excalidraw", "url": "https://excalidraw.com", "mnc_companies": ["Uber", "Netflix", "Stripe", "Amazon", "Meta", "Google"], "recommended_tools": "Excalidraw, Draw.io, or Vireoniq System Design Architecture Sandbox"},
                "when": {"recommended_time": "Evening (05:00 PM – 05:15 PM) — Architecture synthesis", "duration_minutes": 15, "sprint_phase": "Day 1 of 14: Distributed Systems Resilience"},
                "proof_criteria": {"deliverable": "Sequence diagram showing Client, Gateway, Redis Lock, and DB Outbox.", "verification_method": "Architecture review checklist verified in Vireoniq Design Twin"}
            }
        ],
        "tasks_alt": [
            {
                "task_id": "aiml_task_alt_1",
                "title": "Solve LeetCode #239: Sliding Window Maximum (Monotonic Deque O(N))",
                "task_type": "CODING_DRILL",
                "estimated_minutes": 30,
                "projected_delta": "+1.4",
                "status": "PENDING",
                "difficulty": "Hard • Big Tech Bar Raiser",
                "why": "Crucial for streaming window tokenization and real-time tensor feature aggregations.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–7: Monotonic Deque Invariant", "detail": "Maintain double-ended queue storing indices in decreasing order of values. Front of deque is always maximum."},
                        {"phase": "Minute 7–18: Deque Pruning", "detail": "Before pushing index i, pop all elements from back smaller than nums[i]. Pop front if index < i - k + 1."},
                        {"phase": "Minute 18–30: Window Collection", "detail": "Append nums[deque[0]] to results once index i >= k - 1. Time complexity is strictly O(N)."}
                    ],
                    "optimal_approach": "Monotonic Decreasing Deque storing indices. Each index is pushed and popped at most once: O(N) Time, O(k) Space.",
                    "code_blueprint": "from collections import deque\ndef maxSlidingWindow(nums: list[int], k: int) -> list[int]:\n    q = deque()\n    res = []\n    for i, n in enumerate(nums):\n        while q and nums[q[-1]] < n:\n            q.pop()\n        q.append(i)\n        if q[0] < i - k + 1:\n            q.popleft()\n        if i >= k - 1:\n            res.append(nums[q[0]])\n    return res",
                    "common_pitfalls": ["Storing values instead of indices in deque, preventing window expiration checks.", "Using heap instead of deque (takes O(N log k) instead of O(N))."]
                },
                "where": {"platform": "LeetCode #239", "url": "https://leetcode.com/problems/sliding-window-maximum/", "mnc_companies": ["Google", "Amazon", "Meta", "ByteDance", "Uber"], "recommended_tools": "LeetCode / VS Code"},
                "when": {"recommended_time": "Morning (09:00 AM – 09:30 AM) — Deep algorithmic drill", "duration_minutes": 30, "sprint_phase": "Day 2 of 14: Monotonic Data Structures"},
                "proof_criteria": {"deliverable": "Accepted LeetCode submission passing all 51 test cases with O(N) time.", "verification_method": "Submit link in MNC Coding Studio"}
            },
            {
                "task_id": "aiml_task_alt_2",
                "title": "Architect Real-Time Vector Similarity Search Retrieval with Qdrant & HNSW",
                "task_type": "SYSTEM_DESIGN",
                "estimated_minutes": 25,
                "projected_delta": "+1.5",
                "status": "PENDING",
                "difficulty": "Senior Level • Vector DB Core",
                "why": "Core requirement for Tier-1 generative AI and semantic retrieval pipelines at OpenAI, Meta, and Databricks.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–7: Approximate Nearest Neighbors", "detail": "Evaluate HNSW (Hierarchical Navigable Small World) graph vs IVF-PQ trade-offs for 1536-dim embeddings."},
                        {"phase": "Minute 7–16: Quantization & Payload Filtering", "detail": "Implement scalar quantization (SQ) reducing memory by 4x. Configure boolean metadata filtering."},
                        {"phase": "Minute 16–25: Sharding & Replication", "detail": "Design distributed cluster with raft consensus, write-ahead logs (WAL), and sub-10ms recall p99 SLA."}
                    ],
                    "optimal_approach": "Qdrant HNSW graph index with Scalar Quantization and distributed read replicas.",
                    "code_blueprint": "from qdrant_client import QdrantClient\nfrom qdrant_client.http import models\n\nclient = QdrantClient('http://localhost:6333')\nclient.create_collection(\n    collection_name='doc_embeddings',\n    vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),\n    hnsw_config=models.HnswConfigDiff(m=16, ef_construct=100),\n    quantization_config=models.ScalarQuantization(\n        scalar=models.ScalarQuantizationConfig(type=models.ScalarType.INT8, quantile=0.99)\n    )\n)",
                    "common_pitfalls": ["Not setting ef_search appropriately (trading recall accuracy for latency).", "OOM crashes from holding full unquantized vectors in RAM."]
                },
                "where": {"platform": "Qdrant Vector Engine", "url": "https://qdrant.tech/documentation/", "mnc_companies": ["OpenAI", "Meta", "Databricks", "Microsoft", "Cohere"], "recommended_tools": "Qdrant / Docker / Python"},
                "when": {"recommended_time": "Afternoon (02:00 PM – 02:25 PM) — Vector search engineering", "duration_minutes": 25, "sprint_phase": "Day 2 of 14: Semantic Retrieval Pipelines"},
                "proof_criteria": {"deliverable": "Working Python Qdrant indexing script with hybrid search filter.", "verification_method": "Run collection verification test in Vireoniq Lab"}
            },
            {
                "task_id": "aiml_task_alt_3",
                "title": "Draft STAR Story on Optimizing GPU LLM Inference Latency Under Budget",
                "task_type": "BEHAVIORAL_STAR",
                "estimated_minutes": 15,
                "projected_delta": "+0.7",
                "status": "COMPLETED",
                "difficulty": "Bar Raiser • Cost & Scale Ownership",
                "why": "Demonstrates engineering pragmatism and resource optimization required by tech giants.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–4: Situation", "detail": "LLM inference costs spiking 300% monthly while p99 latency crossed 2.8 seconds on unoptimized HuggingFace pipeline."},
                        {"phase": "Minute 4–8: Task", "detail": "Mandate to reduce latency below 800ms and cut cloud GPU spend by 40% without losing model precision."},
                        {"phase": "Minute 8–12: Action", "detail": "Benchmarked vLLM PagedAttention and TensorRT-LLM FP8 quantization. Migrated serving from naive Torch to vLLM on AWS A10G."},
                        {"phase": "Minute 12–15: Result", "detail": "P99 latency plummeted to 480ms (5.8x faster). GPU instances cut from 12 to 4, saving $84K/yr."}
                    ],
                    "optimal_approach": "Concrete benchmark data, trade-off analysis, and verified financial ROI metrics.",
                    "code_blueprint": "Situation: LLM inference p99 latency reached 2.8s during peak customer loads, driving $18K/mo GPU spend.\nTask: Reduce latency to <800ms and reduce cluster spend by 40% ahead of marketing campaign.\nAction: Implemented vLLM engine with continuous batching, KV-cache quantization, and torch.compile optimizations.\nResult: Cut p99 latency to 480ms (82% reduction), slashed GPU instances from 12 to 4, saving $84,000 annually.",
                    "common_pitfalls": ["Claiming 'we optimized it' without explaining the specific technical levers (vLLM, continuous batching).", "Omitting exact cost and latency numbers."]
                },
                "where": {"platform": "Vireoniq Interview Twin Studio", "url": "/app/interview-simulator", "mnc_companies": ["Meta", "Google", "Amazon", "Nvidia", "Microsoft"], "recommended_tools": "Vireoniq Voice Studio"},
                "when": {"recommended_time": "Evening (05:00 PM – 05:15 PM) — Behavioral rehearsal", "duration_minutes": 15, "sprint_phase": "Day 2 of 14: Executive Communication"},
                "proof_criteria": {"deliverable": "Structured STAR written summary with before/after metrics.", "verification_method": "AI rubric evaluation"}
            }
        ]
    },

    # ─── 2. BACKEND ENGINEER ────────────────────────────────────────────────
    "Backend Engineer": {
        "active_plan_title": "14-Day Backend Engineer Accelerated Readiness Sprints",
        "rationale": "Eliminating critical bottlenecks in distributed data consistency, caching invalidation & concurrent query optimization.",
        "tasks": [
            {
                "task_id": "be_task_1",
                "title": "Solve LeetCode #146: LRU Cache Implementation (O(1) Get & Put)",
                "task_type": "CODING_DRILL",
                "estimated_minutes": 30,
                "projected_delta": "+1.3",
                "status": "PENDING",
                "difficulty": "Medium • #1 Most Asked in MNC Loops",
                "why": "Tests Doubly Linked List pointer manipulation and Hash Map composite design under strict O(1) constraints.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–5: Data Structure Strategy", "detail": "Why Hash Map alone fails: O(1) access but O(N) eviction. Combination: Hash Map (key -> node) + Doubly Linked List (order of usage) achieves O(1) for both get and put."},
                        {"phase": "Minute 5–15: Sentinel Node Architecture", "detail": "Use pseudo-head and pseudo-tail dummy sentinel nodes. This completely eliminates null-pointer boundary checks during node insertion and deletion."},
                        {"phase": "Minute 15–25: Core Methods (Get & Put)", "detail": "get(key): If in map, move node to head and return value. Else -1. put(key, val): If exists, update and move to head. If new, insert at head, and if full, pop tail.prev."},
                        {"phase": "Minute 25–30: Boundary Verification", "detail": "Test capacity=1 eviction, re-inserting existing keys, zero operations, and confirm O(1) time complexity."}
                    ],
                    "optimal_approach": "Hash Map mapping keys to Doubly Linked List nodes with Dummy Head & Dummy Tail sentinels. O(1) Time, O(Capacity) Space.",
                    "code_blueprint": "class Node:\n    def __init__(self, key=0, val=0):\n        self.key, self.val = key, val\n        self.prev = self.next = None\n\nclass LRUCache:\n    def __init__(self, capacity: int):\n        self.cap = capacity\n        self.map = {}\n        self.head, self.tail = Node(), Node()\n        self.head.next, self.tail.prev = self.tail, self.head\n\n    def _remove(self, node):\n        node.prev.next = node.next\n        node.next.prev = node.prev\n\n    def _add(self, node):\n        node.next = self.head.next\n        node.prev = self.head\n        self.head.next.prev = node\n        self.head.next = node\n\n    def get(self, key: int) -> int:\n        if key in self.map:\n            node = self.map[key]\n            self._remove(node)\n            self._add(node)\n            return node.val\n        return -1\n\n    def put(self, key: int, value: int) -> None:\n        if key in self.map:\n            self._remove(self.map[key])\n        node = Node(key, value)\n        self._add(node)\n        self.map[key] = node\n        if len(self.map) > self.cap:\n            lru = self.tail.prev\n            self._remove(lru)\n            del self.map[lru.key]",
                    "common_pitfalls": ["Forgetting to delete evicted node key from hash map.", "Forgetting to update node position during 'get' operation.", "Manual null checking without dummy sentinel nodes."]
                },
                "where": {"platform": "LeetCode #146", "url": "https://leetcode.com/problems/lru-cache/", "mnc_companies": ["Google", "Amazon", "Meta", "Microsoft", "Stripe", "Bloomberg"], "recommended_tools": "LeetCode / VS Code"},
                "when": {"recommended_time": "Morning (09:00 AM – 09:30 AM) — Core algorithmic sprint", "duration_minutes": 30, "sprint_phase": "Day 1 of 14: In-Memory Data Structures"},
                "proof_criteria": {"deliverable": "Accepted LeetCode submission passing all 22 testcases in O(1) time.", "verification_method": "Submit verified solution link"}
            },
            {
                "task_id": "be_task_2",
                "title": "Architect Zero-Downtime Database Migration via Expand-Contract Pattern",
                "task_type": "SYSTEM_DESIGN",
                "estimated_minutes": 20,
                "projected_delta": "+1.0",
                "status": "PENDING",
                "difficulty": "Senior Level • High Practical Impact",
                "why": "Demonstrates production database engineering maturity required by Stripe, GitHub, and Uber.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–5: The Problem & Lock Risk", "detail": "Renaming columns locks tables with AccessExclusiveLock, causing downtime for high-volume transactions."},
                        {"phase": "Minute 5–10: Phase 1 (Expand)", "detail": "Add new column as NULLABLE. Deploy app code that writes to BOTH old and new columns (Dual-Write)."},
                        {"phase": "Minute 10–15: Phase 2 (Backfill)", "detail": "Run background worker to backfill historical rows in small batches (e.g. 5,000 rows with 50ms pause)."},
                        {"phase": "Minute 15–20: Phase 3 (Contract)", "detail": "Switch application reads to new column. Verify 0 reads on old column. Drop old column safely."}
                    ],
                    "optimal_approach": "Expand-Contract (Parallel Run) Pattern with batched asynchronous historical backfills.",
                    "code_blueprint": "-- Step 1: Expand (Non-blocking add)\nALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);\n\n-- Step 2: Application Dual-write in code\n# writes both first_name + last_name AND full_name\n\n-- Step 3: Batched Backfill in worker\nUPDATE users SET full_name = first_name || ' ' || last_name WHERE full_name IS NULL AND id BETWEEN 1 AND 5000;\n\n-- Step 4: Contract\nALTER TABLE users DROP COLUMN IF EXISTS first_name, DROP COLUMN IF EXISTS last_name;",
                    "common_pitfalls": ["Executing massive backfill in single transaction, locking entire tables.", "Switching reads before verifying 100% of historical backfill completed.", "Not planning for rollback."]
                },
                "where": {"platform": "PostgreSQL Architecture Sandbox", "url": "https://stripe.com/blog/online-migrations", "mnc_companies": ["Stripe", "GitHub", "Shopify", "Amazon", "Uber"], "recommended_tools": "Alembic Migrations / pgAdmin"},
                "when": {"recommended_time": "Afternoon (02:00 PM – 02:20 PM) — Production engineering focus", "duration_minutes": 20, "sprint_phase": "Day 1 of 14: Production Database Operations"},
                "proof_criteria": {"deliverable": "Alembic 3-step migration plan with dual-write handler code and rollback strategy.", "verification_method": "Pass schema validation check in Vireoniq CI"}
            },
            {
                "task_id": "be_task_3",
                "title": "Draft STAR Story on Mitigating Production P0 Incident (Cascading Failures)",
                "task_type": "BEHAVIORAL_STAR",
                "estimated_minutes": 15,
                "projected_delta": "+0.7",
                "status": "COMPLETED",
                "difficulty": "Critical • SRE / Leadership Loop",
                "why": "Validates incident response maturity, psychological safety under pressure, and systematic post-mortem ownership.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–3: Situation", "detail": "Cascading failure brought down API gateway during peak flash sale, 504 Gateway Timeouts spiked to 18%."},
                        {"phase": "Minute 3–7: Task", "detail": "Immediate blast-radius containment before root cause analysis. Avoided reckless restarts."},
                        {"phase": "Minute 7–11: Action", "detail": "Enabled emergency circuit breaker shedding 30% non-essential traffic. Injected Redis cache fallback. Traffic normalized in 4 min."},
                        {"phase": "Minute 11–15: Result", "detail": "Zero customer data loss. Authored blameless post-mortem, configured automated rate limiting."}
                    ],
                    "optimal_approach": "Containment -> Triage -> Resolution -> Blameless Post-Mortem with quantifiable MTTR.",
                    "code_blueprint": "Situation: At 2:15 PM during product launch, database connection pool exhausted due to unindexed query spike.\nTask: Restore 99.9% availability within 10-minute SLA window.\nAction: Injected rate limiting at Nginx edge, shed async report exports, killed hung DB connections, and deployed hotfix index in 6 minutes.\nResult: Restored full service in 7 minutes (MTTR -58% vs avg), added DB pool watchdog.",
                    "common_pitfalls": ["Blaming other engineers for deploying bad code.", "Skipping preventive post-mortem actions.", "Failing to articulate how status was communicated during crisis."]
                },
                "where": {"platform": "Vireoniq Leadership Simulator", "url": "/app/interview-simulator", "mnc_companies": ["Google", "Amazon", "Microsoft", "Uber", "Netflix"], "recommended_tools": "Vireoniq Voice Simulator"},
                "when": {"recommended_time": "Evening (05:00 PM – 05:15 PM) — Operational reflection", "duration_minutes": 15, "sprint_phase": "Day 1 of 14: Operational Excellence"},
                "proof_criteria": {"deliverable": "Completed 4-part STAR writeup with MTTR metrics and post-mortem preventative measures.", "verification_method": "Submit for automated leadership rubric evaluation"}
            }
        ],
        "tasks_alt": [
            {
                "task_id": "be_task_alt_1",
                "title": "Solve LeetCode #200: Number of Islands (BFS/DFS Grid Traversal)",
                "task_type": "CODING_DRILL",
                "estimated_minutes": 25,
                "projected_delta": "+1.2",
                "status": "PENDING",
                "difficulty": "Medium • Essential Graph/Matrix",
                "why": "Standard MNC technical phone screen benchmark testing 2D matrix exploration without stack overflow.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–5: In-Place Marking", "detail": "Avoid visited set overhead by sinking visited land: mutate grid[r][c] = '0' directly."},
                        {"phase": "Minute 5–15: BFS Queue Traversal", "detail": "Iterate row by row. When '1' encountered, increment island count and initiate BFS queue to flood-fill adjacent horizontal/vertical land cells."},
                        {"phase": "Minute 15–25: Boundary Checks", "detail": "Verify 0 <= nr < rows and 0 <= nc < cols before pushing to queue. Complexity: O(M*N) time, O(min(M,N)) space."}
                    ],
                    "optimal_approach": "In-place grid sinking with BFS queue for O(M*N) time and optimal memory usage.",
                    "code_blueprint": "from collections import deque\ndef numIslands(grid: list[list[str]]) -> int:\n    if not grid: return 0\n    rows, cols = len(grid), len(grid[0])\n    count = 0\n    for r in range(rows):\n        for c in range(cols):\n            if grid[r][c] == '1':\n                count += 1\n                q = deque([(r, c)])\n                grid[r][c] = '0'\n                while q:\n                    cr, cc = q.popleft()\n                    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:\n                        nr, nc = cr + dr, cc + dc\n                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == '1':\n                            grid[nr][nc] = '0'\n                            q.append((nr, nc))\n    return count",
                    "common_pitfalls": ["Mutating grid after popping from queue instead of before pushing (causes duplicate entries and TLE).", "Checking diagonal directions (islands only connect 4-directionally)."]
                },
                "where": {"platform": "LeetCode #200", "url": "https://leetcode.com/problems/number-of-islands/", "mnc_companies": ["Amazon", "Microsoft", "Bloomberg", "Google", "Meta"], "recommended_tools": "LeetCode / Python"},
                "when": {"recommended_time": "Morning (09:00 AM – 09:25 AM) — Matrix traversal sprint", "duration_minutes": 25, "sprint_phase": "Day 2 of 14: Graph & Matrix Algorithms"},
                "proof_criteria": {"deliverable": "Accepted LeetCode submission passing 100% test cases.", "verification_method": "MNC Coding Studio"}
            },
            {
                "task_id": "be_task_alt_2",
                "title": "Design Distributed Rate Limiter Using Redis Token Bucket & Lua Script",
                "task_type": "SYSTEM_DESIGN",
                "estimated_minutes": 25,
                "projected_delta": "+1.4",
                "status": "PENDING",
                "difficulty": "Senior • Distributed Caching",
                "why": "Guarantees atomic API throttling without race conditions under 100,000 concurrent requests/sec.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–7: Token Bucket Invariants", "detail": "Capacity C, refill rate R tokens/sec. Instead of active background timer, compute replenished tokens dynamically based on timestamp delta."},
                        {"phase": "Minute 7–16: Redis Lua Atomicity", "detail": "Execute read-calculate-write in single atomic Redis EVAL script to completely prevent race conditions."},
                        {"phase": "Minute 16–25: Headers & Degraded Mode", "detail": "Return X-RateLimit-Limit, X-RateLimit-Remaining, and Retry-After headers with graceful in-memory fallback."}
                    ],
                    "optimal_approach": "Redis Token Bucket with single atomic Lua script calculating continuous time elapsed.",
                    "code_blueprint": "LUA_SCRIPT = \"\"\"\nlocal key = KEYS[1]\nlocal capacity = tonumber(ARGV[1])\nlocal refill_rate = tonumber(ARGV[2])\nlocal now = tonumber(ARGV[3])\n\nlocal data = redis.call('HMGET', key, 'tokens', 'last_updated')\nlocal tokens = tonumber(data[1]) or capacity\nlocal last_updated = tonumber(data[2]) or now\n\nlocal elapsed = math.max(0, now - last_updated)\ntokens = math.min(capacity, tokens + (elapsed * refill_rate))\n\nif tokens >= 1 then\n    tokens = tokens - 1\n    redis.call('HMSET', key, 'tokens', tokens, 'last_updated', now)\n    redis.call('EXPIRE', key, 3600)\n    return 1\nelse\n    return 0\nend\n\"\"\"",
                    "common_pitfalls": ["Calling Redis GET then SET in application code (race condition causes 2x rate limit breach).", "Using fixed window counters which allow double bursts across window boundaries."]
                },
                "where": {"platform": "Distributed Systems Sandbox", "url": "https://redis.io/docs/manual/patterns/distributed-locks/", "mnc_companies": ["Stripe", "Cloudflare", "Netflix", "Amazon", "Twitter/X"], "recommended_tools": "Redis CLI / Python redis-py"},
                "when": {"recommended_time": "Afternoon (02:00 PM – 02:25 PM) — API gateway resilience", "duration_minutes": 25, "sprint_phase": "Day 2 of 14: Distributed Rate Limiting"},
                "proof_criteria": {"deliverable": "Working Lua rate limiting script benchmarked under simulated concurrency.", "verification_method": "Vireoniq Design Twin"}
            },
            {
                "task_id": "be_task_alt_3",
                "title": "Draft STAR Story on Scaling API Gateway to 50,000 TPS for Flash Sale",
                "task_type": "BEHAVIORAL_STAR",
                "estimated_minutes": 15,
                "projected_delta": "+0.7",
                "status": "COMPLETED",
                "difficulty": "Senior Level • High Concurrency",
                "why": "Demonstrates proven track record handling extreme traffic spikes and capacity planning.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–4: Situation", "detail": "Annual flash sale expected to drive 5x regular peak traffic (50,000 TPS), existing gateway was throttling at 12,000 TPS."},
                        {"phase": "Minute 4–8: Task", "detail": "Scale gateway, eliminate DB read bottlenecks, and implement graceful degradation so core checkout never fails."},
                        {"phase": "Minute 8–12: Action", "detail": "Introduced Redis Cluster multi-level caching, asynchronous queuing with Kafka, and non-blocking connection pooling."},
                        {"phase": "Minute 12–15: Result", "detail": "Sustained 54,000 TPS peak with zero downtime, average latency 28ms, driving $4.2M in sale revenue."}
                    ],
                    "optimal_approach": "Quantified capacity planning and layered architecture defense.",
                    "code_blueprint": "Situation: Anticipated 50,000 TPS load for Black Friday; existing infrastructure degraded at 14,000 TPS.\nTask: Re-architect ingress API gateway within 4 weeks to guarantee 99.99% uptime under 4x traffic.\nAction: Deployed Envoy proxy with distributed Redis caching, connection multiplexing, and priority queuing for checkout APIs.\nResult: Handled 52,400 TPS with 34ms p99 latency; zero dropped transactions and 100% uptime.",
                    "common_pitfalls": ["Focusing purely on throwing more servers at the problem without architectural optimizations.", "Not mentioning the business dollar impact of the sale."]
                },
                "where": {"platform": "Vireoniq Interview Twin Studio", "url": "/app/interview-simulator", "mnc_companies": ["Amazon", "Uber", "Walmart", "Shopify", "DoorDash"], "recommended_tools": "Vireoniq Audio Simulator"},
                "when": {"recommended_time": "Evening (05:00 PM – 05:15 PM) — Leadership rehearsal", "duration_minutes": 15, "sprint_phase": "Day 2 of 14: Concurrency & Scale"},
                "proof_criteria": {"deliverable": "Structured STAR writeup with TPS and latency metrics.", "verification_method": "Automated AI rubric evaluation"}
            }
        ]
    },

    # ─── 3. FULL STACK ENGINEER ─────────────────────────────────────────────
    "Full Stack Engineer": {
        "active_plan_title": "14-Day Full Stack Engineer Accelerated Readiness Sprints",
        "rationale": "Unifying high-throughput frontend reactivity, asynchronous state reconciliation & resilient API contracts.",
        "tasks": [
            {
                "task_id": "fs_task_1",
                "title": "Solve LeetCode #3: Longest Substring Without Repeating Characters",
                "task_type": "CODING_DRILL",
                "estimated_minutes": 25,
                "projected_delta": "+1.1",
                "status": "PENDING",
                "difficulty": "Medium • Essential Sliding Window",
                "why": "Evaluates dynamic sliding window two-pointer tracking and hash index lookup under linear O(N) performance.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–5: Window Boundaries", "detail": "Maintain [left, right] pointers. When char at 'right' is already in window, jump 'left' to last_seen_index + 1."},
                        {"phase": "Minute 5–12: Hash Map Index Jump", "detail": "Store character -> last seen index. Jump left = max(left, map[char] + 1) to achieve pure O(N) execution."},
                        {"phase": "Minute 12–20: Implementation", "detail": "Track max_length = max(max_length, right - left + 1) at each step. Update map[char] = right."},
                        {"phase": "Minute 20–25: Edge Case Verification", "detail": "Check empty string, single char, repeating chars ('bbbb'). Confirm O(N) time and O(min(N, Alphabet)) space."}
                    ],
                    "optimal_approach": "Sliding Window with Hash Map Index Pointer Jump. O(N) Time, O(min(M, N)) Space.",
                    "code_blueprint": "def lengthOfLongestSubstring(s: str) -> int:\n    char_map = {}\n    left = 0\n    max_len = 0\n    for right, ch in enumerate(s):\n        if ch in char_map and char_map[ch] >= left:\n            left = char_map[ch] + 1\n        char_map[ch] = right\n        max_len = max(max_len, right - left + 1)\n    return max_len",
                    "common_pitfalls": ["Forgetting char_map[ch] >= left, causing left pointer to jump backwards.", "Using string slicing inside loop turning O(N) into O(N^2)."]
                },
                "where": {"platform": "LeetCode #3", "url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/", "mnc_companies": ["Google", "Meta", "Amazon", "Microsoft", "Uber", "Apple"], "recommended_tools": "LeetCode / VS Code"},
                "when": {"recommended_time": "Morning (09:00 AM – 09:25 AM) — Algorithmic sharpness", "duration_minutes": 25, "sprint_phase": "Day 1 of 14: Two-Pointer & Sliding Window Mastery"},
                "proof_criteria": {"deliverable": "Accepted LeetCode solution with 100% test suite passing.", "verification_method": "Submission link verified in Vireoniq Coding Studio"}
            },
            {
                "task_id": "fs_task_2",
                "title": "Implement Optimistic UI Mutations with Automatic Rollback & Toast Feedback",
                "task_type": "BUILD",
                "estimated_minutes": 25,
                "projected_delta": "+1.2",
                "status": "PENDING",
                "difficulty": "Intermediate • Client Architecture",
                "why": "Creates instant snappy client responsiveness expected in Tier-1 product applications (Linear, Figma, Notion).",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–5: Optimistic State Architecture", "detail": "Snapshot current state to previousState before firing network request."},
                        {"phase": "Minute 5–12: Instant Cache Mutation", "detail": "Apply expected successful state to UI state immediately (0ms latency)."},
                        {"phase": "Minute 12–20: Error Catch & Rollback", "detail": "On 500/timeout error, catch exception, revert cache to previousState, and trigger toast notification."},
                        {"phase": "Minute 20–25: Conflict Handling", "detail": "On settled, invalidate query to synchronize with ultimate server truth."}
                    ],
                    "optimal_approach": "Optimistic Cache Update + Snapshot Capture + OnError Rollback with User Notification.",
                    "code_blueprint": "const useUpdateTaskMutation = () => {\n  const queryClient = useQueryClient();\n  return useMutation({\n    mutationFn: (updatedTask) => api.updateTask(updatedTask),\n    onMutate: async (newTask) => {\n      await queryClient.cancelQueries({ queryKey: ['tasks'] });\n      const previousTasks = queryClient.getQueryData(['tasks']);\n      queryClient.setQueryData(['tasks'], (old) =>\n        old.map((t) => (t.id === newTask.id ? { ...t, ...newTask } : t))\n      );\n      return { previousTasks };\n    },\n    onError: (err, newTask, context) => {\n      queryClient.setQueryData(['tasks'], context?.previousTasks);\n      toast.error('Network sync failed. Changes reverted.');\n    },\n    onSettled: () => {\n      queryClient.invalidateQueries({ queryKey: ['tasks'] });\n    },\n  });\n};",
                    "common_pitfalls": ["Failing to cancel outgoing queries before setting optimistic cache.", "Not providing user notification when rollback happens.", "Ignoring network timeout situations."]
                },
                "where": {"platform": "React 18 + TanStack Query Sandbox", "url": "https://tanstack.com/query/latest/docs/framework/react/guides/optimistic-updates", "mnc_companies": ["Meta", "Uber", "Airbnb", "Atlassian", "Stripe"], "recommended_tools": "Vite + React Playground"},
                "when": {"recommended_time": "Afternoon (02:00 PM – 02:25 PM) — Frontend engineering", "duration_minutes": 25, "sprint_phase": "Day 1 of 14: Client State Management"},
                "proof_criteria": {"deliverable": "Working optimistic mutation component with rollback and error toasts.", "verification_method": "Interactive demo in Vireoniq Sandbox"}
            },
            {
                "task_id": "fs_task_3",
                "title": "Draft STAR Story on Balancing Technical Debt vs Product Launch Deadlines",
                "task_type": "BEHAVIORAL_STAR",
                "estimated_minutes": 15,
                "projected_delta": "+0.7",
                "status": "COMPLETED",
                "difficulty": "Essential • Product Mindset",
                "why": "Validates ability to navigate trade-offs between clean architecture and commercial delivery velocity.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–3: Situation", "detail": "2 weeks before Q3 demo, product needed instant export feature; backend lacked batch export pipeline."},
                        {"phase": "Minute 3–7: Task", "detail": "Deliver export without locking relational DB or hacking brittle client-side CSV generator."},
                        {"phase": "Minute 7–11: Action", "detail": "Implemented lightweight streamed chunked JSON export with client-side Blob generator. Logged technical debt ticket with clear threshold trigger."},
                        {"phase": "Minute 11–15: Result", "detail": "Launched on time, 100% success rate, seamlessly migrated to S3 queue when traffic reached target threshold."}
                    ],
                    "optimal_approach": "Engineering pragmatism: Deliberate technical debt with documented repayment triggers.",
                    "code_blueprint": "Situation: 2 weeks before Q3 demo, product needed instant export feature; backend lacked batch export pipeline.\nTask: Deliver export without locking relational DB or hacking brittle client-side CSV generator.\nAction: Implemented lightweight streamed chunked JSON export with client-side Blob generator. Logged technical debt ticket with clear threshold trigger.\nResult: Launched on time, 100% success rate, seamlessly migrated to S3 queue when traffic reached target threshold.",
                    "common_pitfalls": ["Refusing to compromise with product, appearing dogmatic.", "Accumulating tech debt silently without documenting.", "Delivering poor quality code that crashes production."]
                },
                "where": {"platform": "Vireoniq Interview Twin Studio", "url": "/app/interview-simulator", "mnc_companies": ["Meta", "Google", "Amazon", "Microsoft", "Apple", "Uber"], "recommended_tools": "Vireoniq Audio Simulator"},
                "when": {"recommended_time": "Evening (05:00 PM – 05:15 PM) — Behavioral mastery", "duration_minutes": 15, "sprint_phase": "Day 1 of 14: Product Engineering Leadership"},
                "proof_criteria": {"deliverable": "Written STAR reflection highlighting measurable business outcome.", "verification_method": "Submit for automated AI rubric scoring"}
            }
        ],
        "tasks_alt": [
            {
                "task_id": "fs_task_alt_1",
                "title": "Solve LeetCode #15: 3Sum (Two Pointers with Duplicate Avoidance)",
                "task_type": "CODING_DRILL",
                "estimated_minutes": 25,
                "projected_delta": "+1.3",
                "status": "PENDING",
                "difficulty": "Medium • Essential Two-Pointer Pattern",
                "why": "Standard MNC screener testing two-pointer convergence and duplicate pruning in O(N^2) time.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–5: Sort & Fix First Element", "detail": "Sort array first (O(N log N)). Iterate i from 0 to N-3. If nums[i] > 0, break early (cannot sum to 0)."},
                        {"phase": "Minute 5–15: Two Pointers & Duplicate Pruning", "detail": "Set left = i + 1, right = N - 1. When total == 0, append triplet and skip identical elements on both sides."},
                        {"phase": "Minute 15–25: Boundary Checks", "detail": "Skip outer loop if nums[i] == nums[i-1]. Confirms O(N^2) time and O(1) extra space."}
                    ],
                    "optimal_approach": "Sort + Two Pointer convergence with adjacent duplicate suppression.",
                    "code_blueprint": "def threeSum(nums: list[int]) -> list[list[int]]:\n    nums.sort()\n    res = []\n    for i in range(len(nums) - 2):\n        if i > 0 and nums[i] == nums[i-1]: continue\n        if nums[i] > 0: break\n        l, r = i + 1, len(nums) - 1\n        while l < r:\n            s = nums[i] + nums[l] + nums[r]\n            if s < 0: l += 1\n            elif s > 0: r -= 1\n            else:\n                res.append([nums[i], nums[l], nums[r]])\n                while l < r and nums[l] == nums[l+1]: l += 1\n                while l < r and nums[r] == nums[r-1]: r -= 1\n                l += 1; r -= 1\n    return res",
                    "common_pitfalls": ["Using a set to remove duplicates at the end instead of skipping in-place (causes TLE).", "Skipping the outer loop check before evaluating the first element."]
                },
                "where": {"platform": "LeetCode #15", "url": "https://leetcode.com/problems/3sum/", "mnc_companies": ["Meta", "Amazon", "Apple", "Google", "Microsoft"], "recommended_tools": "LeetCode / Python"},
                "when": {"recommended_time": "Morning (09:00 AM – 09:25 AM) — Two-pointer mastery", "duration_minutes": 25, "sprint_phase": "Day 2 of 14: Sorting & Two Pointers"},
                "proof_criteria": {"deliverable": "Accepted LeetCode submission passing all 312 test cases in O(N^2) time.", "verification_method": "Vireoniq Coding Studio"}
            },
            {
                "task_id": "fs_task_alt_2",
                "title": "Architect Real-Time Collaborative Canvas / Document State with WebSockets & CRDTs",
                "task_type": "SYSTEM_DESIGN",
                "estimated_minutes": 25,
                "projected_delta": "+1.5",
                "status": "PENDING",
                "difficulty": "Senior • Real-Time Systems",
                "why": "Core architecture of modern full-stack web products like Figma, Miro, Notion, and Google Docs.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–7: Conflict Resolution", "detail": "Compare Operational Transformation (OT) vs Conflict-free Replicated Data Types (CRDTs). Choose Yjs/Automerge."},
                        {"phase": "Minute 7–16: WebSocket Server Ingress", "detail": "Design awareness state (cursor coordinates, active selections) via ephemeral WebSockets, and document deltas via binary state vectors."},
                        {"phase": "Minute 16–25: Offline Persistence", "detail": "Local IndexedDB caching + automatic reconciliation upon network reconnection without server lock contention."}
                    ],
                    "optimal_approach": "Yjs CRDT state synchronization over WebSockets with IndexedDB local persistence.",
                    "code_blueprint": "import * as Y from 'yjs';\nimport { WebsocketProvider } from 'y-websocket';\nimport { IndexeddbPersistence } from 'y-indexeddb';\n\nconst doc = new Y.Doc();\nconst idb = new IndexeddbPersistence('collab-canvas', doc);\nconst ws = new WebsocketProvider('wss://api.vireoniq.com/ws/collab', 'room-101', doc);\n\nconst yElements = doc.getArray('elements');\nyElements.observe((event) => {\n  console.log('Remote state updated without conflict:', event.changes.delta);\n});",
                    "common_pitfalls": ["Overwriting full document state instead of granular vector deltas.", "Sending high-frequency cursor updates over reliable TCP without throttling/RAF."]
                },
                "where": {"platform": "WebSocket Architecture Sandbox", "url": "https://docs.yjs.dev/", "mnc_companies": ["Figma", "Notion", "Atlassian", "Canva", "Google"], "recommended_tools": "VS Code / React / WebSockets"},
                "when": {"recommended_time": "Afternoon (02:00 PM – 02:25 PM) — Collaborative real-time design", "duration_minutes": 25, "sprint_phase": "Day 2 of 14: Event-Driven WebSockets"},
                "proof_criteria": {"deliverable": "Functional collaborative canvas demo showing instant sync across two browser windows.", "verification_method": "Vireoniq Design Twin"}
            },
            {
                "task_id": "fs_task_alt_3",
                "title": "Draft STAR Story on Resolving Cross-Functional Bottlenecks with Design & Product",
                "task_type": "BEHAVIORAL_STAR",
                "estimated_minutes": 15,
                "projected_delta": "+0.7",
                "status": "COMPLETED",
                "difficulty": "Essential • Product Collaboration",
                "why": "Demonstrates cross-functional empathy and ability to ship design systems that empower non-engineers.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–4: Situation", "detail": "Design team continually submitted Figma specs with ad-hoc colors/spacing; engineering spent 40% of sprint time fixing CSS regressions."},
                        {"phase": "Minute 4–8: Task", "detail": "Establish unified design token pipeline bridging Figma Tokens and Tailwind CSS to eliminate handoff friction."},
                        {"phase": "Minute 8–12: Action", "detail": "Built automated GitHub Action syncing Figma token JSON into CSS variables; co-authored component library with design lead."},
                        {"phase": "Minute 12–15: Result", "detail": "UI implementation velocity increased by 65%; visual regressions dropped to zero across 4 product releases."}
                    ],
                    "optimal_approach": "Systemic design system engineering with automated tooling over manual review meetings.",
                    "code_blueprint": "Situation: UI inconsistency and design handoff disputes were consuming 40% of frontend sprint bandwidth.\nTask: Create a single source of truth connecting Figma design tokens with our production React component library.\nAction: Implemented automated token sync pipeline converting Figma JSON to Tailwind CSS tokens, and established weekly component office hours.\nResult: Reduced sprint UI bug tickets by 72% and accelerated feature delivery by 2 weeks per release.",
                    "common_pitfalls": ["Sounding like an adversary complaining about designers.", "Not mentioning the business speed and consistency benefits."]
                },
                "where": {"platform": "Vireoniq Interview Twin Studio", "url": "/app/interview-simulator", "mnc_companies": ["Airbnb", "Meta", "Stripe", "Uber", "Apple"], "recommended_tools": "Vireoniq Voice Studio"},
                "when": {"recommended_time": "Evening (05:00 PM – 05:15 PM) — Behavioral mastery", "duration_minutes": 15, "sprint_phase": "Day 2 of 14: Cross-Functional Alignment"},
                "proof_criteria": {"deliverable": "STAR story writeup with quantified design system velocity metrics.", "verification_method": "Automated AI rubric"}
            }
        ]
    },

    # ─── 4. DATA ENGINEER ───────────────────────────────────────────────────
    "Data Engineer": {
        "active_plan_title": "14-Day Data Engineer Accelerated Readiness Sprints",
        "rationale": "Eliminating critical bottlenecks in distributed lakehouse partitioning, streaming pipelines & idempotent batch transformations.",
        "tasks": [
            {
                "task_id": "de_task_1",
                "title": "Solve LeetCode #185: Department Top Three Salaries (SQL DENSE_RANK)",
                "task_type": "CODING_DRILL",
                "estimated_minutes": 25,
                "projected_delta": "+1.2",
                "status": "PENDING",
                "difficulty": "Medium • Tier-1 Big Data Core",
                "why": "Evaluates SQL analytical window partitioning, DENSE_RANK() vs RANK(), and subquery filtering under large enterprise data volumes.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–5: Window Function Strategy", "detail": "Why RANK() fails: ties produce non-consecutive ranks (1, 1, 3). DENSE_RANK() guarantees consecutive sequence (1, 1, 2, 3), critical for 'top 3 unique salaries'."},
                        {"phase": "Minute 5–15: CTE Partitioning", "detail": "Construct CTE with DENSE_RANK() OVER (PARTITION BY departmentId ORDER BY salary DESC) as salary_rank."},
                        {"phase": "Minute 15–25: Filter & Join", "detail": "Select from CTE where salary_rank <= 3. Join with Department table on id to retrieve readable department names."}
                    ],
                    "optimal_approach": "CTE with DENSE_RANK() window function partitioned by Department. O(N log N) sorting time, O(N) space.",
                    "code_blueprint": "WITH RankedSalaries AS (\n    SELECT\n        d.name AS Department,\n        e.name AS Employee,\n        e.salary AS Salary,\n        DENSE_RANK() OVER (\n            PARTITION BY e.departmentId \n            ORDER BY e.salary DESC\n        ) AS rnk\n    FROM Employee e\n    JOIN Department d ON e.departmentId = d.id\n)\nSELECT Department, Employee, Salary\nFROM RankedSalaries\nWHERE rnk <= 3;",
                    "common_pitfalls": ["Using RANK() instead of DENSE_RANK(), which excludes the 3rd distinct salary if there is a tie for 1st or 2nd.", "Using subquery count of higher salaries instead of window functions, causing O(N^2) execution on large tables."]
                },
                "where": {"platform": "LeetCode #185", "url": "https://leetcode.com/problems/department-top-three-salaries/", "mnc_companies": ["Snowflake", "Databricks", "Amazon", "Meta", "Google", "Bloomberg"], "recommended_tools": "PostgreSQL / Snowflake / LeetCode"},
                "when": {"recommended_time": "Morning (09:00 AM – 09:25 AM) — SQL analytical query sprint", "duration_minutes": 25, "sprint_phase": "Day 1 of 14: Analytical SQL & Window Functions"},
                "proof_criteria": {"deliverable": "Accepted SQL submission passing all test cases.", "verification_method": "MNC Coding Studio"}
            },
            {
                "task_id": "de_task_2",
                "title": "Architect Stream-Table Join Pipeline with Apache Flink & Kafka Debezium CDC",
                "task_type": "SYSTEM_DESIGN",
                "estimated_minutes": 25,
                "projected_delta": "+1.4",
                "status": "PENDING",
                "difficulty": "Advanced • Streaming Architecture",
                "why": "Demonstrates real-time stateful stream processing, watermarking, and out-of-order event reconciliation.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–7: Ingress & CDC Architecture", "detail": "Capture relational OLTP changes via Debezium CDC into Kafka topic. Stream telemetry events in real-time."},
                        {"phase": "Minute 7–16: Stateful Join with Flink", "detail": "Implement Interval Join or Temporal Table Join with event-time watermarking to tolerate up to 10s network latency."},
                        {"phase": "Minute 16–25: Checkpointing & Exactly-Once", "detail": "Configure RocksDB state backend with incremental checkpoints to S3 and two-phase commit (2PC) sinks."}
                    ],
                    "optimal_approach": "Kafka CDC + Apache Flink Temporal Table Join with event-time watermarks and RocksDB state backend.",
                    "code_blueprint": "from pyflink.datastream import StreamExecutionEnvironment\nfrom pyflink.table import StreamTableEnvironment\n\nenv = StreamExecutionEnvironment.get_execution_environment()\nenv.enable_checkpointing(10000) # 10s checkpoint\nt_env = StreamTableEnvironment.create(env)\n\nt_env.execute_sql(\"\"\"\nCREATE TABLE orders (\n    order_id STRING,\n    user_id STRING,\n    amount DECIMAL(10, 2),\n    order_time TIMESTAMP(3),\n    WATERMARK FOR order_time AS order_time - INTERVAL '5' SECOND\n) WITH ('connector' = 'kafka', 'topic' = 'orders_cdc', 'format' = 'json');\n\"\"\")",
                    "common_pitfalls": ["Using processing time instead of event time, resulting in out-of-order data corruption during network jitter.", "Not tuning RocksDB state memory, leading to JVM off-heap OOM."]
                },
                "where": {"platform": "Apache Flink Architecture Blueprint", "url": "https://flink.apache.org/", "mnc_companies": ["Uber", "Netflix", "Databricks", "Stripe", "LinkedIn", "ByteDance"], "recommended_tools": "PyFlink / Kafka / Docker"},
                "when": {"recommended_time": "Afternoon (02:00 PM – 02:25 PM) — Streaming pipeline design", "duration_minutes": 25, "sprint_phase": "Day 1 of 14: Real-Time Stream Processing"},
                "proof_criteria": {"deliverable": "Stream-Table join architecture diagram and Flink SQL schema.", "verification_method": "Vireoniq Design Twin"}
            },
            {
                "task_id": "de_task_3",
                "title": "Draft STAR Story on Resolving Silent Data Drift & Pipeline Schema Breaks in Production",
                "task_type": "BEHAVIORAL_STAR",
                "estimated_minutes": 15,
                "projected_delta": "+0.8",
                "status": "COMPLETED",
                "difficulty": "Crucial • Data Governance Loop",
                "why": "Validates proactive observability, Great Expectations schema contracts, and stakeholder communication during critical data corruption.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–3: Situation", "detail": "Upstream microservice deployed unannounced schema change, breaking daily executive financial reporting pipeline."},
                        {"phase": "Minute 3–7: Task", "detail": "Identify corrupted partition range, isolate downstream tables, and backfill verified historical records without data loss."},
                        {"phase": "Minute 7–11: Action", "detail": "Halted automated ingestion, quarantined invalid records to dead-letter storage, re-ran backfill, and instituted automated schema contract enforcement (Protobuf/Great Expectations)."},
                        {"phase": "Minute 11–15: Result", "detail": "Restored reporting with 0 discrepancy; eliminated schema-breaking incidents by 100% via pre-merge schema validation gates."}
                    ],
                    "optimal_approach": "Proactive isolation -> Targeted backfill -> Automated schema registry enforcement.",
                    "code_blueprint": "Situation: Upstream team altered payment payload types without warning, corrupting 1.8M daily revenue analytics rows.\nTask: Reconcile financial records with payment gateways within 4 hours before board financial closing.\nAction: Quarantined tainted data, ran PySpark backfill comparing raw Stripe webhooks, and enforced Great Expectations schema CI checks.\nResult: Zero financial reporting errors; automated schema registry prevented 14 subsequent breaking changes.",
                    "common_pitfalls": ["Failing to mention quarantine/circuit-breaker steps that prevented bad data from spreading downstream.", "Focusing only on the technical SQL fix rather than governance preventative measures."]
                },
                "where": {"platform": "Vireoniq Leadership Simulator", "url": "/app/interview-simulator", "mnc_companies": ["Snowflake", "Stripe", "Amazon", "Goldman Sachs", "Meta"], "recommended_tools": "Vireoniq Voice Simulator"},
                "when": {"recommended_time": "Evening (05:00 PM – 05:15 PM) — Data governance reflection", "duration_minutes": 15, "sprint_phase": "Day 1 of 14: Data Quality & Governance"},
                "proof_criteria": {"deliverable": "4-part STAR writeup detailing root cause, quarantine, and schema registry prevention.", "verification_method": "Automated AI rubric"}
            }
        ],
        "tasks_alt": [
            {
                "task_id": "de_task_alt_1",
                "title": "Solve LeetCode #42: Trapping Rain Water (Two-Pointer Elevation Volume Calculation)",
                "task_type": "CODING_DRILL",
                "estimated_minutes": 30,
                "projected_delta": "+1.5",
                "status": "PENDING",
                "difficulty": "Hard • Big Tech Algorithmic Standard",
                "why": "Demonstrates optimal space efficiency O(1) and coordinate convergence essential for physical metric aggregations.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–7: Invariant Analysis", "detail": "Water trapped at index i is determined by min(max_left, max_right) - height[i]. Two pointers eliminate O(N) array storage."},
                        {"phase": "Minute 7–20: Two Pointer Convergence", "detail": "Move pointer from shorter side inwards. Update left_max or right_max, adding difference to accumulated water volume."},
                        {"phase": "Minute 20–30: Edge Verification", "detail": "Check monotonic heights ([1,2,3,4,5] -> 0), empty list, and valleys. Time: O(N), Auxiliary Space: O(1)."}
                    ],
                    "optimal_approach": "Two Pointers moving inwards with left_max and right_max bounds. O(N) Time, O(1) Space.",
                    "code_blueprint": "def trap(height: list[int]) -> int:\n    if not height: return 0\n    l, r = 0, len(height) - 1\n    left_max, right_max = height[l], height[r]\n    water = 0\n    while l < r:\n        if left_max < right_max:\n            l += 1\n            left_max = max(left_max, height[l])\n            water += left_max - height[l]\n        else:\n            r -= 1\n            right_max = max(right_max, height[r])\n            water += right_max - height[r]\n    return water",
                    "common_pitfalls": ["Using nested loops O(N^2), timing out on 100,000 array sizes.", "Forgetting to update max bounds before adding trapped water."]
                },
                "where": {"platform": "LeetCode #42", "url": "https://leetcode.com/problems/trapping-rain-water/", "mnc_companies": ["Google", "Amazon", "Bloomberg", "Meta", "Goldman Sachs"], "recommended_tools": "LeetCode / Python"},
                "when": {"recommended_time": "Morning (09:00 AM – 09:30 AM) — Algorithmic rigor", "duration_minutes": 30, "sprint_phase": "Day 2 of 14: Two Pointers & Space Optimization"},
                "proof_criteria": {"deliverable": "Accepted LeetCode submission passing all 322 test cases with O(1) space.", "verification_method": "Vireoniq Coding Studio"}
            },
            {
                "task_id": "de_task_alt_2",
                "title": "Design Lakehouse Bronze-Silver-Gold Medallion Partitioning with Delta Lake / Iceberg",
                "task_type": "SYSTEM_DESIGN",
                "estimated_minutes": 25,
                "projected_delta": "+1.3",
                "status": "PENDING",
                "difficulty": "Senior • Modern Lakehouse Architecture",
                "why": "Industry standard at Databricks, Snowflake, and Uber for petabyte-scale analytics and ACID reliability.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–7: Medallion Layering", "detail": "Bronze (Raw append-only landing) -> Silver (Cleaned, deduplicated, enriched) -> Gold (Aggregated business data marts)."},
                        {"phase": "Minute 7–16: Partitioning & Z-Ordering", "detail": "Partition by date (year/month/day), apply Z-order clustering on high-cardinality lookup dimensions (userId, deviceId)."},
                        {"phase": "Minute 16–25: Compaction & Vacuuming", "detail": "Design automated compaction job resolving small-file problems (bin-packing) and setting VACUUM retention periods."}
                    ],
                    "optimal_approach": "Delta Lake Medallion Architecture with auto-compact, Z-order clustering, and strict retention SLAs.",
                    "code_blueprint": "from delta.tables import DeltaTable\n# Silver Layer Upsert (Merge Schema & Deduplicate)\ndeltaTable = DeltaTable.forPath(spark, 's3://lakehouse/silver/events')\ndeltaTable.alias('target').merge(\n    source_df.alias('source'),\n    'target.event_id = source.event_id'\n).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()\n\n# Optimize & Z-Order for sub-second query performance\nspark.sql('OPTIMIZE delta.`s3://lakehouse/silver/events` ZORDER BY (user_id, event_type)')",
                    "common_pitfalls": ["Over-partitioning by high cardinality keys (creating millions of 1KB files).", "Running VACUUM with zero retention during concurrent writes, corrupting active reads."]
                },
                "where": {"platform": "Delta Lake Architecture", "url": "https://delta.io/", "mnc_companies": ["Databricks", "Apple", "Uber", "Adobe", "Microsoft"], "recommended_tools": "Apache Spark / Delta Lake"},
                "when": {"recommended_time": "Afternoon (02:00 PM – 02:25 PM) — Lakehouse engineering", "duration_minutes": 25, "sprint_phase": "Day 2 of 14: Lakehouse Storage Optimization"},
                "proof_criteria": {"deliverable": "Medallion architecture diagram and PySpark merge/optimize pipeline script.", "verification_method": "Vireoniq Design Twin"}
            },
            {
                "task_id": "de_task_alt_3",
                "title": "Draft STAR Story on Slashing BigQuery / Snowflake Compute Bill by 60% via Clustering",
                "task_type": "BEHAVIORAL_STAR",
                "estimated_minutes": 15,
                "projected_delta": "+0.7",
                "status": "COMPLETED",
                "difficulty": "Essential • FinOps & Cost Leadership",
                "why": "Demonstrates business-minded cost optimization, partition pruning, and cluster clustering.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–4: Situation", "detail": "Warehouse costs climbed to $45K/mo due to full-table scans across 20TB daily customer event tables."},
                        {"phase": "Minute 4–8: Task", "detail": "Reduce warehouse spend by >40% without degrading Tableau dashboard response times."},
                        {"phase": "Minute 8–12: Action", "detail": "Analyzed query history logs, partitioned tables by date, added clustering on org_id, and converted scheduled ad-hoc queries into incremental materialized views."},
                        {"phase": "Minute 12–15: Result", "detail": "Reduced scanned bytes by 84%; monthly warehouse bill dropped from $45K to $18K (saving $324K annually)."}
                    ],
                    "optimal_approach": "Systematic query log profiling -> Partitioning & Clustering -> Materialized Views -> Measured Dollar Savings.",
                    "code_blueprint": "Situation: Snowflake warehouse compute costs surged to $45,000/month as analyst queries executed unindexed 50TB full-table scans.\nTask: Audit query patterns, eliminate full-table scans, and slash cloud data warehouse spend by at least 40%.\nAction: Restructured core fact tables with date partitioning and org_id clustering keys; replaced hourly batch rebuilds with incremental dynamic tables.\nResult: Cut scanned data volume by 84%, reduced dashboard load time by 3.2x, and reduced annual spend by $324,000.",
                    "common_pitfalls": ["Speaking vaguely about cost without specific dollar amounts or scanned gigabyte metrics.", "Not explaining the technical mechanism behind the savings (pruning, clustering)."]
                },
                "where": {"platform": "Vireoniq Interview Twin Studio", "url": "/app/interview-simulator", "mnc_companies": ["Snowflake", "Databricks", "Amazon", "Meta", "Google"], "recommended_tools": "Vireoniq Voice Studio"},
                "when": {"recommended_time": "Evening (05:00 PM – 05:15 PM) — Leadership rehearsal", "duration_minutes": 15, "sprint_phase": "Day 2 of 14: FinOps & Storage Strategy"},
                "proof_criteria": {"deliverable": "Structured STAR writeup with audited cost reduction percentages.", "verification_method": "Automated AI rubric"}
            }
        ]
    },

    # ─── 5. DEVOPS / SRE ────────────────────────────────────────────────────
    "DevOps / SRE": {
        "active_plan_title": "14-Day DevOps / SRE Accelerated Readiness Sprints",
        "rationale": "Eliminating bottlenecks in Kubernetes pod autoscaling, chaos resilience, zero-downtime Canary rollouts & SLO alerting.",
        "tasks": [
            {
                "task_id": "devops_task_1",
                "title": "Solve LeetCode #76: Minimum Window Substring (Two-Pointer Frequency Vector)",
                "task_type": "CODING_DRILL",
                "estimated_minutes": 30,
                "projected_delta": "+1.4",
                "status": "PENDING",
                "difficulty": "Hard • Algorithmic Core",
                "why": "Evaluates sliding window expansion and contraction with character frequency map.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–7: Sliding Window Boundaries", "detail": "Maintain target map of required characters. Expand right pointer until window contains all required chars."},
                        {"phase": "Minute 7–20: Contract Left Pointer", "detail": "Once valid, shrink left pointer to find minimum window size, updating best result when valid."},
                        {"phase": "Minute 20–30: O(N) Invariant", "detail": "Both left and right traverse the string at most once. Time complexity is strictly O(N)."}
                    ],
                    "optimal_approach": "Two Pointers sliding window with matched character counter. O(N) Time, O(Alphabet) Space.",
                    "code_blueprint": "from collections import Counter\ndef minWindow(s: str, t: str) -> str:\n    if not t or not s: return ''\n    need = Counter(t)\n    missing = len(t)\n    start, end = 0, 0\n    i = 0\n    for j, char in enumerate(s, 1):\n        if need[char] > 0: missing -= 1\n        need[char] -= 1\n        if missing == 0:\n            while i < j and need[s[i]] < 0:\n                need[s[i]] += 1\n                i += 1\n            if not end or j - i <= end - start:\n                start, end = i, j\n            need[s[i]] += 1\n            missing += 1\n            i += 1\n    return s[start:end]",
                    "common_pitfalls": ["Comparing entire dictionary at each step instead of maintaining integer match count.", "Failing when s contains duplicate characters."]
                },
                "where": {"platform": "LeetCode #76", "url": "https://leetcode.com/problems/minimum-window-substring/", "mnc_companies": ["Google", "Meta", "Amazon", "Apple", "Uber"], "recommended_tools": "LeetCode / Python"},
                "when": {"recommended_time": "Morning (09:00 AM – 09:30 AM) — Core algorithmic sprint", "duration_minutes": 30, "sprint_phase": "Day 1 of 14: Algorithmic Efficiency"},
                "proof_criteria": {"deliverable": "Accepted LeetCode submission passing all test cases in O(N) time.", "verification_method": "Vireoniq Coding Studio"}
            },
            {
                "task_id": "devops_task_2",
                "title": "Architect Kubernetes Multi-Region Disaster Recovery with GitOps (ArgoCD & Vault)",
                "task_type": "SYSTEM_DESIGN",
                "estimated_minutes": 25,
                "projected_delta": "+1.3",
                "status": "PENDING",
                "difficulty": "Advanced • Cloud Infrastructure",
                "why": "Demonstrates multi-cluster synchronization, secret rotation, and active-passive failover.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–7: GitOps Declarative Ingress", "detail": "Use ArgoCD ApplicationSets to synchronize manifest definitions across Primary (us-east-1) and Secondary (eu-west-1)."},
                        {"phase": "Minute 7–16: Secret Management & Vault", "detail": "External Secrets Operator syncing dynamic database credentials from HashiCorp Vault without hardcoded secrets in Git."},
                        {"phase": "Minute 16–25: RTO/RPO Failover Testing", "detail": "Configure Route 53 DNS failover healthchecks with automated DNS record propagation within 60 seconds."}
                    ],
                    "optimal_approach": "ArgoCD ApplicationSets + External Secrets Operator + Route 53 latency DNS failover.",
                    "code_blueprint": "apiVersion: argoproj.io/v1alpha1\nkind: ApplicationSet\nmetadata:\n  name: production-workloads\nspec:\n  generators:\n  - list:\n      elements:\n      - cluster: us-east-1\n        url: https://k8s-useast1.vireoniq.internal\n      - cluster: eu-west-1\n        url: https://k8s-euwest1.vireoniq.internal\n  template:\n    metadata:\n      name: '{{cluster}}-workload'\n    spec:\n      destination:\n        server: '{{url}}'\n        namespace: production\n      source:\n        repoURL: https://github.com/vireoniq/k8s-manifests\n        path: apps/production",
                    "common_pitfalls": ["Storing plaintext secrets in Git repositories instead of using sealed secrets or Vault.", "Not verifying stateful volume backup replication (EBS snapshots/CSI)."]
                },
                "where": {"platform": "Kubernetes Architecture Sandbox", "url": "https://argo-cd.readthedocs.io/", "mnc_companies": ["Netflix", "Datadog", "AWS", "Google Cloud", "Atlassian"], "recommended_tools": "kubectl / Helm / ArgoCD"},
                "when": {"recommended_time": "Afternoon (02:00 PM – 02:25 PM) — GitOps infrastructure design", "duration_minutes": 25, "sprint_phase": "Day 1 of 14: Disaster Recovery & High Availability"},
                "proof_criteria": {"deliverable": "ArgoCD ApplicationSet manifest and architecture topology diagram.", "verification_method": "Vireoniq Design Twin"}
            },
            {
                "task_id": "devops_task_3",
                "title": "Draft STAR Story on Leading Root Cause Analysis (RCA) After Major Cloud Outage",
                "task_type": "BEHAVIORAL_STAR",
                "estimated_minutes": 15,
                "projected_delta": "+0.8",
                "status": "COMPLETED",
                "difficulty": "Critical • Incident Commander Loop",
                "why": "Validates psychological safety, blameless post-mortem ownership, and preventative architectural controls.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–3: Situation", "detail": "Major AWS us-east-1 network partition triggered cascading pod evictions across 400 microservices."},
                        {"phase": "Minute 3–7: Task", "detail": "Acted as Incident Commander: restore service, manage stakeholder communication, and chair blameless RCA."},
                        {"phase": "Minute 7–11: Action", "detail": "Promoted cross-region standby cluster, re-routed traffic, and instituted pod disruption budgets (PDBs) and anti-affinity rules."},
                        {"phase": "Minute 11–15: Result", "detail": "Service restored in 18 minutes; zero recurrence in following 12 months."}
                    ],
                    "optimal_approach": "Incident Command -> Rapid Containment -> Blameless RCA -> Structural Anti-Fragility.",
                    "code_blueprint": "Situation: A regional cloud network partition triggered split-brain condition across our Kubernetes cluster, affecting 200K active users.\nTask: Assume role of Incident Commander, coordinate SREs, contain outage, and chair the subsequent post-mortem.\nAction: Executed traffic cutover to disaster recovery region, stabilized core services within 18 minutes, and added automated PodDisruptionBudgets.\nResult: Met 99.95% annual availability target; our RCA template was adopted across all 12 platform engineering teams.",
                    "common_pitfalls": ["Assigning individual blame rather than identifying systemic lack of guardrails.", "Not specifying quantifiable MTTA / MTTR improvements."]
                },
                "where": {"platform": "Vireoniq Leadership Simulator", "url": "/app/interview-simulator", "mnc_companies": ["Google", "Amazon", "Netflix", "Datadog", "Cloudflare"], "recommended_tools": "Vireoniq Voice Simulator"},
                "when": {"recommended_time": "Evening (05:00 PM – 05:15 PM) — SRE incident rehearsal", "duration_minutes": 15, "sprint_phase": "Day 1 of 14: Incident Management & SRE Culture"},
                "proof_criteria": {"deliverable": "Structured blameless post-mortem document with 5-whys root cause analysis.", "verification_method": "Automated AI rubric"}
            }
        ],
        "tasks_alt": [
            {
                "task_id": "devops_task_alt_1",
                "title": "Solve LeetCode #394: Decode String (Stack-Based Parser)",
                "task_type": "CODING_DRILL",
                "estimated_minutes": 25,
                "projected_delta": "+1.1",
                "status": "PENDING",
                "difficulty": "Medium • Infrastructure Config Parsing",
                "why": "Tests dual-stack operand tracking and recursive string unfolding under O(N) memory limits.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–5: Dual Stack Strategy", "detail": "Maintain count_stack and string_stack to handle arbitrarily nested patterns like 3[a2[c]]."},
                        {"phase": "Minute 5–15: Token Handling", "detail": "When '[' encountered, push current_num and current_str. When ']' encountered, pop and repeat string."},
                        {"phase": "Minute 15–25: Edge Verification", "detail": "Handle multi-digit multipliers ('100[leetcode]') and adjacent blocks ('2[a]3[b]'). Time: O(Output_Length)."}
                    ],
                    "optimal_approach": "Two-stack parser maintaining state across nested bracket scopes.",
                    "code_blueprint": "def decodeString(s: str) -> str:\n    stack = []\n    cur_num = 0\n    cur_str = ''\n    for c in s:\n        if c.isdigit():\n            cur_num = cur_num * 10 + int(c)\n        elif c == '[':\n            stack.append((cur_str, cur_num))\n            cur_str, cur_num = '', 0\n        elif c == ']':\n            prev_str, num = stack.pop()\n            cur_str = prev_str + num * cur_str\n        else:\n            cur_str += c\n    return cur_str",
                    "common_pitfalls": ["Failing to parse multi-digit numbers (e.g. '12[ab]').", "Using recursive string concatenation which creates quadratic memory overhead."]
                },
                "where": {"platform": "LeetCode #394", "url": "https://leetcode.com/problems/decode-string/", "mnc_companies": ["Google", "Bloomberg", "Cisco", "Amazon", "Oracle"], "recommended_tools": "LeetCode / Python"},
                "when": {"recommended_time": "Morning (09:00 AM – 09:25 AM) — Parsing algorithms", "duration_minutes": 25, "sprint_phase": "Day 2 of 14: Stack & Grammar Parsing"},
                "proof_criteria": {"deliverable": "Accepted LeetCode submission passing 100% test cases.", "verification_method": "Vireoniq Coding Studio"}
            },
            {
                "task_id": "devops_task_alt_2",
                "title": "Design Zero-Downtime Canary Rollout with Istio Service Mesh & Automated Rollback",
                "task_type": "SYSTEM_DESIGN",
                "estimated_minutes": 25,
                "projected_delta": "+1.3",
                "status": "PENDING",
                "difficulty": "Senior • Traffic Routing & SRE",
                "why": "Implements progressive traffic shifting (95/5 -> 50/50), Prometheus error rate thresholds, and zero-touch rollback.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–7: VirtualService Weighting", "detail": "Define Istio VirtualService splitting incoming production traffic between stable (v1) and canary (v2)."},
                        {"phase": "Minute 7–16: Prometheus Metric Analysis", "detail": "Flagger operator polling Prometheus for HTTP 5xx error rate (< 0.5%) and p99 latency (< 250ms)."},
                        {"phase": "Minute 16–25: Automated Promotion & Rollback", "detail": "If metrics breach threshold for 2 consecutive checks, immediately revert VirtualService weights to 100% stable."}
                    ],
                    "optimal_approach": "Istio VirtualService + Flagger automated canary analysis based on Prometheus metrics.",
                    "code_blueprint": "apiVersion: flagger.app/v1beta1\nkind: Canary\nmetadata:\n  name: payment-service\nspec:\n  targetRef:\n    apiVersion: apps/v1\n    kind: Deployment\n    name: payment-service\n  service:\n    port: 8080\n  analysis:\n    interval: 1m\n    threshold: 3\n    maxWeight: 50\n    stepWeight: 10\n    metrics:\n    - name: request-success-rate\n      thresholdRange:\n        min: 99.5\n      interval: 1m",
                    "common_pitfalls": ["Relying on manual human promotion instead of metric-driven threshold gates.", "Not testing database schema backwards compatibility between v1 and v2 deployments."]
                },
                "where": {"platform": "Istio Service Mesh", "url": "https://istio.io/", "mnc_companies": ["Netflix", "Uber", "Spotify", "Amazon", "Salesforce"], "recommended_tools": "Istio / Prometheus / Flagger"},
                "when": {"recommended_time": "Afternoon (02:00 PM – 02:25 PM) — Canary deployment engineering", "duration_minutes": 25, "sprint_phase": "Day 2 of 14: Progressive Traffic Delivery"},
                "proof_criteria": {"deliverable": "Istio VirtualService and Flagger Canary manifest with rollback criteria.", "verification_method": "Vireoniq Design Twin"}
            },
            {
                "task_id": "devops_task_alt_3",
                "title": "Draft STAR Story on Automating Infrastructure Drift Detection Across 500+ Cloud Accounts",
                "task_type": "BEHAVIORAL_STAR",
                "estimated_minutes": 15,
                "projected_delta": "+0.7",
                "status": "COMPLETED",
                "difficulty": "Essential • Automation & Scale",
                "why": "Showcases Terraform Cloud drift detection, automated PR remediation, and compliance governance.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–4: Situation", "detail": "Manual console changes in AWS by engineers created 140+ unmanaged security groups, failing SOC2 compliance."},
                        {"phase": "Minute 4–8: Task", "detail": "Automate hourly drift detection across 500 AWS accounts and remediate non-compliant infrastructure automatically."},
                        {"phase": "Minute 8–12: Action", "detail": "Built serverless event bus with AWS Config and Terraform Cloud API; alerted engineering owners on Slack with 1-click reconcile PRs."},
                        {"phase": "Minute 12–15: Result", "detail": "Achieved 100% SOC2 compliance audit pass; eliminated manual configuration drift across enterprise."}
                    ],
                    "optimal_approach": "Automated detection -> Self-healing workflow -> Friction-free developer experience.",
                    "code_blueprint": "Situation: Over 140 undocumented security group changes were made via AWS console, threatening our upcoming SOC2 Type II audit.\nTask: Implement continuous automated drift detection and remediation across 500+ production cloud accounts.\nAction: Built an EventBridge-driven scanner that invokes Terraform Cloud to generate automated rollback pull requests when manual edits are detected.\nResult: Slashed unmanaged cloud drift to zero within 3 weeks, enabling our security team to pass SOC2 with zero non-conformances.",
                    "common_pitfalls": ["Blaming developers for using the console instead of building better guardrails.", "Not explaining the business value of passing the SOC2 audit."]
                },
                "where": {"platform": "Vireoniq Interview Twin Studio", "url": "/app/interview-simulator", "mnc_companies": ["HashiCorp", "AWS", "Google Cloud", "Atlassian", "Twilio"], "recommended_tools": "Vireoniq Voice Studio"},
                "when": {"recommended_time": "Evening (05:00 PM – 05:15 PM) — Leadership rehearsal", "duration_minutes": 15, "sprint_phase": "Day 2 of 14: Cloud Security & Governance"},
                "proof_criteria": {"deliverable": "Structured STAR reflection detailing automated governance workflows.", "verification_method": "Automated AI rubric"}
            }
        ]
    },

    # ─── 6. CLOUD ARCHITECT ─────────────────────────────────────────────────
    "Cloud Architect": {
        "active_plan_title": "14-Day Cloud Architect Accelerated Readiness Sprints",
        "rationale": "Eliminating bottlenecks in multi-region active-active VPC peering, transit gateways & zero-trust IAM least-privilege architecture.",
        "tasks": [
            {
                "task_id": "cloud_task_1",
                "title": "Solve LeetCode #207: Course Schedule (Graph Cycle & Kahn's Topological Sort)",
                "task_type": "CODING_DRILL",
                "estimated_minutes": 25,
                "projected_delta": "+1.2",
                "status": "PENDING",
                "difficulty": "Medium • Dependency DAG Resolution",
                "why": "Validates in-degree graph modeling and dependency graph cycle detection critical for cloud provisioning DAGs.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–5: Graph Modeling", "detail": "Represent courses as nodes and prerequisites as directed edges. Cycle implies impossible schedule."},
                        {"phase": "Minute 5–15: Kahn's Algorithm (BFS)", "detail": "Compute in-degrees of all nodes. Push all in-degree 0 nodes to queue. Decrement child in-degrees when popped."},
                        {"phase": "Minute 15–25: Cycle Validation", "detail": "If processed node count equals total courses, valid DAG exists. Otherwise cycle detected. Time: O(V + E)."}
                    ],
                    "optimal_approach": "Kahn's algorithm using in-degree array and BFS queue. O(V + E) Time, O(V + E) Space.",
                    "code_blueprint": "from collections import deque, defaultdict\ndef canFinish(numCourses: int, prerequisites: list[list[int]]) -> bool:\n    adj = defaultdict(list)\n    in_degree = [0] * numCourses\n    for dest, src in prerequisites:\n        adj[src].append(dest)\n        in_degree[dest] += 1\n    q = deque([i for i in range(numCourses) if in_degree[i] == 0])\n    visited = 0\n    while q:\n        curr = q.popleft()\n        visited += 1\n        for neighbor in adj[curr]:\n            in_degree[neighbor] -= 1\n            if in_degree[neighbor] == 0:\n                q.append(neighbor)\n    return visited == numCourses",
                    "common_pitfalls": ["Reversing edge directions (prerequisite should point to target course).", "Using DFS without 3-state coloring (visiting/visited), leading to infinite loops on cycles."]
                },
                "where": {"platform": "LeetCode #207", "url": "https://leetcode.com/problems/course-schedule/", "mnc_companies": ["Amazon", "Google", "Microsoft", "Uber", "Palantir"], "recommended_tools": "LeetCode / Python"},
                "when": {"recommended_time": "Morning (09:00 AM – 09:25 AM) — Graph DAG sprint", "duration_minutes": 25, "sprint_phase": "Day 1 of 14: Directed Graph Modeling"},
                "proof_criteria": {"deliverable": "Accepted LeetCode submission passing all test cases.", "verification_method": "MNC Coding Studio"}
            },
            {
                "task_id": "cloud_task_2",
                "title": "Architect Multi-Tenant Multi-Region Active-Active Cloud Mesh on AWS/GCP",
                "task_type": "SYSTEM_DESIGN",
                "estimated_minutes": 25,
                "projected_delta": "+1.5",
                "status": "PENDING",
                "difficulty": "Principal • Global Infrastructure",
                "why": "Architects low-latency cross-region replication (Route 53 latency routing, DynamoDB global tables, CDN edge compute).",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–7: Global Ingress Routing", "detail": "AWS Route 53 Latency-Based Routing with CloudFront CDN edge caching and AWS Global Accelerator."},
                        {"phase": "Minute 7–16: Data Layer Consistency", "detail": "DynamoDB Global Tables for multi-region writes with conflict resolution based on last-writer-wins."},
                        {"phase": "Minute 16–25: Inter-Region Networking", "detail": "AWS Transit Gateway with inter-region peering over dedicated AWS private backbone, bypassing public internet."}
                    ],
                    "optimal_approach": "Route 53 Geolocation/Latency + DynamoDB Global Tables + Transit Gateway private mesh.",
                    "code_blueprint": "# Terraform AWS Transit Gateway Peering\nresource \"aws_ec2_transit_gateway_peering_attachment\" \"us_to_eu\" {\n  transit_gateway_id      = aws_ec2_transit_gateway.useast1.id\n  peer_transit_gateway_id = aws_ec2_transit_gateway.euwest1.id\n  peer_region             = \"eu-west-1\"\n  tags = { Name = \"tgw-peering-useast1-euwest1\" }\n}",
                    "common_pitfalls": ["Overlooking cross-region data transfer egress costs.", "Assuming synchronous ACID transactions are viable across 80ms transatlantic latency."]
                },
                "where": {"platform": "AWS / Cloud Architecture Sandbox", "url": "https://aws.amazon.com/architecture/", "mnc_companies": ["Amazon Web Services", "Google Cloud", "Microsoft Azure", "Salesforce", "Snowflake"], "recommended_tools": "Terraform / Draw.io / AWS Architecture Center"},
                "when": {"recommended_time": "Afternoon (02:00 PM – 02:25 PM) — Multi-region system design", "duration_minutes": 25, "sprint_phase": "Day 1 of 14: High Availability Architecture"},
                "proof_criteria": {"deliverable": "Multi-region architecture diagram with Route 53, Transit Gateway, and global data sync topology.", "verification_method": "Vireoniq Design Twin"}
            },
            {
                "task_id": "cloud_task_3",
                "title": "Draft STAR Story on Driving Cloud Migration from On-Premises with 99.999% Availability",
                "task_type": "BEHAVIORAL_STAR",
                "estimated_minutes": 15,
                "projected_delta": "+0.8",
                "status": "COMPLETED",
                "difficulty": "Executive • Transformation Loop",
                "why": "Communicates executive stakeholder alignment, risk mitigation, and legacy decoupling without operational disruption.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–3: Situation", "detail": "Aging on-prem data center contracts expiring; needed to migrate 80 core banking services to AWS in 6 months."},
                        {"phase": "Minute 3–7: Task", "detail": "Lead cloud migration roadmap, convince cautious executive risk committees, and guarantee zero downtime."},
                        {"phase": "Minute 7–11: Action", "detail": "Implemented strangler fig migration pattern; established Direct Connect hybrid link; migrated lowest-risk read workloads first."},
                        {"phase": "Minute 11–15: Result", "detail": "Completed migration 3 weeks early with 100% uptime; saved $2.1M in annual hardware renewal expenses."}
                    ],
                    "optimal_approach": "Strangler Fig Pattern + Executive alignment + Risk-tiered migration phasing.",
                    "code_blueprint": "Situation: Expiring data center leases required migrating 80 enterprise services to AWS within 6 months with zero downtime.\nTask: Serve as Lead Cloud Architect, establish the multi-phase migration architecture, and guide 5 engineering teams through cutover.\nAction: Deployed AWS Direct Connect with Strangler Fig routing; piloted non-critical reporting before migrating primary transactional databases.\nResult: Cutover completed 3 weeks ahead of schedule with 99.999% availability, reducing infrastructure TCO by 34% ($2.1M/year).",
                    "common_pitfalls": ["Advocating for a 'big bang' cutover instead of phased strangler fig decoupling.", "Failing to discuss risk management and rollback readiness."]
                },
                "where": {"platform": "Vireoniq Leadership Simulator", "url": "/app/interview-simulator", "mnc_companies": ["Amazon", "Microsoft", "Goldman Sachs", "JPMorgan", "Oracle"], "recommended_tools": "Vireoniq Voice Simulator"},
                "when": {"recommended_time": "Evening (05:00 PM – 05:15 PM) — Executive communication", "duration_minutes": 15, "sprint_phase": "Day 1 of 14: Cloud Governance & Transformation"},
                "proof_criteria": {"deliverable": "Executive STAR narrative with audited downtime and TCO metrics.", "verification_method": "Automated AI rubric"}
            }
        ],
        "tasks_alt": [
            {
                "task_id": "cloud_task_alt_1",
                "title": "Solve LeetCode #269: Alien Dictionary (Topological Sort with Strict Invariants)",
                "task_type": "CODING_DRILL",
                "estimated_minutes": 30,
                "projected_delta": "+1.4",
                "status": "PENDING",
                "difficulty": "Hard • Graph Modeling",
                "why": "Tests directed acyclic graph cycle validation and lexicographic order reconstruction.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–7: Edge Extraction", "detail": "Compare adjacent words pairwise. The first differing character defines a directed edge (char1 -> char2)."},
                        {"phase": "Minute 7–18: Prefix Edge Case Check", "detail": "If word2 is a proper prefix of word1 (e.g. 'abc' before 'ab'), the dictionary is invalid, return '' immediately."},
                        {"phase": "Minute 18–30: Kahn's BFS Sort", "detail": "Apply Kahn's algorithm on extracted edges. If all distinct characters sorted, return string, else return ''."}
                    ],
                    "optimal_approach": "Pairwise prefix check + Kahn's BFS topological ordering.",
                    "code_blueprint": "from collections import defaultdict, deque\ndef alienOrder(words: list[str]) -> str:\n    adj = {c: set() for w in words for c in w}\n    in_degree = {c: 0 for c in adj}\n    for w1, w2 in zip(words, words[1:]):\n        if len(w1) > len(w2) and w1.startswith(w2): return ''\n        for c1, c2 in zip(w1, w2):\n            if c1 != c2:\n                if c2 not in adj[c1]:\n                    adj[c1].add(c2)\n                    in_degree[c2] += 1\n                break\n    q = deque([c for c in in_degree if in_degree[c] == 0])\n    res = []\n    while q:\n        c = q.popleft()\n        res.append(c)\n        for nxt in adj[c]:\n            in_degree[nxt] -= 1\n            if in_degree[nxt] == 0: q.append(nxt)\n    return ''.join(res) if len(res) == len(in_degree) else ''",
                    "common_pitfalls": ["Missing the prefix edge case where longer word appears before its prefix.", "Failing to track isolated characters that never appear in difference pairs."]
                },
                "where": {"platform": "LeetCode #269", "url": "https://leetcode.com/problems/alien-dictionary/", "mnc_companies": ["Google", "Amazon", "Facebook", "Microsoft", "Airbnb"], "recommended_tools": "LeetCode / Python"},
                "when": {"recommended_time": "Morning (09:00 AM – 09:30 AM) — Deep graph algorithms", "duration_minutes": 30, "sprint_phase": "Day 2 of 14: Advanced Topological Sorting"},
                "proof_criteria": {"deliverable": "Accepted LeetCode solution with 100% test passing rate.", "verification_method": "Vireoniq Coding Studio"}
            },
            {
                "task_id": "cloud_task_alt_2",
                "title": "Design Zero-Trust Enterprise IAM Strategy with AWS Organizations, SSO & Least Privilege",
                "task_type": "SYSTEM_DESIGN",
                "estimated_minutes": 25,
                "projected_delta": "+1.2",
                "status": "PENDING",
                "difficulty": "Enterprise • Cloud Security",
                "why": "Implements Service Control Policies (SCPs), short-lived STS tokens, and boundary policy enforcement.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–7: Organizational Hierarchy", "detail": "Root -> Core/Security/Workloads OUs. Deny all root user access and require MFA deletion via SCPs."},
                        {"phase": "Minute 7–16: Temporary STS Credentials", "detail": "Eliminate long-lived IAM user access keys. Enforce AWS IAM Identity Center (SSO) with Okta SAML 2.0 integration."},
                        {"phase": "Minute 16–25: Permission Boundaries", "detail": "Apply IAM Permissions Boundaries preventing developer roles from elevating privileges beyond their boundary."}
                    ],
                    "optimal_approach": "Multi-tier SCPs + IAM Permission Boundaries + OIDC Short-lived STS tokens.",
                    "code_blueprint": "{\n  \"Version\": \"2012-10-17\",\n  \"Statement\": [\n    {\n      \"Sid\": \"DenyAllOutsideApprovedRegions\",\n      \"Effect\": \"Deny\",\n      \"NotAction\": [\n        \"iam:*\", \"organizations:*\", \"route53:*\", \"cloudfront:*\"\n      ],\n      \"Resource\": \"*\",\n      \"Condition\": {\n        \"StringNotEquals\": {\n          \"aws:RequestedRegion\": [\"us-east-1\", \"eu-west-1\"]\n        }\n      }\n    }\n  ]\n}",
                    "common_pitfalls": ["Over-privileged admin roles with AdministratorAccess.", "Not excluding global services (IAM, Route 53) when applying regional lockdown SCPs."]
                },
                "where": {"platform": "AWS Security Best Practices", "url": "https://aws.amazon.com/security/", "mnc_companies": ["Amazon", "Microsoft", "Palantir", "Goldman Sachs", "Stripe"], "recommended_tools": "AWS Organizations / IAM"},
                "when": {"recommended_time": "Afternoon (02:00 PM – 02:25 PM) — IAM security architecture", "duration_minutes": 25, "sprint_phase": "Day 2 of 14: Cloud Security & Governance"},
                "proof_criteria": {"deliverable": "Complete SCP and Permission Boundary JSON with regional restriction policy.", "verification_method": "Vireoniq Design Twin"}
            },
            {
                "task_id": "cloud_task_alt_3",
                "title": "Draft STAR Story on Convincing C-Suite to Adopt Event-Driven Serverless vs K8s Overhead",
                "task_type": "BEHAVIORAL_STAR",
                "estimated_minutes": 15,
                "projected_delta": "+0.7",
                "status": "COMPLETED",
                "difficulty": "Leadership • Architecture Tradeoff",
                "why": "Demonstrates total cost of ownership (TCO) analysis, maintenance overhead reduction, and rapid time-to-market.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–4: Situation", "detail": "Startup team wanted to deploy 6-node Kubernetes cluster for small asynchronous background event service."},
                        {"phase": "Minute 4–8: Task", "detail": "Advocate for AWS Lambda + EventBridge architecture to avoid $120K/yr DevOps maintenance overhead."},
                        {"phase": "Minute 8–12: Action", "detail": "Presented 3-year TCO model comparing operational burden, patching costs, and scaling elasticity."},
                        {"phase": "Minute 12–15: Result", "detail": "Leadership approved Serverless path; shipped 2 months faster with 92% lower infrastructure bill."}
                    ],
                    "optimal_approach": "Pragmatic TCO modeling over architectural hype.",
                    "code_blueprint": "Situation: Engineering leadership proposed a full multi-tenant Kubernetes cluster for a greenfield event processing application.\nTask: Present objective TCO and operational maintenance tradeoffs to CTO and Product VP.\nAction: Built a comparative model demonstrating AWS EventBridge + Lambda saved $120,000/yr in dedicated SRE maintenance with instant scaling.\nResult: Executive team adopted Serverless approach, launching the product 8 weeks ahead of deadline with zero dedicated infrastructure overhead.",
                    "common_pitfalls": ["Criticizing Kubernetes in general instead of focusing on context-specific fit for team size.", "Ignoring developer familiarity and vendor lock-in concerns."]
                },
                "where": {"platform": "Vireoniq Interview Twin Studio", "url": "/app/interview-simulator", "mnc_companies": ["Amazon", "Capital One", "Datadog", "Stripe", "Netflix"], "recommended_tools": "Vireoniq Voice Studio"},
                "when": {"recommended_time": "Evening (05:00 PM – 05:15 PM) — Leadership rehearsal", "duration_minutes": 15, "sprint_phase": "Day 2 of 14: Cloud Economics & Advocacy"},
                "proof_criteria": {"deliverable": "STAR story writeup with comparative TCO calculations.", "verification_method": "Automated AI rubric"}
            }
        ]
    },

    # ─── 7. MOBILE ENGINEER ─────────────────────────────────────────────────
    "Mobile Engineer": {
        "active_plan_title": "14-Day Mobile Engineer Accelerated Readiness Sprints",
        "rationale": "Eliminating bottlenecks in 60 FPS frame render threads, offline SQLite reconciliation, biometrics & memory leak profiles.",
        "tasks": [
            {
                "task_id": "mobile_task_1",
                "title": "Solve LeetCode #206: Reverse Linked List & Deep Clone of Graph (Pointers)",
                "task_type": "CODING_DRILL",
                "estimated_minutes": 25,
                "projected_delta": "+1.1",
                "status": "PENDING",
                "difficulty": "Medium • Memory Lifecycle & Pointers",
                "why": "Ensures deep understanding of in-memory object references and cyclic graph traversal.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–5: Pointer Mutation Invariant", "detail": "Maintain prev, curr, and next_temp pointers. Avoid memory leaks or cyclic references."},
                        {"phase": "Minute 5–15: In-Place Reversal", "detail": "Save curr.next, point curr.next = prev, advance prev = curr, advance curr = next_temp."},
                        {"phase": "Minute 15–25: Edge Case Verification", "detail": "Test empty list, single node, two nodes. Confirm O(N) time and O(1) space complexity."}
                    ],
                    "optimal_approach": "Iterative three-pointer in-place reversal. O(N) Time, O(1) Space.",
                    "code_blueprint": "class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef reverseList(head: ListNode | None) -> ListNode | None:\n    prev = None\n    curr = head\n    while curr:\n        next_temp = curr.next\n        curr.next = prev\n        prev = curr\n        curr = next_temp\n    return prev",
                    "common_pitfalls": ["Losing reference to curr.next before updating pointer (causes broken list).", "Using recursion which risks stack overflow on lists with 10,000+ elements."]
                },
                "where": {"platform": "LeetCode #206", "url": "https://leetcode.com/problems/reverse-linked-list/", "mnc_companies": ["Apple", "Google", "Meta", "Uber", "Spotify"], "recommended_tools": "LeetCode / Swift / Kotlin / Python"},
                "when": {"recommended_time": "Morning (09:00 AM – 09:25 AM) — Pointer mechanics sprint", "duration_minutes": 25, "sprint_phase": "Day 1 of 14: In-Memory Pointer Manipulation"},
                "proof_criteria": {"deliverable": "Accepted LeetCode submission passing all test cases in O(1) space.", "verification_method": "Vireoniq Coding Studio"}
            },
            {
                "task_id": "mobile_task_2",
                "title": "Architect Offline-First Mobile Storage with SQLite/Room, Background Sync & WorkManager",
                "task_type": "SYSTEM_DESIGN",
                "estimated_minutes": 25,
                "projected_delta": "+1.3",
                "status": "PENDING",
                "difficulty": "Senior • Mobile Architecture",
                "why": "Designs resilient offline mutation queues, optimistic UI sync, and backpressure retry handling.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–7: Local Database Entity Design", "detail": "SQLite/Room/CoreData schema with sync_status ('SYNCED', 'PENDING_UPLOAD', 'CONFLICT') and client timestamp."},
                        {"phase": "Minute 7–16: Background Queue & WorkManager", "detail": "Schedule WorkManager/BGAppRefreshTask with network constraints (CONNECTED, UNMETERED)."},
                        {"phase": "Minute 16–25: Exponential Backoff & Conflict Resolution", "detail": "Implement exponential backoff with jitter on network failure; resolve server conflicts via client revision IDs."}
                    ],
                    "optimal_approach": "Repository Pattern with Room/CoreData Single Source of Truth + WorkManager background sync.",
                    "code_blueprint": "// Kotlin Room + Coroutines Offline Repository\nclass OfflineFirstRepository(\n    private val localDao: ItemDao,\n    private val api: RemoteApi\n) {\n    val items: Flow<List<ItemEntity>> = localDao.getAllItems()\n\n    suspend fun createItemOptimistic(item: ItemEntity) {\n        localDao.insert(item.copy(syncStatus = SyncStatus.PENDING))\n        enqueueSyncWork()\n    }\n}",
                    "common_pitfalls": ["Updating remote server directly without updating local database first (causes UI flicker).", "Running heavy database transactions on main UI thread causing app freezes (ANRs)."]
                },
                "where": {"platform": "Mobile Architecture Sandbox", "url": "https://developer.android.com/topic/architecture/data-layer/offline-first", "mnc_companies": ["Uber", "Instagram", "WhatsApp", "Duolingo", "DoorDash"], "recommended_tools": "Android Studio / Xcode / Room / CoreData"},
                "when": {"recommended_time": "Afternoon (02:00 PM – 02:25 PM) — Offline mobile design", "duration_minutes": 25, "sprint_phase": "Day 1 of 14: Offline-First Architecture"},
                "proof_criteria": {"deliverable": "Offline repository sync sequence diagram and entity schema.", "verification_method": "Vireoniq Design Twin"}
            },
            {
                "task_id": "mobile_task_3",
                "title": "Draft STAR Story on Profiling & Eliminating 60 FPS Frame Drops on Low-End Devices",
                "task_type": "BEHAVIORAL_STAR",
                "estimated_minutes": 15,
                "projected_delta": "+0.8",
                "status": "COMPLETED",
                "difficulty": "Critical • Mobile Performance",
                "why": "Demonstrates Android Profiler / Xcode Instruments proficiency, offloading heavy calculations from main thread.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–3: Situation", "detail": "App dropped to 24 FPS during infinite feed scrolling on budget Android devices, driving negative app store reviews."},
                        {"phase": "Minute 3–7: Task", "detail": "Profile app, identify main thread bottlenecks, and guarantee stable 60 FPS across 95% of active fleet."},
                        {"phase": "Minute 7–11: Action", "detail": "Used Android Studio Systrace/Profiler; discovered bitmap decoding on main thread and overdraw in custom list item layouts; moved decoding to background coroutines and flattened view hierarchy."},
                        {"phase": "Minute 11–15: Result", "detail": "Achieved steady 60 FPS; frame drop rate fell from 18% to 1.2%; app store rating rose from 3.8 to 4.7 stars."}
                    ],
                    "optimal_approach": "Tool-driven profiling (Systrace/Instruments) -> View hierarchy flattening -> Off-main-thread image decoding.",
                    "code_blueprint": "Situation: App frame rates dropped to 24 FPS during feed scrolling on budget devices, resulting in a wave of 1-star reviews.\nTask: Diagnose rendering bottlenecks and restore silky 60 FPS scrolling across all supported device tiers.\nAction: Profiled with Android GPU Profiler; identified excessive layout overdraw and synchronous image resizing on main thread; migrated image processing to Dispatchers.Default and flattened XML hierarchy.\nResult: Frame drop rate plummeted from 18% to 1.2%, maintaining steady 60 FPS; Play Store rating climbed to 4.7 stars.",
                    "common_pitfalls": ["Guessing where the lag comes from instead of using Systrace or Instruments.", "Not mentioning the specific device specs tested on (e.g. low-end 2GB RAM devices)."]
                },
                "where": {"platform": "Vireoniq Leadership Simulator", "url": "/app/interview-simulator", "mnc_companies": ["Google", "Meta", "ByteDance", "Snap", "Spotify"], "recommended_tools": "Vireoniq Voice Simulator"},
                "when": {"recommended_time": "Evening (05:00 PM – 05:15 PM) — Performance engineering reflection", "duration_minutes": 15, "sprint_phase": "Day 1 of 14: Mobile Performance Optimization"},
                "proof_criteria": {"deliverable": "Structured STAR performance report with frame rate telemetry before/after.", "verification_method": "Automated AI rubric"}
            }
        ],
        "tasks_alt": [
            {
                "task_id": "mobile_task_alt_1",
                "title": "Solve LeetCode #142: Linked List Cycle II (Floyd's Tortoise & Hare Cycle Entry)",
                "task_type": "CODING_DRILL",
                "estimated_minutes": 25,
                "projected_delta": "+1.1",
                "status": "PENDING",
                "difficulty": "Medium • Constant Space Cycle Detection",
                "why": "Tests constant-space cycle detection and mathematical loop entry point derivation.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–5: Floyd's Algorithm Phase 1", "detail": "Advance slow by 1 step, fast by 2 steps. If fast meets slow, a cycle exists."},
                        {"phase": "Minute 5–15: Phase 2 (Find Entry Point)", "detail": "Reset slow pointer to head. Keep fast at intersection. Advance both by 1 step simultaneously. Meeting point is exact cycle entry."},
                        {"phase": "Minute 15–25: Mathematical Proof", "detail": "Distance from head to entry equals distance from intersection to entry. O(N) Time, O(1) Space."}
                    ],
                    "optimal_approach": "Two-phase Floyd Tortoise and Hare algorithm for O(1) space cycle entry determination.",
                    "code_blueprint": "def detectCycle(head: ListNode | None) -> ListNode | None:\n    slow = fast = head\n    while fast and fast.next:\n        slow = slow.next\n        fast = fast.next.next\n        if slow == fast:\n            slow = head\n            while slow != fast:\n                slow = slow.next\n                fast = fast.next\n            return slow\n    return None",
                    "common_pitfalls": ["Using a hash set to store seen nodes (takes O(N) space, violating interview memory constraints).", "Advancing fast pointer without checking fast.next."]
                },
                "where": {"platform": "LeetCode #142", "url": "https://leetcode.com/problems/linked-list-cycle-ii/", "mnc_companies": ["Apple", "Microsoft", "Amazon", "Google", "Snap"], "recommended_tools": "LeetCode / Python"},
                "when": {"recommended_time": "Morning (09:00 AM – 09:25 AM) — Cycle detection algorithms", "duration_minutes": 25, "sprint_phase": "Day 2 of 14: Pointer Geometry"},
                "proof_criteria": {"deliverable": "Accepted LeetCode submission passing all test cases.", "verification_method": "Vireoniq Coding Studio"}
            },
            {
                "task_id": "mobile_task_alt_2",
                "title": "Design Biometric Authentication & Secure Enclave Keystore Integration for FinTech App",
                "task_type": "SYSTEM_DESIGN",
                "estimated_minutes": 25,
                "projected_delta": "+1.3",
                "status": "PENDING",
                "difficulty": "Advanced • Mobile AppSec",
                "why": "Integrates Hardware Security Module (HSM), KeyStore cryptographic signature verification, and anti-tamper jailbreak detection.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–7: Hardware Security Module (HSM)", "detail": "Generate asymmetric ECC P-256 key pair inside iOS Secure Enclave / Android StrongBox Keymaster. Private key never leaves hardware."},
                        {"phase": "Minute 7–16: Biometric Prompt & Cipher Auth", "detail": "Trigger BiometricPrompt requiring UserAuthenticationValidityDurationSeconds. Sign challenge nonce returned by server."},
                        {"phase": "Minute 16–25: Anti-Tamper & Root Detection", "detail": "Check SafetyNet/Play Integrity and jailbreak hooks before authorizing cryptographic token release."}
                    ],
                    "optimal_approach": "Hardware-backed asymmetric key pair requiring biometric authentication per transaction.",
                    "code_blueprint": "// Android KeyGenParameterSpec with Biometric Requirement\nval keyGen = KeyGenParameterSpec.Builder(\"fintech_auth_key\", KeyProperties.PURPOSE_SIGN)\n    .setDigests(KeyProperties.DIGEST_SHA256)\n    .setAlgorithmParameterSpec(ECGenParameterSpec(\"secp256r1\"))\n    .setUserAuthenticationRequired(true)\n    .setUserAuthenticationParameters(0, KeyProperties.AUTH_BIOMETRIC_STRONG)\n    .build()",
                    "common_pitfalls": ["Storing private keys in SharedPreferences or UserDefaults instead of KeyStore/KeyChain.", "Authorizing payments purely based on client-side boolean flags without server cryptographic nonce verification."]
                },
                "where": {"platform": "Mobile Security Standards", "url": "https://owasp.org/www-project-mobile-top-10/", "mnc_companies": ["Square/Block", "Stripe", "Robinhood", "PayPal", "Apple Pay"], "recommended_tools": "Android KeyStore / iOS KeyChain"},
                "when": {"recommended_time": "Afternoon (02:00 PM – 02:25 PM) — Mobile cryptography architecture", "duration_minutes": 25, "sprint_phase": "Day 2 of 14: Mobile AppSec & Biometrics"},
                "proof_criteria": {"deliverable": "Biometric cryptographic authentication flow diagram and KeyStore configuration.", "verification_method": "Vireoniq Design Twin"}
            },
            {
                "task_id": "mobile_task_alt_3",
                "title": "Draft STAR Story on Slashing Mobile App Crash-Free Rate to 99.95% Across 2M Active Devices",
                "task_type": "BEHAVIORAL_STAR",
                "estimated_minutes": 15,
                "projected_delta": "+0.7",
                "status": "COMPLETED",
                "difficulty": "Essential • Operational Reliability",
                "why": "Showcases automated crash grouping, staging phased rollouts, and defensive null-safety practices.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–4: Situation", "detail": "Major version release caused crash rate to jump to 2.4%, primarily NullPointerExceptions in legacy background notification handler."},
                        {"phase": "Minute 4–8: Task", "detail": "Halt rollout, patch root cause, and establish automated guardrails ensuring crash-free sessions exceed 99.9%."},
                        {"phase": "Minute 8–12: Action", "detail": "Paused phased rollout in Google Play Console; triaged crash stack traces via Crashlytics; enforced strict non-null Kotlin types and added pre-release automated UI monkey testing."},
                        {"phase": "Minute 12–15: Result", "detail": "Crash-free rate reached 99.96%; phased rollout policy adopted as standard engineering SOP."}
                    ],
                    "optimal_approach": "Swift triage -> Phased rollout halt -> Strict null safety typing -> Automated smoke testing.",
                    "code_blueprint": "Situation: A production release caused app crashes to spike to 2.4% on Android 14 devices due to a modified background intent payload.\nTask: Halt the release blast radius, diagnose root cause within 2 hours, and lift crash-free users back above 99.9%.\nAction: Halted phased rollout at 10%; analyzed Crashlytics stack traces; shipped a hotfix with defensive null checks; instituted a mandatory 5% staged release rule.\nResult: Achieved 99.96% crash-free session rate across 2 million devices; zero further regressions across subsequent releases.",
                    "common_pitfalls": ["Failing to immediately pause staged release rollout upon detecting crash spike.", "Not establishing systemic regression testing to prevent identical future failures."]
                },
                "where": {"platform": "Vireoniq Interview Twin Studio", "url": "/app/interview-simulator", "mnc_companies": ["Google", "Apple", "Uber", "Spotify", "Meta"], "recommended_tools": "Vireoniq Voice Studio"},
                "when": {"recommended_time": "Evening (05:00 PM – 05:15 PM) — Reliability rehearsal", "duration_minutes": 15, "sprint_phase": "Day 2 of 14: Mobile App Reliability"},
                "proof_criteria": {"deliverable": "Structured STAR narrative with Crashlytics telemetry data.", "verification_method": "Automated AI rubric"}
            }
        ]
    },

    # ─── 8. CYBERSECURITY ENGINEER ──────────────────────────────────────────
    "Cybersecurity Engineer": {
        "active_plan_title": "14-Day Cybersecurity Engineer Accelerated Readiness Sprints",
        "rationale": "Eliminating bottlenecks in zero-trust mTLS authorization, OAuth2 PKCE replay defense & automated SAST/DAST vuln triage.",
        "tasks": [
            {
                "task_id": "cyber_task_1",
                "title": "Solve LeetCode #227: Basic Calculator II (Expression Parsing & Sanitization)",
                "task_type": "CODING_DRILL",
                "estimated_minutes": 25,
                "projected_delta": "+1.2",
                "status": "PENDING",
                "difficulty": "Medium • Input Validation & Grammar",
                "why": "Tests stack parsing without eval(), preventing remote code execution (RCE) vulnerabilities.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–5: Operator Precedence", "detail": "Multiplication and division have higher precedence than addition and subtraction. Use stack to evaluate immediate * and / operations."},
                        {"phase": "Minute 5–15: Stack Operations", "detail": "Iterate through string. For '+', push num. For '-', push -num. For '*' or '/', pop top, evaluate with current num, and push result back."},
                        {"phase": "Minute 15–25: Final Summation", "detail": "Sum all elements in stack. Pure O(N) time and O(N) space."}
                    ],
                    "optimal_approach": "Stack-based operator precedence parser without dangerous eval() execution.",
                    "code_blueprint": "def calculate(s: str) -> int:\n    stack = []\n    num = 0\n    sign = '+'\n    for i, c in enumerate(s):\n        if c.isdigit(): num = num * 10 + int(c)\n        if c in '+-*/' or i == len(s) - 1:\n            if sign == '+': stack.append(num)\n            elif sign == '-': stack.append(-num)\n            elif sign == '*': stack.append(stack.pop() * num)\n            elif sign == '/': stack.append(int(stack.pop() / num))\n            sign = c\n            num = 0\n    return sum(stack)",
                    "common_pitfalls": ["Using eval() which is an instant security vulnerability failure in any MNC coding interview.", "Truncating negative division incorrectly (Python // floors towards -infinity, use int(a / b))."]
                },
                "where": {"platform": "LeetCode #227", "url": "https://leetcode.com/problems/basic-calculator-ii/", "mnc_companies": ["CrowdStrike", "Palo Alto Networks", "Cloudflare", "Google", "Amazon"], "recommended_tools": "LeetCode / Python"},
                "when": {"recommended_time": "Morning (09:00 AM – 09:25 AM) — Parsing & input sanitization", "duration_minutes": 25, "sprint_phase": "Day 1 of 14: Secure Input Parsing"},
                "proof_criteria": {"deliverable": "Accepted LeetCode submission without eval() usage.", "verification_method": "Vireoniq Coding Studio"}
            },
            {
                "task_id": "cyber_task_2",
                "title": "Architect Zero-Trust Micro-Segmentation & Mutual TLS (mTLS) with SPIFFE/SPIRE",
                "task_type": "SYSTEM_DESIGN",
                "estimated_minutes": 25,
                "projected_delta": "+1.4",
                "status": "PENDING",
                "difficulty": "Advanced • Zero-Trust Security",
                "why": "Enforces cryptographically verifiable workload identities, dynamic X.509 certificate rotation, and egress filtering.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–7: SPIFFE ID & Workload Attestation", "detail": "Issue cryptographically verified SPIFFE IDs (spiffe://vireoniq.internal/ns/prod/sa/payment-svc) based on node and pod attestation."},
                        {"phase": "Minute 7–16: Automated mTLS Handshake & Rotation", "detail": "Envoy sidecars establish mutual TLS using ephemeral X.509 SVIDs rotated every 60 minutes with zero downtime."},
                        {"phase": "Minute 16–25: L7 Authorization Policies", "detail": "Enforce strict deny-by-default Istio AuthorizationPolicy matching client SPIFFE IDs and specific REST verbs."}
                    ],
                    "optimal_approach": "SPIRE Workload Attestor + Envoy Sidecar mTLS + Deny-All Istio Authorization Policies.",
                    "code_blueprint": "apiVersion: security.istio.io/v1beta1\nkind: AuthorizationPolicy\nmetadata:\n  name: payment-access-control\n  namespace: production\nspec:\n  selector:\n    matchLabels:\n      app: payment-service\n  action: ALLOW\n  rules:\n  - from:\n    - source:\n        principals: [\"cluster.local/ns/production/sa/checkout-service-account\"]\n    to:\n    - operation:\n        methods: [\"POST\"]\n        paths: [\"/api/v1/charge\"]",
                    "common_pitfalls": ["Relying on network perimeter firewalls (IP/port) instead of cryptographic cryptographic workload identity.", "Allowing long-lived root certificates without automated rotation."]
                },
                "where": {"platform": "Zero-Trust Architecture Sandbox", "url": "https://spiffe.io/", "mnc_companies": ["Cloudflare", "CrowdStrike", "Google", "Amazon", "Palo Alto Networks"], "recommended_tools": "SPIFFE / SPIRE / Envoy / Istio"},
                "when": {"recommended_time": "Afternoon (02:00 PM – 02:25 PM) — Zero-trust system design", "duration_minutes": 25, "sprint_phase": "Day 1 of 14: Workload Identity & Cryptography"},
                "proof_criteria": {"deliverable": "mTLS handshake sequence diagram and Istio AuthorizationPolicy YAML.", "verification_method": "Vireoniq Design Twin"}
            },
            {
                "task_id": "cyber_task_3",
                "title": "Draft STAR Story on Triage and Remediation of Zero-Day RCE Vulnerability in Production",
                "task_type": "BEHAVIORAL_STAR",
                "estimated_minutes": 15,
                "projected_delta": "+0.8",
                "status": "COMPLETED",
                "difficulty": "Critical • SecOps / Incident Response",
                "why": "Highlights containment speed, ethical disclosure, customer impact assessment, and automated hotfix patching.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–3: Situation", "detail": "Critical zero-day Log4j/Spring4Shell RCE disclosed affecting public-facing search microservices."},
                        {"phase": "Minute 3–7: Task", "detail": "Detect affected containers, block active exploit probes at WAF edge, and deploy patched dependencies within 6 hours."},
                        {"phase": "Minute 7–11: Action", "detail": "Applied Cloudflare WAF regex rule blocking JNDI payloads; audited container image bill of materials (SBOM); patched dependencies and rolled out new images via automated CI."},
                        {"phase": "Minute 11–15: Result", "detail": "Zero unauthorized intrusion or exfiltration; praised by security committee for industry-leading containment velocity."}
                    ],
                    "optimal_approach": "Edge WAF virtual patching -> SBOM dependency audit -> Immutable container image replacement.",
                    "code_blueprint": "Situation: Critical zero-day RCE (CVSS 10.0) announced publicly, with exploit attempts hitting our ingress API within 45 minutes.\nTask: Contain threat immediately across 600 container workloads and deploy patched binaries with zero downtime.\nAction: Deployed an emergency WAF filter blocking malicious exploit payloads at the edge; generated automated SBOM diffs to identify vulnerable libraries; deployed patched images via CI.\nResult: 100% of attack probes blocked at perimeter; complete cluster remediation verified within 4 hours with zero customer data exposure.",
                    "common_pitfalls": ["Waiting for full binary rebuild before deploying virtual patch at WAF edge.", "Failing to conduct post-incident forensic log audits to verify no prior compromise."]
                },
                "where": {"platform": "Vireoniq Leadership Simulator", "url": "/app/interview-simulator", "mnc_companies": ["CrowdStrike", "Mandiant", "Google Security", "Cloudflare", "Microsoft"], "recommended_tools": "Vireoniq Voice Simulator"},
                "when": {"recommended_time": "Evening (05:00 PM – 05:15 PM) — Incident response reflection", "duration_minutes": 15, "sprint_phase": "Day 1 of 14: Vulnerability Response"},
                "proof_criteria": {"deliverable": "Structured STAR incident writeup with CVSS triage and edge mitigation steps.", "verification_method": "Automated AI rubric"}
            }
        ],
        "tasks_alt": [
            {
                "task_id": "cyber_task_alt_1",
                "title": "Solve LeetCode #128: Longest Consecutive Sequence (O(N) Hash Set)",
                "task_type": "CODING_DRILL",
                "estimated_minutes": 25,
                "projected_delta": "+1.2",
                "status": "PENDING",
                "difficulty": "Medium • Constant Time Lookup",
                "why": "Evaluates hash set membership verification in linear time without sorting.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–5: Hash Set Conversion", "detail": "Convert array to hash set (O(N)). Sorting is forbidden because it requires O(N log N)."},
                        {"phase": "Minute 5–15: Sequence Starting Point", "detail": "Only attempt to build sequence from num if (num - 1) is NOT in set. This ensures each number is visited at most twice."},
                        {"phase": "Minute 15–25: Length Tracking", "detail": "While (current_num + 1) in set, increment length. Update global max_streak. O(N) Time, O(N) Space."}
                    ],
                    "optimal_approach": "Hash Set with starting-point filtering (num - 1 not in set) for strict O(N) linear time.",
                    "code_blueprint": "def longestConsecutive(nums: list[int]) -> int:\n    num_set = set(nums)\n    longest = 0\n    for n in num_set:\n        if n - 1 not in num_set:\n            cur = n\n            streak = 1\n            while cur + 1 in num_set:\n                cur += 1\n                streak += 1\n            longest = max(longest, streak)\n    return longest",
                    "common_pitfalls": ["Checking every number without 'n - 1 not in num_set' check, causing O(N^2) worst case on consecutive arrays.", "Sorting the array first (violates O(N) complexity requirement)."]
                },
                "where": {"platform": "LeetCode #128", "url": "https://leetcode.com/problems/longest-consecutive-sequence/", "mnc_companies": ["Google", "Amazon", "Meta", "Microsoft", "Bloomberg"], "recommended_tools": "LeetCode / Python"},
                "when": {"recommended_time": "Morning (09:00 AM – 09:25 AM) — Hash set algorithms", "duration_minutes": 25, "sprint_phase": "Day 2 of 14: Linear Set Algorithms"},
                "proof_criteria": {"deliverable": "Accepted LeetCode submission passing all 76 test cases in O(N) time.", "verification_method": "Vireoniq Coding Studio"}
            },
            {
                "task_id": "cyber_task_alt_2",
                "title": "Design OAuth2.0 / OIDC Authorization Server with PKCE Defense",
                "task_type": "SYSTEM_DESIGN",
                "estimated_minutes": 25,
                "projected_delta": "+1.3",
                "status": "PENDING",
                "difficulty": "Senior • Identity & AuthSec",
                "why": "Guarantees authorization code interception protection, cryptographic code challenge hashing (S256), and token revocation.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–7: PKCE Protocol Flow", "detail": "Client generates random code_verifier, hashes with SHA-256 to create code_challenge. Sends challenge in initial /authorize request."},
                        {"phase": "Minute 7–16: Authorization Code Exchange", "detail": "Client sends plaintext code_verifier in /token POST request. Server computes SHA-256(verifier) and verifies match before issuing JWT."},
                        {"phase": "Minute 16–25: Token Revocation & Refresh Rotation", "detail": "Implement single-use refresh tokens with automatic detection of reuse (invalidates entire token family upon duplicate presentation)."}
                    ],
                    "optimal_approach": "OAuth 2.1 RFC 7636 PKCE with S256 challenge verification and refresh token family rotation.",
                    "code_blueprint": "import hashlib, base64\n\ndef generate_pkce_pair(verifier: str) -> str:\n    # Computes code_challenge = BASE64URL-ENCODE(SHA256(code_verifier))\n    digest = hashlib.sha256(verifier.encode('ascii')).digest()\n    return base64.urlsafe_b64encode(digest).decode('ascii').rstrip('=')",
                    "common_pitfalls": ["Using 'plain' code_challenge_method instead of S256.", "Not invalidating the authorization code immediately after first use (vulnerable to replay)."]
                },
                "where": {"platform": "OAuth2.0 / IETF Standards", "url": "https://oauth.net/2/pkce/", "mnc_companies": ["Okta", "Auth0", "Google Identity", "Microsoft", "Stripe"], "recommended_tools": "OAuth Playground / Postman"},
                "when": {"recommended_time": "Afternoon (02:00 PM – 02:25 PM) — Identity security architecture", "duration_minutes": 25, "sprint_phase": "Day 2 of 14: Authentication Protocols"},
                "proof_criteria": {"deliverable": "PKCE authorization sequence diagram and token exchange validation logic.", "verification_method": "Vireoniq Design Twin"}
            },
            {
                "task_id": "cyber_task_alt_3",
                "title": "Draft STAR Story on Architecting Automated SAST/DAST Security Gates in CI/CD",
                "task_type": "BEHAVIORAL_STAR",
                "estimated_minutes": 15,
                "projected_delta": "+0.7",
                "status": "COMPLETED",
                "difficulty": "Essential • DevSecOps Culture",
                "why": "Demonstrates friction-free developer enablement, automated Semgrep/Trivy gating, and zero false-positive tuning.",
                "how": {
                    "steps": [
                        {"phase": "Minute 0–4: Situation", "detail": "Penetration tests consistently revealed OWASP Top 10 vulnerabilities (SQLi, SSRF) right before major releases."},
                        {"phase": "Minute 4–8: Task", "detail": "Shift security left by integrating automated scanners into developer PR workflows without adding more than 2 minutes to build times."},
                        {"phase": "Minute 8–12: Action", "detail": "Configured Semgrep SAST rules and Trivy container scanning in GitHub Actions; tuned out noisy rules to prevent false-positive alert fatigue; automated auto-fix suggestions."},
                        {"phase": "Minute 12–15: Result", "detail": "Vulnerabilities caught before staging jumped to 94%; zero high-severity findings in subsequent external third-party pentest."}
                    ],
                    "optimal_approach": "Frictionless developer tooling -> Low false-positive custom rules -> High-impact automated PR comments.",
                    "code_blueprint": "Situation: Late-stage penetration tests discovered 12 critical vulnerabilities days before release, threatening customer compliance audits.\nTask: Implement an automated 'shift-left' security scanning pipeline directly in GitHub Actions without slowing down development.\nAction: Integrated Semgrep for AST analysis and Trivy for container scanning; tuned custom rules to eliminate 95% of false positives; provided inline remediation snippets.\nResult: 94% of security vulnerabilities caught and fixed at pull request stage; subsequent external pentest passed with zero high findings.",
                    "common_pitfalls": ["Deploying default scanner rules that trigger thousands of false positives and make developers ignore warnings.", "Blocking builds on low-severity informational notices."]
                },
                "where": {"platform": "Vireoniq Interview Twin Studio", "url": "/app/interview-simulator", "mnc_companies": ["Snyk", "GitHub Security", "Datadog", "CrowdStrike", "Palantir"], "recommended_tools": "Vireoniq Voice Studio"},
                "when": {"recommended_time": "Evening (05:00 PM – 05:15 PM) — DevSecOps leadership", "duration_minutes": 15, "sprint_phase": "Day 2 of 14: Shift-Left Security"},
                "proof_criteria": {"deliverable": "STAR reflection writeup on developer enablement and vulnerability reduction metrics.", "verification_method": "Automated AI rubric"}
            }
        ]
    }
}
