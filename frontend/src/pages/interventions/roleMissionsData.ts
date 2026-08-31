import type { DailyMissionData, DailyMissionTask } from '@/api/careerIntelligenceApi';

export const TOP_25_MNCS = [
  "Google", "Amazon", "Meta", "Microsoft", "Uber", "Bloomberg", "Adobe",
  "Apple", "Netflix", "Salesforce", "Atlassian", "LinkedIn", "Goldman Sachs",
  "Oracle", "Stripe", "ByteDance", "PayPal", "Intuit", "ServiceNow", "Twilio",
  "Morgan Stanley", "Cisco", "Airbnb", "Databricks", "Spotify", "Snowflake"
];

export function normalizeRole(role: string): string {
  const r = (role || "").trim().toLowerCase();
  if (r.includes("data")) return "Data Engineer";
  if (r.includes("devops") || r.includes("sre")) return "DevOps / SRE";
  if (r.includes("cloud") || r.includes("architect")) return "Cloud Architect";
  if (r.includes("mobile") || r.includes("ios") || r.includes("android")) return "Mobile Engineer";
  if (r.includes("cyber") || r.includes("security")) return "Cybersecurity Engineer";
  if (r.includes("full") || r.includes("stack") || r.includes("frontend")) return "Full Stack Engineer";
  if (r.includes("ai") || r.includes("ml") || r.includes("machine")) return "AI/ML Engineer";
  return "Backend Engineer";
}

const todayDate = new Date().toISOString().split('T')[0];

export const ROLE_MISSIONS_PRIMARY: Record<string, DailyMissionData> = {
  "AI/ML Engineer": {
    mission_date: todayDate,
    target_role: "AI/ML Engineer",
    active_plan_title: "14-Day AI/ML Engineer Accelerated Readiness Sprints",
    rationale: "Targeting your highest-ROI bottlenecks in distributed systems, feature pipelines & algorithmic complexity.",
    tasks_count: 3,
    total_estimated_minutes: 60,
    progress_pct: 35,
    tasks: [
      {
        task_id: "aiml-1",
        title: "Solve LeetCode #560: Subarray Sum Equals K (O(N) Prefix Sum)",
        task_type: "CODING_DRILL",
        estimated_minutes: 25,
        projected_delta: "+1.2",
        status: "PENDING",
        difficulty: "Medium • Tier-1 MNC Core",
        why: "Strengthens your Arrays & Hash Map competency for Tier-1 MNC algorithmic screening.",
        how: {
          steps: [
            { phase: "Minute 0–5: Constraints & Edge Cases", detail: "Clarify: Can elements or k be negative? (Yes! Negative numbers invalidate sliding window). Identify space/time limits: N <= 2*10^4." },
            { phase: "Minute 5–12: Mathematical Formulation", detail: "Prefix sum property: sum(i to j) = prefix[j] - prefix[i-1] = k => prefix[i-1] = prefix[j] - k. Maintain running sum in a hash map with frequency counts. Initialize prefix_map = {0: 1}." },
            { phase: "Minute 12–20: Clean Implementation", detail: "Iterate once through nums. Add current num to running sum. Check if (running_sum - k) is in prefix_map. Increment count by frequency. Then increment map[running_sum]." },
            { phase: "Minute 20–25: MNC Dry-Run & Edge Cases", detail: "Trace edge cases: nums=[1, -1, 0], k=0; nums=[1], k=0. Confirm O(N) time and O(N) auxiliary space." }
          ],
          optimal_approach: "Single-pass Prefix Sum with Hash Map frequency counter. O(N) Time, O(N) Space.",
          code_blueprint: `def subarraySum(nums: list[int], k: int) -> int:
    count = 0
    current_sum = 0
    prefix_counts = {0: 1}
    for num in nums:
        current_sum += num
        if (current_sum - k) in prefix_counts:
            count += prefix_counts[current_sum - k]
        prefix_counts[current_sum] = prefix_counts.get(current_sum, 0) + 1
    return count`,
          common_pitfalls: [
            "Using Two Pointers or Sliding Window (fails with negative numbers or zeroes).",
            "Forgetting base case prefix_counts = {0: 1}, causing off-by-one errors on prefix matches.",
            "Adding current_sum to the map before checking (current_sum - k)."
          ]
        },
        where: {
          platform: "LeetCode #560",
          url: "https://leetcode.com/problems/subarray-sum-equals-k/",
          mnc_companies: ["Google", "Meta", "Amazon", "Microsoft", "Uber", "Apple"],
          recommended_tools: "LeetCode Scratchpad or VS Code + Python 3.12 / Java"
        },
        when: {
          recommended_time: "Morning (09:00 AM – 09:25 AM) — Algorithmic focus",
          duration_minutes: 25,
          sprint_phase: "Day 1 of 14: Data Structures Foundation"
        },
        proof_criteria: {
          deliverable: "Accepted LeetCode submission screenshot or GitHub commit link with runtime >85% percentile.",
          verification_method: "Paste submission URL or test in MNC Coding Studio"
        }
      },
      {
        task_id: "aiml-2",
        title: "Draft STAR Behavioral Story on Disagreement & Architecture Tradeoff",
        task_type: "BEHAVIORAL_STAR",
        estimated_minutes: 20,
        projected_delta: "+0.8",
        status: "PENDING",
        difficulty: "Essential • Bar Raiser Round",
        why: "Elevates Leadership & Cultural Alignment readiness score.",
        how: {
          steps: [
            { phase: "Minute 0–5: Situation & Context", detail: "Pick a real technical disagreement (e.g. streaming tokens directly via SSE vs buffered polling). Set context, deadline, and stakes." },
            { phase: "Minute 5–10: Task & The Conflict", detail: "State the challenge: Team lead preferred polling for simplicity, but client p99 TTFT was failing SLAs." },
            { phase: "Minute 10–15: Action with Concrete Data", detail: "Built a 1-day benchmark testing SSE with HTTP/2 multiplexing vs chunked REST under 2,000 concurrent queries. Presented findings neutrally." },
            { phase: "Minute 15–20: Result & Business Impact", detail: "Team adopted SSE; TTFT dropped from 1.4s to 240ms, user perceived latency fell by 82%." }
          ],
          optimal_approach: "STAR Framework (Situation, Task, Action, Result) with measurable metrics and 'Disagree and Commit' leadership principles.",
          code_blueprint: `Situation: In our LLM feature pipeline, team debated streaming tokens directly via SSE vs buffered polling.
Task: As the AI/ML engineer, needed to achieve <300ms Time-To-First-Token without overwhelming backend connection pools.
Action: Created a 1-day benchmark testing SSE with HTTP/2 multiplexing vs chunked REST under 2,000 concurrent simulated queries.
Result: Team adopted SSE; TTFT dropped from 1.4s to 240ms, user perceived latency fell by 82%.`,
          common_pitfalls: [
            "Sounding combative or presenting teammate as incompetent.",
            "Lacking concrete quantifiable metrics in the Result phase.",
            "Focusing too much on the Situation rather than YOUR personal actions."
          ]
        },
        where: {
          platform: "Vireoniq Interview Twin Studio",
          url: "/app/interview-simulator",
          mnc_companies: ["Amazon", "Google", "Microsoft", "Meta", "Uber", "Apple"],
          recommended_tools: "Vireoniq Voice Rehearsal Studio or Smartphone Voice Memos"
        },
        when: {
          recommended_time: "Afternoon (02:00 PM – 02:20 PM) — Communication focus",
          duration_minutes: 20,
          sprint_phase: "Day 1 of 14: Leadership & Behavioral Alignment"
        },
        proof_criteria: {
          deliverable: "Structured 4-bullet STAR written summary or 90-second audio recording rehearsal.",
          verification_method: "Submit in Vireoniq Behavioral Studio for automated AI tone scoring"
        }
      },
      {
        task_id: "aiml-3",
        title: "Simulate Distributed Idempotency in Notification Microservices",
        task_type: "SYSTEM_DESIGN",
        estimated_minutes: 15,
        projected_delta: "+1.5",
        status: "COMPLETED",
        difficulty: "Advanced • HLD & LLD Core",
        why: "Directly addresses primary bottleneck in distributed systems resilience.",
        how: {
          steps: [
            { phase: "Minute 0–3: Idempotency Contract", detail: "Define API contract: Client transmits unique 'Idempotency-Key: UUIDv4' in header." },
            { phase: "Minute 3–7: Redis Distributed Lock & Cache", detail: "Atomic check-and-set in Redis: SET idempotency:{key} 'PROCESSING' EX 300 NX." },
            { phase: "Minute 7–11: Transactional Outbox & DB Commit", detail: "Execute business logic within single ACID transaction. Write to idempotency_records table." },
            { phase: "Minute 11–15: Failure Modes & Recovery", detail: "Handle worker crash before completion (TTL expires, allows safe retry)." }
          ],
          optimal_approach: "Header Idempotency Key + Redis Atomic SETNX (300s TTL) + Relational Outbox Pattern for ACID guarantees.",
          code_blueprint: `async def process_with_idempotency(idempotency_key: str, payload: dict):
    is_new = await redis.set(f"idemp:{idempotency_key}", "PROCESSING", ex=300, nx=True)
    if not is_new:
        cached = await redis.get(f"idemp:{idempotency_key}")
        if cached != "PROCESSING": return json.loads(cached)
        raise HTTPException(409, "Request currently in-flight")
    try:
        result = await execute_core_action(payload)
        await redis.set(f"idemp:{idempotency_key}", json.dumps(result), ex=86400)
        return result
    except Exception as exc:
        await redis.delete(f"idemp:{idempotency_key}")
        raise exc`,
          common_pitfalls: [
            "Non-atomic check-then-set allowing race condition.",
            "Infinite deadlock when worker dies without TTL.",
            "Returning error on duplicate instead of identical previous response."
          ]
        },
        where: {
          platform: "System Design Sandbox",
          url: "https://excalidraw.com",
          mnc_companies: ["Uber", "Netflix", "Stripe", "Amazon", "Meta", "Google"],
          recommended_tools: "Excalidraw, Draw.io, or Vireoniq System Design Architecture Sandbox"
        },
        when: {
          recommended_time: "Evening (05:00 PM – 05:15 PM) — Architecture synthesis",
          duration_minutes: 15,
          sprint_phase: "Day 1 of 14: Distributed Systems Resilience"
        },
        proof_criteria: {
          deliverable: "Sequence diagram showing Client, Gateway, Redis Lock, and DB Outbox.",
          verification_method: "Architecture review checklist verified in Vireoniq Design Twin"
        }
      }
    ]
  },

  "Backend Engineer": {
    mission_date: todayDate,
    target_role: "Backend Engineer",
    active_plan_title: "14-Day Backend Engineer Accelerated Readiness Sprints",
    rationale: "Eliminating critical bottlenecks in distributed data consistency, caching invalidation & concurrent query optimization.",
    tasks_count: 3,
    total_estimated_minutes: 65,
    progress_pct: 35,
    tasks: [
      {
        task_id: "be-1",
        title: "Solve LeetCode #146: LRU Cache Implementation (O(1) Get & Put)",
        task_type: "CODING_DRILL",
        estimated_minutes: 30,
        projected_delta: "+1.3",
        status: "PENDING",
        difficulty: "Medium • #1 Most Asked in MNC Loops",
        why: "Tests Doubly Linked List pointer manipulation and Hash Map composite design under strict O(1) constraints.",
        how: {
          steps: [
            { phase: "Minute 0–5: Strategy", detail: "Combination of Hash Map (key -> node) + Doubly Linked List (usage order) achieves O(1) get & put." },
            { phase: "Minute 5–15: Sentinels", detail: "Use pseudo-head and pseudo-tail dummy sentinel nodes to eliminate null boundary checks." },
            { phase: "Minute 15–25: Methods", detail: "get: move node to head. put: insert at head, if capacity exceeded pop tail.prev." },
            { phase: "Minute 25–30: Edge Cases", detail: "Test capacity=1 eviction, re-inserting existing keys, O(1) complexity." }
          ],
          optimal_approach: "Hash Map mapping keys to Doubly Linked List nodes with Dummy Sentinels. O(1) Time, O(Capacity) Space.",
          code_blueprint: `class Node:
    def __init__(self, key=0, val=0):
        self.key, self.val = key, val
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.map = {}
        self.head, self.tail = Node(), Node()
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key in self.map:
            node = self.map[key]
            self._remove(node)
            self._add(node)
            return node.val
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.map:
            self._remove(self.map[key])
        node = Node(key, value)
        self._add(node)
        self.map[key] = node
        if len(self.map) > self.cap:
            lru = self.tail.prev
            self._remove(lru)
            del self.map[lru.key]`,
          common_pitfalls: ["Forgetting to delete evicted node key from hash map.", "Forgetting to update node position on get."]
        },
        where: {
          platform: "LeetCode #146",
          url: "https://leetcode.com/problems/lru-cache/",
          mnc_companies: ["Google", "Amazon", "Meta", "Microsoft", "Stripe", "Bloomberg"],
          recommended_tools: "LeetCode / VS Code"
        },
        when: {
          recommended_time: "Morning (09:00 AM – 09:30 AM) — Core algorithmic sprint",
          duration_minutes: 30,
          sprint_phase: "Day 1 of 14: In-Memory Data Structures"
        },
        proof_criteria: {
          deliverable: "Accepted LeetCode submission passing all 22 testcases in O(1) time.",
          verification_method: "Submit verified solution link"
        }
      },
      {
        task_id: "be-2",
        title: "Architect Zero-Downtime Database Migration via Expand-Contract Pattern",
        task_type: "SYSTEM_DESIGN",
        estimated_minutes: 20,
        projected_delta: "+1.0",
        status: "PENDING",
        difficulty: "Senior Level • Production Engineering",
        why: "Demonstrates production database engineering maturity required by Stripe, GitHub, and Uber.",
        how: {
          steps: [
            { phase: "Minute 0–5: Lock Risk", detail: "Renaming columns locks tables with AccessExclusiveLock, causing downtime for high-volume transactions." },
            { phase: "Minute 5–10: Phase 1 Expand", detail: "Add new column as NULLABLE. Deploy app code writing to both columns (Dual-Write)." },
            { phase: "Minute 10–15: Phase 2 Backfill", detail: "Run background worker backfilling historical rows in small 5,000-row batches." },
            { phase: "Minute 15–20: Phase 3 Contract", detail: "Switch app reads to new column. Verify 0 reads on old. Safely drop old column." }
          ],
          optimal_approach: "Expand-Contract Pattern with batched asynchronous historical backfills.",
          code_blueprint: `-- Step 1: Expand
ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);
-- Step 2: Application Dual-write in code
-- Step 3: Batched Backfill in worker
UPDATE users SET full_name = first_name || ' ' || last_name WHERE full_name IS NULL AND id BETWEEN 1 AND 5000;
-- Step 4: Contract
ALTER TABLE users DROP COLUMN IF EXISTS first_name, DROP COLUMN IF EXISTS last_name;`,
          common_pitfalls: ["Executing massive backfill in single transaction locking entire table.", "Switching reads before 100% backfill complete."]
        },
        where: {
          platform: "PostgreSQL Sandbox",
          url: "https://stripe.com/blog/online-migrations",
          mnc_companies: ["Stripe", "GitHub", "Shopify", "Amazon", "Uber"],
          recommended_tools: "Alembic Migrations / pgAdmin"
        },
        when: {
          recommended_time: "Afternoon (02:00 PM – 02:20 PM) — Production database focus",
          duration_minutes: 20,
          sprint_phase: "Day 1 of 14: Production Database Operations"
        },
        proof_criteria: {
          deliverable: "Alembic 3-step migration plan with dual-write handler code.",
          verification_method: "Pass schema validation in Vireoniq CI"
        }
      },
      {
        task_id: "be-3",
        title: "Draft STAR Story on Mitigating Production P0 Incident (Cascading Failures)",
        task_type: "BEHAVIORAL_STAR",
        estimated_minutes: 15,
        projected_delta: "+0.7",
        status: "COMPLETED",
        difficulty: "Critical • SRE / Leadership Loop",
        why: "Validates incident response maturity, psychological safety under pressure, and systematic post-mortem ownership.",
        how: {
          steps: [
            { phase: "Minute 0–3: Situation", detail: "Cascading failure brought down API gateway during peak flash sale; 504 Timeouts spiked to 18%." },
            { phase: "Minute 3–7: Task", detail: "Immediate blast-radius containment before root cause analysis. Avoided reckless restarts." },
            { phase: "Minute 7–11: Action", detail: "Enabled circuit breaker shedding 30% background load. Injected Redis cache fallback. Traffic normalized in 4 min." },
            { phase: "Minute 11–15: Result", detail: "Zero customer data loss. Authored blameless post-mortem, configured automated rate limiting." }
          ],
          optimal_approach: "Containment -> Triage -> Resolution -> Blameless Post-Mortem with quantifiable MTTR.",
          code_blueprint: `Situation: At 2:15 PM during product launch, database connection pool exhausted due to unindexed query spike.
Task: Restore 99.9% availability within 10-minute SLA window.
Action: Injected rate limiting at Nginx edge, shed async report exports, killed hung DB connections, and deployed hotfix index in 6 minutes.
Result: Restored full service in 7 minutes (MTTR -58% vs avg), added DB pool watchdog that prevents connection exhaustion.`,
          common_pitfalls: ["Blaming other engineers for deploying bad code.", "Skipping preventive post-mortem actions."]
        },
        where: {
          platform: "Vireoniq Leadership Simulator",
          url: "/app/interview-simulator",
          mnc_companies: ["Google", "Amazon", "Microsoft", "Uber", "Netflix"],
          recommended_tools: "Vireoniq Voice Simulator"
        },
        when: {
          recommended_time: "Evening (05:00 PM – 05:15 PM) — Operational reflection",
          duration_minutes: 15,
          sprint_phase: "Day 1 of 14: Engineering Operational Excellence"
        },
        proof_criteria: {
          deliverable: "Completed 4-part STAR writeup with MTTR metrics and post-mortem preventative measures.",
          verification_method: "Submit for automated leadership rubric evaluation"
        }
      }
    ]
  },

  "Full Stack Engineer": {
    mission_date: todayDate,
    target_role: "Full Stack Engineer",
    active_plan_title: "14-Day Full Stack Engineer Accelerated Readiness Sprints",
    rationale: "Unifying high-throughput frontend reactivity, asynchronous state reconciliation & resilient API contracts.",
    tasks_count: 3,
    total_estimated_minutes: 65,
    progress_pct: 35,
    tasks: [
      {
        task_id: "fs-1",
        title: "Solve LeetCode #3: Longest Substring Without Repeating Characters",
        task_type: "CODING_DRILL",
        estimated_minutes: 25,
        projected_delta: "+1.1",
        status: "PENDING",
        difficulty: "Medium • Essential Sliding Window",
        why: "Evaluates dynamic sliding window two-pointer tracking and hash index lookup under linear O(N) performance.",
        how: {
          steps: [
            { phase: "Minute 0–5: Window Boundaries", detail: "Maintain [left, right] indices. When char at 'right' in window, jump left = max(left, map[char] + 1)." },
            { phase: "Minute 5–15: Execution", detail: "Store character -> last seen index. Update max_len = max(max_len, right - left + 1)." },
            { phase: "Minute 15–25: Edge Cases", detail: "Check empty string, single char, all repeating chars. Confirm O(N) time and O(min(N, Alphabet)) space." }
          ],
          optimal_approach: "Sliding Window with Hash Map Index Pointer Jump. O(N) Time, O(min(M, N)) Space.",
          code_blueprint: `def lengthOfLongestSubstring(s: str) -> int:
    char_map = {}
    left = 0
    max_len = 0
    for right, ch in enumerate(s):
        if ch in char_map and char_map[ch] >= left:
            left = char_map[ch] + 1
        char_map[ch] = right
        max_len = max(max_len, right - left + 1)
    return max_len`,
          common_pitfalls: ["Forgetting char_map[ch] >= left, causing left pointer to jump backwards.", "String slicing in loop making it O(N^2)."]
        },
        where: {
          platform: "LeetCode #3",
          url: "https://leetcode.com/problems/longest-substring-without-repeating-characters/",
          mnc_companies: ["Google", "Meta", "Amazon", "Microsoft", "Uber", "Apple"],
          recommended_tools: "LeetCode / VS Code"
        },
        when: {
          recommended_time: "Morning (09:00 AM – 09:25 AM) — Algorithmic sharpness",
          duration_minutes: 25,
          sprint_phase: "Day 1 of 14: Two-Pointer & Sliding Window Mastery"
        },
        proof_criteria: {
          deliverable: "Accepted LeetCode solution with 100% test suite passing.",
          verification_method: "Submission link verified in Vireoniq Coding Studio"
        }
      },
      {
        task_id: "fs-2",
        title: "Implement Optimistic UI Mutations with Automatic Rollback & Toast Feedback",
        task_type: "BUILD",
        estimated_minutes: 25,
        projected_delta: "+1.2",
        status: "PENDING",
        difficulty: "Intermediate • Client Architecture",
        why: "Creates instant snappy client responsiveness expected in Tier-1 product applications (Linear, Figma, Notion).",
        how: {
          steps: [
            { phase: "Minute 0–5: Optimistic State", detail: "Snapshot current state to previousState before firing network request." },
            { phase: "Minute 5–12: Cache Mutation", detail: "Apply expected successful state to UI state immediately in 0ms." },
            { phase: "Minute 12–20: OnError Rollback", detail: "On network error/timeout, catch exception, revert cache to previousState, and trigger error toast." },
            { phase: "Minute 20–25: OnSettled", detail: "Invalidate query on settled to synchronize with server truth." }
          ],
          optimal_approach: "Optimistic Cache Update + Snapshot Capture + OnError Rollback with User Notification.",
          code_blueprint: `const useUpdateTaskMutation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (updatedTask) => api.updateTask(updatedTask),
    onMutate: async (newTask) => {
      await queryClient.cancelQueries({ queryKey: ['tasks'] });
      const previousTasks = queryClient.getQueryData(['tasks']);
      queryClient.setQueryData(['tasks'], (old) =>
        old.map((t) => (t.id === newTask.id ? { ...t, ...newTask } : t))
      );
      return { previousTasks };
    },
    onError: (err, newTask, context) => {
      queryClient.setQueryData(['tasks'], context?.previousTasks);
      toast.error('Network sync failed. Changes reverted.');
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
};`,
          common_pitfalls: ["Failing to cancel outgoing queries before setting optimistic cache.", "Not notifying user on rollback."]
        },
        where: {
          platform: "React 18 + TanStack Query Sandbox",
          url: "https://tanstack.com/query/latest/docs/framework/react/guides/optimistic-updates",
          mnc_companies: ["Meta", "Uber", "Airbnb", "Atlassian", "Stripe"],
          recommended_tools: "Vite + React Playground"
        },
        when: {
          recommended_time: "Afternoon (02:00 PM – 02:25 PM) — Client state focus",
          duration_minutes: 25,
          sprint_phase: "Day 1 of 14: Client State Management"
        },
        proof_criteria: {
          deliverable: "Working optimistic mutation custom hook with rollback and error toasts.",
          verification_method: "Interactive demo test in Vireoniq Sandbox"
        }
      },
      {
        task_id: "fs-3",
        title: "Draft STAR Story on Balancing Technical Debt vs Product Launch Deadlines",
        task_type: "BEHAVIORAL_STAR",
        estimated_minutes: 15,
        projected_delta: "+0.7",
        status: "COMPLETED",
        difficulty: "Essential • Product Mindset",
        why: "Validates ability to navigate trade-offs between clean architecture and commercial delivery velocity.",
        how: {
          steps: [
            { phase: "Minute 0–3: Situation", detail: "2 weeks before Q3 demo, product needed instant export feature; backend lacked batch export pipeline." },
            { phase: "Minute 3–7: Task", detail: "Deliver export without locking relational DB or hacking brittle client-side CSV generator." },
            { phase: "Minute 7–11: Action", detail: "Implemented lightweight streamed chunked JSON export with client-side Blob generator. Logged technical debt ticket with clear threshold trigger." },
            { phase: "Minute 11–15: Result", detail: "Launched on time, 100% success rate, seamlessly migrated to S3 queue when traffic reached target threshold." }
          ],
          optimal_approach: "Engineering pragmatism: Deliberate technical debt with documented repayment triggers.",
          code_blueprint: `Situation: 2 weeks before Q3 demo, product needed instant export feature; backend lacked batch export pipeline.
Task: Deliver export without locking relational DB or hacking brittle client-side CSV generator.
Action: Implemented lightweight streamed chunked JSON export with client-side Blob generator. Logged technical debt ticket with clear threshold trigger.
Result: Launched on time, 100% success rate, seamlessly migrated to S3 queue when traffic reached target threshold.`,
          common_pitfalls: ["Refusing to compromise with product, appearing dogmatic.", "Accumulating tech debt silently."]
        },
        where: {
          platform: "Vireoniq Interview Twin Studio",
          url: "/app/interview-simulator",
          mnc_companies: ["Meta", "Google", "Amazon", "Microsoft", "Apple", "Uber"],
          recommended_tools: "Vireoniq Audio Simulator"
        },
        when: {
          recommended_time: "Evening (05:00 PM – 05:15 PM) — Behavioral mastery",
          duration_minutes: 15,
          sprint_phase: "Day 1 of 14: Product Engineering Leadership"
        },
        proof_criteria: {
          deliverable: "Written STAR reflection highlighting measurable business outcome.",
          verification_method: "Submit for automated AI rubric scoring"
        }
      }
    ]
  },

  "Data Engineer": {
    mission_date: todayDate,
    target_role: "Data Engineer",
    active_plan_title: "14-Day Data Engineer Accelerated Readiness Sprints",
    rationale: "Eliminating critical bottlenecks in distributed lakehouse partitioning, streaming pipelines & idempotent batch transformations.",
    tasks_count: 3,
    total_estimated_minutes: 65,
    progress_pct: 35,
    tasks: [
      {
        task_id: "de-1",
        title: "Solve LeetCode #185: Department Top Three Salaries (SQL DENSE_RANK)",
        task_type: "CODING_DRILL",
        estimated_minutes: 25,
        projected_delta: "+1.2",
        status: "PENDING",
        difficulty: "Medium • Tier-1 Big Data Core",
        why: "Evaluates SQL analytical window partitioning, DENSE_RANK() vs RANK(), and subquery filtering under large enterprise data volumes.",
        how: {
          steps: [
            { phase: "Minute 0–5: Window Function Strategy", detail: "DENSE_RANK() guarantees consecutive sequence (1, 1, 2, 3) across duplicate salaries, unlike RANK() which skips numbers." },
            { phase: "Minute 5–15: CTE Partitioning", detail: "Partition by departmentId and order by salary DESC inside CTE." },
            { phase: "Minute 15–25: Filter & Join", detail: "Filter where rnk <= 3 and join with Department table for human-readable output." }
          ],
          optimal_approach: "CTE with DENSE_RANK() window function partitioned by Department. O(N log N) sorting time, O(N) space.",
          code_blueprint: `WITH RankedSalaries AS (
    SELECT
        d.name AS Department,
        e.name AS Employee,
        e.salary AS Salary,
        DENSE_RANK() OVER (
            PARTITION BY e.departmentId 
            ORDER BY e.salary DESC
        ) AS rnk
    FROM Employee e
    JOIN Department d ON e.departmentId = d.id
)
SELECT Department, Employee, Salary
FROM RankedSalaries
WHERE rnk <= 3;`,
          common_pitfalls: ["Using RANK() instead of DENSE_RANK(), excluding 3rd salary on ties.", "Using correlated subqueries with O(N^2) complexity."]
        },
        where: {
          platform: "LeetCode #185",
          url: "https://leetcode.com/problems/department-top-three-salaries/",
          mnc_companies: ["Snowflake", "Databricks", "Amazon", "Meta", "Google", "Bloomberg"],
          recommended_tools: "PostgreSQL / Snowflake / LeetCode"
        },
        when: {
          recommended_time: "Morning (09:00 AM – 09:25 AM) — SQL analytical query sprint",
          duration_minutes: 25,
          sprint_phase: "Day 1 of 14: Analytical SQL & Window Functions"
        },
        proof_criteria: {
          deliverable: "Accepted SQL submission passing all test cases.",
          verification_method: "MNC Coding Studio"
        }
      },
      {
        task_id: "de-2",
        title: "Architect Stream-Table Join Pipeline with Apache Flink & Kafka Debezium CDC",
        task_type: "SYSTEM_DESIGN",
        estimated_minutes: 25,
        projected_delta: "+1.4",
        status: "PENDING",
        difficulty: "Advanced • Streaming Architecture",
        why: "Demonstrates real-time stateful stream processing, watermarking, and out-of-order event reconciliation.",
        how: {
          steps: [
            { phase: "Minute 0–7: CDC Ingress", detail: "Capture relational OLTP changes via Debezium CDC into Kafka topic. Stream telemetry events in real-time." },
            { phase: "Minute 7–16: Stateful Join with Flink", detail: "Implement Temporal Table Join with event-time watermarking to tolerate up to 10s network latency." },
            { phase: "Minute 16–25: Checkpointing & Exactly-Once", detail: "Configure RocksDB state backend with incremental checkpoints to S3 and two-phase commit (2PC) sinks." }
          ],
          optimal_approach: "Kafka CDC + Apache Flink Temporal Table Join with event-time watermarks and RocksDB state backend.",
          code_blueprint: `from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

env = StreamExecutionEnvironment.get_execution_environment()
env.enable_checkpointing(10000) # 10s checkpoint
t_env = StreamTableEnvironment.create(env)

t_env.execute_sql("""
CREATE TABLE orders (
    order_id STRING,
    user_id STRING,
    amount DECIMAL(10, 2),
    order_time TIMESTAMP(3),
    WATERMARK FOR order_time AS order_time - INTERVAL '5' SECOND
) WITH ('connector' = 'kafka', 'topic' = 'orders_cdc', 'format' = 'json');
""")`,
          common_pitfalls: ["Using processing time instead of event time causing out-of-order corruption.", "Not tuning RocksDB memory, triggering JVM OOM."]
        },
        where: {
          platform: "Apache Flink Blueprint",
          url: "https://flink.apache.org/",
          mnc_companies: ["Uber", "Netflix", "Databricks", "Stripe", "LinkedIn", "ByteDance"],
          recommended_tools: "PyFlink / Kafka / Docker"
        },
        when: {
          recommended_time: "Afternoon (02:00 PM – 02:25 PM) — Streaming pipeline design",
          duration_minutes: 25,
          sprint_phase: "Day 1 of 14: Real-Time Stream Processing"
        },
        proof_criteria: {
          deliverable: "Stream-Table join architecture diagram and Flink SQL schema.",
          verification_method: "Vireoniq Design Twin"
        }
      },
      {
        task_id: "de-3",
        title: "Draft STAR Story on Resolving Silent Data Drift & Pipeline Schema Breaks in Production",
        task_type: "BEHAVIORAL_STAR",
        estimated_minutes: 15,
        projected_delta: "+0.8",
        status: "COMPLETED",
        difficulty: "Crucial • Data Governance Loop",
        why: "Validates proactive observability, Great Expectations schema contracts, and stakeholder communication during critical data corruption.",
        how: {
          steps: [
            { phase: "Minute 0–3: Situation", detail: "Upstream team altered payment payload types without warning, corrupting 1.8M daily revenue analytics rows." },
            { phase: "Minute 3–7: Task", detail: "Reconcile financial records with payment gateways within 4 hours before board financial closing." },
            { phase: "Minute 7–11: Action", detail: "Quarantined tainted data, ran PySpark backfill comparing raw Stripe webhooks, and enforced Great Expectations schema CI checks." },
            { phase: "Minute 11–15: Result", detail: "Zero financial reporting errors; automated schema registry prevented 14 subsequent breaking changes." }
          ],
          optimal_approach: "Proactive isolation -> Targeted backfill -> Automated schema registry enforcement.",
          code_blueprint: `Situation: Upstream team altered payment payload types without warning, corrupting 1.8M daily revenue analytics rows.
Task: Reconcile financial records with payment gateways within 4 hours before board financial closing.
Action: Quarantined tainted data, ran PySpark backfill comparing raw Stripe webhooks, and enforced Great Expectations schema CI checks.
Result: Zero financial reporting errors; automated schema registry prevented 14 subsequent breaking changes.`,
          common_pitfalls: ["Failing to mention quarantine/circuit-breaker steps.", "Focusing only on the technical SQL fix rather than governance preventative measures."]
        },
        where: {
          platform: "Vireoniq Leadership Simulator",
          url: "/app/interview-simulator",
          mnc_companies: ["Snowflake", "Stripe", "Amazon", "Goldman Sachs", "Meta"],
          recommended_tools: "Vireoniq Voice Simulator"
        },
        when: {
          recommended_time: "Evening (05:00 PM – 05:15 PM) — Data governance reflection",
          duration_minutes: 15,
          sprint_phase: "Day 1 of 14: Data Quality & Governance"
        },
        proof_criteria: {
          deliverable: "4-part STAR writeup detailing root cause, quarantine, and schema registry prevention.",
          verification_method: "Automated AI rubric"
        }
      }
    ]
  },

  "DevOps / SRE": {
    mission_date: todayDate,
    target_role: "DevOps / SRE",
    active_plan_title: "14-Day DevOps / SRE Accelerated Readiness Sprints",
    rationale: "Eliminating bottlenecks in Kubernetes pod autoscaling, chaos resilience, zero-downtime Canary rollouts & SLO alerting.",
    tasks_count: 3,
    total_estimated_minutes: 70,
    progress_pct: 35,
    tasks: [
      {
        task_id: "devops-1",
        title: "Solve LeetCode #76: Minimum Window Substring (Two-Pointer Frequency Vector)",
        task_type: "CODING_DRILL",
        estimated_minutes: 30,
        projected_delta: "+1.4",
        status: "PENDING",
        difficulty: "Hard • Algorithmic Core",
        why: "Evaluates sliding window expansion and contraction with character frequency map.",
        how: {
          steps: [
            { phase: "Minute 0–7: Boundaries", detail: "Maintain target map of required characters. Expand right pointer until window contains all required chars." },
            { phase: "Minute 7–20: Contract Left", detail: "Once valid, shrink left pointer to find minimum window size, updating best result when valid." },
            { phase: "Minute 20–30: O(N) Invariant", detail: "Both left and right traverse string at most once. Time complexity is strictly O(N)." }
          ],
          optimal_approach: "Two Pointers sliding window with matched character counter. O(N) Time, O(Alphabet) Space.",
          code_blueprint: `from collections import Counter
def minWindow(s: str, t: str) -> str:
    if not t or not s: return ''
    need = Counter(t)
    missing = len(t)
    start, end = 0, 0
    i = 0
    for j, char in enumerate(s, 1):
        if need[char] > 0: missing -= 1
        need[char] -= 1
        if missing == 0:
            while i < j and need[s[i]] < 0:
                need[s[i]] += 1
                i += 1
            if not end or j - i <= end - start:
                start, end = i, j
            need[s[i]] += 1
            missing += 1
            i += 1
    return s[start:end]`,
          common_pitfalls: ["Comparing entire dictionary at each step instead of maintaining integer match count."]
        },
        where: {
          platform: "LeetCode #76",
          url: "https://leetcode.com/problems/minimum-window-substring/",
          mnc_companies: ["Google", "Meta", "Amazon", "Apple", "Uber"],
          recommended_tools: "LeetCode / Python"
        },
        when: {
          recommended_time: "Morning (09:00 AM – 09:30 AM) — Core algorithmic sprint",
          duration_minutes: 30,
          sprint_phase: "Day 1 of 14: Algorithmic Efficiency"
        },
        proof_criteria: {
          deliverable: "Accepted LeetCode submission passing all test cases in O(N) time.",
          verification_method: "Vireoniq Coding Studio"
        }
      },
      {
        task_id: "devops-2",
        title: "Architect Kubernetes Multi-Region Disaster Recovery with GitOps (ArgoCD & Vault)",
        task_type: "SYSTEM_DESIGN",
        estimated_minutes: 25,
        projected_delta: "+1.3",
        status: "PENDING",
        difficulty: "Advanced • Cloud Infrastructure",
        why: "Demonstrates multi-cluster synchronization, secret rotation, and active-passive failover.",
        how: {
          steps: [
            { phase: "Minute 0–7: GitOps Declarative Ingress", detail: "Use ArgoCD ApplicationSets to synchronize manifest definitions across Primary and Secondary clusters." },
            { phase: "Minute 7–16: Secret Management", detail: "External Secrets Operator syncing dynamic database credentials from HashiCorp Vault without hardcoded secrets in Git." },
            { phase: "Minute 16–25: Failover Healthchecks", detail: "Configure Route 53 DNS failover healthchecks with automated DNS record propagation within 60 seconds." }
          ],
          optimal_approach: "ArgoCD ApplicationSets + External Secrets Operator + Route 53 latency DNS failover.",
          code_blueprint: `apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: production-workloads
spec:
  generators:
  - list:
      elements:
      - cluster: us-east-1
        url: https://k8s-useast1.vireoniq.internal
      - cluster: eu-west-1
        url: https://k8s-euwest1.vireoniq.internal`,
          common_pitfalls: ["Storing plaintext secrets in Git.", "Not verifying stateful volume backup replication."]
        },
        where: {
          platform: "Kubernetes Sandbox",
          url: "https://argo-cd.readthedocs.io/",
          mnc_companies: ["Netflix", "Datadog", "AWS", "Google Cloud", "Atlassian"],
          recommended_tools: "kubectl / Helm / ArgoCD"
        },
        when: {
          recommended_time: "Afternoon (02:00 PM – 02:25 PM) — GitOps infrastructure design",
          duration_minutes: 25,
          sprint_phase: "Day 1 of 14: Disaster Recovery & High Availability"
        },
        proof_criteria: {
          deliverable: "ArgoCD ApplicationSet manifest and architecture topology diagram.",
          verification_method: "Vireoniq Design Twin"
        }
      },
      {
        task_id: "devops-3",
        title: "Draft STAR Story on Leading Root Cause Analysis (RCA) After Major Cloud Outage",
        task_type: "BEHAVIORAL_STAR",
        estimated_minutes: 15,
        projected_delta: "+0.8",
        status: "COMPLETED",
        difficulty: "Critical • Incident Commander Loop",
        why: "Validates psychological safety, blameless post-mortem ownership, and preventative architectural controls.",
        how: {
          steps: [
            { phase: "Minute 0–3: Situation", detail: "Major cloud network partition triggered split-brain condition across Kubernetes cluster affecting 200K active users." },
            { phase: "Minute 3–7: Task", detail: "Assume role of Incident Commander, coordinate SREs, contain outage, and chair post-mortem." },
            { phase: "Minute 7–11: Action", detail: "Executed cutover to disaster recovery region, stabilized core services within 18 minutes, added PodDisruptionBudgets." },
            { phase: "Minute 11–15: Result", detail: "Met 99.95% annual availability target; RCA template adopted across all 12 platform engineering teams." }
          ],
          optimal_approach: "Incident Command -> Rapid Containment -> Blameless RCA -> Structural Anti-Fragility.",
          code_blueprint: `Situation: A regional cloud network partition triggered split-brain condition across our Kubernetes cluster, affecting 200K active users.
Task: Assume role of Incident Commander, coordinate SREs, contain outage, and chair the subsequent post-mortem.
Action: Executed traffic cutover to disaster recovery region, stabilized core services within 18 minutes, and added automated PodDisruptionBudgets.
Result: Met 99.95% annual availability target; our RCA template was adopted across all 12 platform engineering teams.`,
          common_pitfalls: ["Assigning individual blame.", "Not specifying quantifiable MTTA / MTTR improvements."]
        },
        where: {
          platform: "Vireoniq Leadership Simulator",
          url: "/app/interview-simulator",
          mnc_companies: ["Google", "Amazon", "Netflix", "Datadog", "Cloudflare"],
          recommended_tools: "Vireoniq Voice Simulator"
        },
        when: {
          recommended_time: "Evening (05:00 PM – 05:15 PM) — SRE incident rehearsal",
          duration_minutes: 15,
          sprint_phase: "Day 1 of 14: Incident Management & SRE Culture"
        },
        proof_criteria: {
          deliverable: "Structured blameless post-mortem document with 5-whys root cause analysis.",
          verification_method: "Automated AI rubric"
        }
      }
    ]
  },

  "Cloud Architect": {
    mission_date: todayDate,
    target_role: "Cloud Architect",
    active_plan_title: "14-Day Cloud Architect Accelerated Readiness Sprints",
    rationale: "Eliminating bottlenecks in multi-region active-active VPC peering, transit gateways & zero-trust IAM least-privilege architecture.",
    tasks_count: 3,
    total_estimated_minutes: 65,
    progress_pct: 35,
    tasks: [
      {
        task_id: "cloud-1",
        title: "Solve LeetCode #207: Course Schedule (Graph Cycle & Kahn's Topological Sort)",
        task_type: "CODING_DRILL",
        estimated_minutes: 25,
        projected_delta: "+1.2",
        status: "PENDING",
        difficulty: "Medium • Dependency DAG Resolution",
        why: "Validates in-degree graph modeling and dependency graph cycle detection critical for cloud provisioning DAGs.",
        how: {
          steps: [
            { phase: "Minute 0–5: Graph Modeling", detail: "Represent courses as nodes and prerequisites as directed edges. Cycle implies impossible schedule." },
            { phase: "Minute 5–15: Kahn's Algorithm", detail: "Compute in-degrees of all nodes. Push all in-degree 0 nodes to queue. Decrement child in-degrees when popped." },
            { phase: "Minute 15–25: Cycle Validation", detail: "If processed node count equals total courses, valid DAG exists. Otherwise cycle detected. Time: O(V + E)." }
          ],
          optimal_approach: "Kahn's algorithm using in-degree array and BFS queue. O(V + E) Time, O(V + E) Space.",
          code_blueprint: `from collections import deque, defaultdict
def canFinish(numCourses: int, prerequisites: list[list[int]]) -> bool:
    adj = defaultdict(list)
    in_degree = [0] * numCourses
    for dest, src in prerequisites:
        adj[src].append(dest)
        in_degree[dest] += 1
    q = deque([i for i in range(numCourses) if in_degree[i] == 0])
    visited = 0
    while q:
        curr = q.popleft()
        visited += 1
        for neighbor in adj[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                q.append(neighbor)
    return visited == numCourses`,
          common_pitfalls: ["Reversing edge directions.", "Using DFS without 3-state coloring leading to infinite loops."]
        },
        where: {
          platform: "LeetCode #207",
          url: "https://leetcode.com/problems/course-schedule/",
          mnc_companies: ["Amazon", "Google", "Microsoft", "Uber", "Palantir"],
          recommended_tools: "LeetCode / Python"
        },
        when: {
          recommended_time: "Morning (09:00 AM – 09:25 AM) — Graph DAG sprint",
          duration_minutes: 25,
          sprint_phase: "Day 1 of 14: Directed Graph Modeling"
        },
        proof_criteria: {
          deliverable: "Accepted LeetCode submission passing all test cases.",
          verification_method: "MNC Coding Studio"
        }
      },
      {
        task_id: "cloud-2",
        title: "Architect Multi-Tenant Multi-Region Active-Active Cloud Mesh on AWS/GCP",
        task_type: "SYSTEM_DESIGN",
        estimated_minutes: 25,
        projected_delta: "+1.5",
        status: "PENDING",
        difficulty: "Principal • Global Infrastructure",
        why: "Architects low-latency cross-region replication (Route 53 latency routing, DynamoDB global tables, CDN edge compute).",
        how: {
          steps: [
            { phase: "Minute 0–7: Global Ingress Routing", detail: "AWS Route 53 Latency-Based Routing with CloudFront CDN edge caching and AWS Global Accelerator." },
            { phase: "Minute 7–16: Data Layer Consistency", detail: "DynamoDB Global Tables for multi-region writes with conflict resolution based on last-writer-wins." },
            { phase: "Minute 16–25: Inter-Region Networking", detail: "AWS Transit Gateway with inter-region peering over dedicated AWS private backbone, bypassing public internet." }
          ],
          optimal_approach: "Route 53 Geolocation/Latency + DynamoDB Global Tables + Transit Gateway private mesh.",
          code_blueprint: `# Terraform AWS Transit Gateway Peering
resource "aws_ec2_transit_gateway_peering_attachment" "us_to_eu" {
  transit_gateway_id      = aws_ec2_transit_gateway.useast1.id
  peer_transit_gateway_id = aws_ec2_transit_gateway.euwest1.id
  peer_region             = "eu-west-1"
  tags = { Name = "tgw-peering-useast1-euwest1" }
}`,
          common_pitfalls: ["Overlooking cross-region data transfer egress costs.", "Assuming synchronous ACID transactions across 80ms transatlantic latency."]
        },
        where: {
          platform: "AWS Architecture Sandbox",
          url: "https://aws.amazon.com/architecture/",
          mnc_companies: ["Amazon Web Services", "Google Cloud", "Microsoft Azure", "Salesforce", "Snowflake"],
          recommended_tools: "Terraform / Draw.io / AWS Architecture Center"
        },
        when: {
          recommended_time: "Afternoon (02:00 PM – 02:25 PM) — Multi-region system design",
          duration_minutes: 25,
          sprint_phase: "Day 1 of 14: High Availability Architecture"
        },
        proof_criteria: {
          deliverable: "Multi-region architecture diagram with Route 53, Transit Gateway, and global data sync topology.",
          verification_method: "Vireoniq Design Twin"
        }
      },
      {
        task_id: "cloud-3",
        title: "Draft STAR Story on Driving Cloud Migration from On-Premises with 99.999% Availability",
        task_type: "BEHAVIORAL_STAR",
        estimated_minutes: 15,
        projected_delta: "+0.8",
        status: "COMPLETED",
        difficulty: "Executive • Transformation Loop",
        why: "Communicates executive stakeholder alignment, risk mitigation, and legacy decoupling without operational disruption.",
        how: {
          steps: [
            { phase: "Minute 0–3: Situation", detail: "Expiring data center leases required migrating 80 enterprise services to AWS within 6 months with zero downtime." },
            { phase: "Minute 3–7: Task", detail: "Serve as Lead Cloud Architect, establish multi-phase migration architecture, and guide 5 engineering teams." },
            { phase: "Minute 7–11: Action", detail: "Deployed AWS Direct Connect with Strangler Fig routing; piloted non-critical reporting before migrating primary transactional databases." },
            { phase: "Minute 11–15: Result", detail: "Cutover completed 3 weeks ahead of schedule with 99.999% availability, reducing infrastructure TCO by 34% ($2.1M/year)." }
          ],
          optimal_approach: "Strangler Fig Pattern + Executive alignment + Risk-tiered migration phasing.",
          code_blueprint: `Situation: Expiring data center leases required migrating 80 enterprise services to AWS within 6 months with zero downtime.
Task: Serve as Lead Cloud Architect, establish the multi-phase migration architecture, and guide 5 engineering teams through cutover.
Action: Deployed AWS Direct Connect with Strangler Fig routing; piloted non-critical reporting before migrating primary transactional databases.
Result: Cutover completed 3 weeks ahead of schedule with 99.999% availability, reducing infrastructure TCO by 34% ($2.1M/year).`,
          common_pitfalls: ["Advocating for a 'big bang' cutover instead of phased strangler fig decoupling.", "Failing to discuss risk management and rollback readiness."]
        },
        where: {
          platform: "Vireoniq Leadership Simulator",
          url: "/app/interview-simulator",
          mnc_companies: ["Amazon", "Microsoft", "Goldman Sachs", "JPMorgan", "Oracle"],
          recommended_tools: "Vireoniq Voice Simulator"
        },
        when: {
          recommended_time: "Evening (05:00 PM – 05:15 PM) — Executive communication",
          duration_minutes: 15,
          sprint_phase: "Day 1 of 14: Cloud Governance & Transformation"
        },
        proof_criteria: {
          deliverable: "Executive STAR narrative with audited downtime and TCO metrics.",
          verification_method: "Automated AI rubric"
        }
      }
    ]
  },

  "Mobile Engineer": {
    mission_date: todayDate,
    target_role: "Mobile Engineer",
    active_plan_title: "14-Day Mobile Engineer Accelerated Readiness Sprints",
    rationale: "Eliminating bottlenecks in 60 FPS frame render threads, offline SQLite reconciliation, biometrics & memory leak profiles.",
    tasks_count: 3,
    total_estimated_minutes: 65,
    progress_pct: 35,
    tasks: [
      {
        task_id: "mobile-1",
        title: "Solve LeetCode #206: Reverse Linked List & Deep Clone of Graph (Pointers)",
        task_type: "CODING_DRILL",
        estimated_minutes: 25,
        projected_delta: "+1.1",
        status: "PENDING",
        difficulty: "Medium • Memory Lifecycle & Pointers",
        why: "Ensures deep understanding of in-memory object references and cyclic graph traversal.",
        how: {
          steps: [
            { phase: "Minute 0–5: Pointer Invariants", detail: "Maintain prev, curr, and next_temp pointers. Avoid memory leaks or cyclic references." },
            { phase: "Minute 5–15: In-Place Reversal", detail: "Save curr.next, point curr.next = prev, advance prev = curr, advance curr = next_temp." },
            { phase: "Minute 15–25: Edge Cases", detail: "Test empty list, single node, two nodes. Confirm O(N) time and O(1) space complexity." }
          ],
          optimal_approach: "Iterative three-pointer in-place reversal. O(N) Time, O(1) Space.",
          code_blueprint: `class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverseList(head: ListNode | None) -> ListNode | None:
    prev = None
    curr = head
    while curr:
        next_temp = curr.next
        curr.next = prev
        prev = curr
        curr = next_temp
    return prev`,
          common_pitfalls: ["Losing reference to curr.next before updating pointer.", "Using recursion which risks stack overflow on 10,000+ lists."]
        },
        where: {
          platform: "LeetCode #206",
          url: "https://leetcode.com/problems/reverse-linked-list/",
          mnc_companies: ["Apple", "Google", "Meta", "Uber", "Spotify"],
          recommended_tools: "LeetCode / Swift / Kotlin / Python"
        },
        when: {
          recommended_time: "Morning (09:00 AM – 09:25 AM) — Pointer mechanics sprint",
          duration_minutes: 25,
          sprint_phase: "Day 1 of 14: In-Memory Pointer Manipulation"
        },
        proof_criteria: {
          deliverable: "Accepted LeetCode submission passing all test cases in O(1) space.",
          verification_method: "Vireoniq Coding Studio"
        }
      },
      {
        task_id: "mobile-2",
        title: "Architect Offline-First Mobile Storage with SQLite/Room, Background Sync & WorkManager",
        task_type: "SYSTEM_DESIGN",
        estimated_minutes: 25,
        projected_delta: "+1.3",
        status: "PENDING",
        difficulty: "Senior • Mobile Architecture",
        why: "Designs resilient offline mutation queues, optimistic UI sync, and backpressure retry handling.",
        how: {
          steps: [
            { phase: "Minute 0–7: Entity Design", detail: "Room/CoreData schema with sync_status ('SYNCED', 'PENDING_UPLOAD', 'CONFLICT') and client timestamp." },
            { phase: "Minute 7–16: Background Queue", detail: "Schedule WorkManager/BGAppRefreshTask with network constraints (CONNECTED, UNMETERED)." },
            { phase: "Minute 16–25: Backoff & Reconciliation", detail: "Implement exponential backoff with jitter on network failure; resolve server conflicts via client revision IDs." }
          ],
          optimal_approach: "Repository Pattern with Room/CoreData Single Source of Truth + WorkManager background sync.",
          code_blueprint: `// Kotlin Room + Coroutines Offline Repository
class OfflineFirstRepository(
    private val localDao: ItemDao,
    private val api: RemoteApi
) {
    val items: Flow<List<ItemEntity>> = localDao.getAllItems()

    suspend fun createItemOptimistic(item: ItemEntity) {
        localDao.insert(item.copy(syncStatus = SyncStatus.PENDING))
        enqueueSyncWork()
    }
}`,
          common_pitfalls: ["Updating remote server directly without updating local database first.", "Running heavy database operations on main thread causing ANRs."]
        },
        where: {
          platform: "Mobile Architecture Sandbox",
          url: "https://developer.android.com/topic/architecture/data-layer/offline-first",
          mnc_companies: ["Uber", "Instagram", "WhatsApp", "Duolingo", "DoorDash"],
          recommended_tools: "Android Studio / Xcode / Room / CoreData"
        },
        when: {
          recommended_time: "Afternoon (02:00 PM – 02:25 PM) — Offline mobile design",
          duration_minutes: 25,
          sprint_phase: "Day 1 of 14: Offline-First Architecture"
        },
        proof_criteria: {
          deliverable: "Offline repository sync sequence diagram and entity schema.",
          verification_method: "Vireoniq Design Twin"
        }
      },
      {
        task_id: "mobile-3",
        title: "Draft STAR Story on Profiling & Eliminating 60 FPS Frame Drops on Low-End Devices",
        task_type: "BEHAVIORAL_STAR",
        estimated_minutes: 15,
        projected_delta: "+0.8",
        status: "COMPLETED",
        difficulty: "Critical • Mobile Performance",
        why: "Demonstrates Android Profiler / Xcode Instruments proficiency, offloading heavy calculations from main thread.",
        how: {
          steps: [
            { phase: "Minute 0–3: Situation", detail: "App frame rates dropped to 24 FPS during feed scrolling on budget devices, resulting in a wave of 1-star reviews." },
            { phase: "Minute 3–7: Task", detail: "Diagnose rendering bottlenecks and restore silky 60 FPS scrolling across all supported device tiers." },
            { phase: "Minute 7–11: Action", detail: "Profiled with Android GPU Profiler; identified excessive layout overdraw and synchronous image resizing on main thread; moved work to background coroutines." },
            { phase: "Minute 11–15: Result", detail: "Frame drop rate plummeted from 18% to 1.2%, maintaining steady 60 FPS; Play Store rating climbed to 4.7 stars." }
          ],
          optimal_approach: "Tool-driven profiling (Systrace/Instruments) -> View hierarchy flattening -> Off-main-thread image decoding.",
          code_blueprint: `Situation: App frame rates dropped to 24 FPS during feed scrolling on budget devices, resulting in a wave of 1-star reviews.
Task: Diagnose rendering bottlenecks and restore silky 60 FPS scrolling across all supported device tiers.
Action: Profiled with Android GPU Profiler; identified excessive layout overdraw and synchronous image resizing on main thread; migrated image processing to Dispatchers.Default and flattened XML hierarchy.
Result: Frame drop rate plummeted from 18% to 1.2%, maintaining steady 60 FPS; Play Store rating climbed to 4.7 stars.`,
          common_pitfalls: ["Guessing where lag comes from instead of using Systrace or Instruments.", "Not mentioning specific hardware device tiers."]
        },
        where: {
          platform: "Vireoniq Leadership Simulator",
          url: "/app/interview-simulator",
          mnc_companies: ["Google", "Meta", "ByteDance", "Snap", "Spotify"],
          recommended_tools: "Vireoniq Voice Simulator"
        },
        when: {
          recommended_time: "Evening (05:00 PM – 05:15 PM) — Performance engineering reflection",
          duration_minutes: 15,
          sprint_phase: "Day 1 of 14: Mobile Performance Optimization"
        },
        proof_criteria: {
          deliverable: "Structured STAR performance report with frame rate telemetry before/after.",
          verification_method: "Automated AI rubric"
        }
      }
    ]
  },

  "Cybersecurity Engineer": {
    mission_date: todayDate,
    target_role: "Cybersecurity Engineer",
    active_plan_title: "14-Day Cybersecurity Engineer Accelerated Readiness Sprints",
    rationale: "Eliminating bottlenecks in zero-trust mTLS authorization, OAuth2 PKCE replay defense & automated SAST/DAST vuln triage.",
    tasks_count: 3,
    total_estimated_minutes: 65,
    progress_pct: 35,
    tasks: [
      {
        task_id: "cyber-1",
        title: "Solve LeetCode #227: Basic Calculator II (Expression Parsing & Input Sanitization)",
        task_type: "CODING_DRILL",
        estimated_minutes: 25,
        projected_delta: "+1.2",
        status: "PENDING",
        difficulty: "Medium • Input Validation & Grammar",
        why: "Tests stack parsing without eval(), preventing remote code execution (RCE) vulnerabilities.",
        how: {
          steps: [
            { phase: "Minute 0–5: Operator Precedence", detail: "Multiplication and division have higher precedence. Use stack to evaluate immediate * and / operations." },
            { phase: "Minute 5–15: Stack Evaluation", detail: "Iterate through string. For '+', push num. For '-', push -num. For '*' or '/', pop top, evaluate with current num, push result back." },
            { phase: "Minute 15–25: Final Summation", detail: "Sum all elements in stack. Pure O(N) time and O(N) space." }
          ],
          optimal_approach: "Stack-based operator precedence parser without dangerous eval() execution.",
          code_blueprint: `def calculate(s: str) -> int:
    stack = []
    num = 0
    sign = '+'
    for i, c in enumerate(s):
        if c.isdigit(): num = num * 10 + int(c)
        if c in '+-*/' or i == len(s) - 1:
            if sign == '+': stack.append(num)
            elif sign == '-': stack.append(-num)
            elif sign == '*': stack.append(stack.pop() * num)
            elif sign == '/': stack.append(int(stack.pop() / num))
            sign = c
            num = 0
    return sum(stack)`,
          common_pitfalls: ["Using eval() which is an instant security vulnerability.", "Truncating negative division incorrectly in Python (use int(a/b))."]
        },
        where: {
          platform: "LeetCode #227",
          url: "https://leetcode.com/problems/basic-calculator-ii/",
          mnc_companies: ["CrowdStrike", "Palo Alto Networks", "Cloudflare", "Google", "Amazon"],
          recommended_tools: "LeetCode / Python"
        },
        when: {
          recommended_time: "Morning (09:00 AM – 09:25 AM) — Parsing & input sanitization",
          duration_minutes: 25,
          sprint_phase: "Day 1 of 14: Secure Input Parsing"
        },
        proof_criteria: {
          deliverable: "Accepted LeetCode submission without eval() usage.",
          verification_method: "Vireoniq Coding Studio"
        }
      },
      {
        task_id: "cyber-2",
        title: "Architect Zero-Trust Micro-Segmentation & Mutual TLS (mTLS) with SPIFFE/SPIRE",
        task_type: "SYSTEM_DESIGN",
        estimated_minutes: 25,
        projected_delta: "+1.4",
        status: "PENDING",
        difficulty: "Advanced • Zero-Trust Security",
        why: "Enforces cryptographically verifiable workload identities, dynamic X.509 certificate rotation, and egress filtering.",
        how: {
          steps: [
            { phase: "Minute 0–7: SPIFFE ID Attestation", detail: "Issue cryptographically verified SPIFFE IDs based on node and pod attestation." },
            { phase: "Minute 7–16: Automated mTLS Rotation", detail: "Envoy sidecars establish mutual TLS using ephemeral X.509 SVIDs rotated every 60 minutes with zero downtime." },
            { phase: "Minute 16–25: L7 Authorization Policies", detail: "Enforce strict deny-by-default Istio AuthorizationPolicy matching client SPIFFE IDs and specific REST verbs." }
          ],
          optimal_approach: "SPIRE Workload Attestor + Envoy Sidecar mTLS + Deny-All Istio Authorization Policies.",
          code_blueprint: `apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: payment-access-control
  namespace: production
spec:
  selector:
    matchLabels:
      app: payment-service
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/production/sa/checkout-service-account"]
    to:
    - operation:
        methods: ["POST"]
        paths: ["/api/v1/charge"]`,
          common_pitfalls: ["Relying on network perimeter firewalls instead of cryptographic workload identity.", "Allowing long-lived root certificates without automated rotation."]
        },
        where: {
          platform: "Zero-Trust Sandbox",
          url: "https://spiffe.io/",
          mnc_companies: ["Cloudflare", "CrowdStrike", "Google", "Amazon", "Palo Alto Networks"],
          recommended_tools: "SPIFFE / SPIRE / Envoy / Istio"
        },
        when: {
          recommended_time: "Afternoon (02:00 PM – 02:25 PM) — Zero-trust system design",
          duration_minutes: 25,
          sprint_phase: "Day 1 of 14: Workload Identity & Cryptography"
        },
        proof_criteria: {
          deliverable: "mTLS handshake sequence diagram and Istio AuthorizationPolicy YAML.",
          verification_method: "Vireoniq Design Twin"
        }
      },
      {
        task_id: "cyber-3",
        title: "Draft STAR Story on Triage and Remediation of Zero-Day RCE Vulnerability in Production",
        task_type: "BEHAVIORAL_STAR",
        estimated_minutes: 15,
        projected_delta: "+0.8",
        status: "COMPLETED",
        difficulty: "Critical • SecOps / Incident Response",
        why: "Highlights containment speed, ethical disclosure, customer impact assessment, and automated hotfix patching.",
        how: {
          steps: [
            { phase: "Minute 0–3: Situation", detail: "Critical zero-day RCE disclosed publicly, with exploit attempts hitting ingress API within 45 minutes." },
            { phase: "Minute 3–7: Task", detail: "Contain threat immediately across 600 container workloads and deploy patched binaries with zero downtime." },
            { phase: "Minute 7–11: Action", detail: "Deployed emergency WAF filter blocking malicious exploit payloads at the edge; generated automated SBOM diffs; deployed patched images via CI." },
            { phase: "Minute 11–15: Result", detail: "100% of attack probes blocked at perimeter; complete cluster remediation verified within 4 hours with zero customer data exposure." }
          ],
          optimal_approach: "Edge WAF virtual patching -> SBOM dependency audit -> Immutable container image replacement.",
          code_blueprint: `Situation: Critical zero-day RCE (CVSS 10.0) announced publicly, with exploit attempts hitting our ingress API within 45 minutes.
Task: Contain threat immediately across 600 container workloads and deploy patched binaries with zero downtime.
Action: Deployed an emergency WAF filter blocking malicious exploit payloads at the edge; generated automated SBOM diffs to identify vulnerable libraries; deployed patched images via CI.
Result: 100% of attack probes blocked at perimeter; complete cluster remediation verified within 4 hours with zero customer data exposure.`,
          common_pitfalls: ["Waiting for full binary rebuild before deploying virtual patch at WAF edge.", "Failing to conduct post-incident forensic log audits."]
        },
        where: {
          platform: "Vireoniq Leadership Simulator",
          url: "/app/interview-simulator",
          mnc_companies: ["CrowdStrike", "Mandiant", "Google Security", "Cloudflare", "Microsoft"],
          recommended_tools: "Vireoniq Voice Simulator"
        },
        when: {
          recommended_time: "Evening (05:00 PM – 05:15 PM) — Incident response reflection",
          duration_minutes: 15,
          sprint_phase: "Day 1 of 14: Vulnerability Response"
        },
        proof_criteria: {
          deliverable: "Structured STAR incident writeup with CVSS triage and edge mitigation steps.",
          verification_method: "Automated AI rubric"
        }
      }
    ]
  }
};

export const ROLE_MISSIONS_ALT: Record<string, DailyMissionData> = {
  "AI/ML Engineer": {
    mission_date: todayDate,
    target_role: "AI/ML Engineer",
    active_plan_title: "14-Day AI/ML Engineer Accelerated Readiness Sprints (Set B)",
    rationale: "Targeting speculative decoding, monotonic queue optimization & high-throughput vector retrieval.",
    tasks_count: 3,
    total_estimated_minutes: 70,
    progress_pct: 42,
    tasks: [
      {
        task_id: "aiml-alt-1",
        title: "Solve LeetCode #239: Sliding Window Maximum (Monotonic Deque O(N))",
        task_type: "CODING_DRILL",
        estimated_minutes: 30,
        projected_delta: "+1.4",
        status: "PENDING",
        difficulty: "Hard • Big Tech Bar Raiser",
        why: "Crucial for streaming window tokenization and real-time tensor feature aggregations.",
        how: {
          steps: [
            { phase: "Minute 0–7: Invariant", detail: "Maintain double-ended queue storing indices in decreasing order of values. Front of deque is always window maximum." },
            { phase: "Minute 7–18: Pruning", detail: "Pop elements from back smaller than current num. Pop front if index < i - k + 1." },
            { phase: "Minute 18–30: Collection", detail: "Append nums[deque[0]] to results once index i >= k - 1. Time complexity strictly O(N)." }
          ],
          optimal_approach: "Monotonic Decreasing Deque storing indices. O(N) Time, O(k) Space.",
          code_blueprint: `from collections import deque
def maxSlidingWindow(nums: list[int], k: int) -> list[int]:
    q = deque()
    res = []
    for i, n in enumerate(nums):
        while q and nums[q[-1]] < n:
            q.pop()
        q.append(i)
        if q[0] < i - k + 1:
            q.popleft()
        if i >= k - 1:
            res.append(nums[q[0]])
    return res`,
          common_pitfalls: ["Storing values instead of indices in deque.", "Using heap taking O(N log k) instead of O(N)."]
        },
        where: {
          platform: "LeetCode #239",
          url: "https://leetcode.com/problems/sliding-window-maximum/",
          mnc_companies: ["Google", "Amazon", "Meta", "ByteDance", "Uber"],
          recommended_tools: "LeetCode / VS Code"
        },
        when: {
          recommended_time: "Morning (09:00 AM – 09:30 AM) — Monotonic deque drill",
          duration_minutes: 30,
          sprint_phase: "Day 2 of 14: Monotonic Data Structures"
        },
        proof_criteria: {
          deliverable: "Accepted LeetCode submission passing all 51 test cases with O(N) time.",
          verification_method: "Submit link in MNC Coding Studio"
        }
      },
      {
        task_id: "aiml-alt-2",
        title: "Architect Real-Time Vector Similarity Search Retrieval with Qdrant & HNSW",
        task_type: "SYSTEM_DESIGN",
        estimated_minutes: 25,
        projected_delta: "+1.5",
        status: "PENDING",
        difficulty: "Senior Level • Vector DB Core",
        why: "Core requirement for Tier-1 generative AI and semantic retrieval pipelines at OpenAI, Meta, and Databricks.",
        how: {
          steps: [
            { phase: "Minute 0–7: Approximate Nearest Neighbors", detail: "Evaluate HNSW graph vs IVF-PQ trade-offs for 1536-dim embeddings." },
            { phase: "Minute 7–16: Quantization", detail: "Implement scalar quantization (SQ) reducing memory by 4x. Configure boolean metadata filtering." },
            { phase: "Minute 16–25: Clustering", detail: "Design distributed cluster with raft consensus, write-ahead logs (WAL), and sub-10ms recall p99 SLA." }
          ],
          optimal_approach: "Qdrant HNSW graph index with Scalar Quantization and distributed read replicas.",
          code_blueprint: `from qdrant_client import QdrantClient
from qdrant_client.http import models

client = QdrantClient("http://localhost:6333")
client.create_collection(
    collection_name="doc_embeddings",
    vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
    hnsw_config=models.HnswConfigDiff(m=16, ef_construct=100)
)`,
          common_pitfalls: ["Not setting ef_search appropriately.", "OOM crashes from holding full unquantized vectors in RAM."]
        },
        where: {
          platform: "Qdrant Vector Engine",
          url: "https://qdrant.tech/documentation/",
          mnc_companies: ["OpenAI", "Meta", "Databricks", "Microsoft", "Cohere"],
          recommended_tools: "Qdrant / Docker / Python"
        },
        when: {
          recommended_time: "Afternoon (02:00 PM – 02:25 PM) — Vector search engineering",
          duration_minutes: 25,
          sprint_phase: "Day 2 of 14: Semantic Retrieval Pipelines"
        },
        proof_criteria: {
          deliverable: "Working Python Qdrant indexing script with hybrid search filter.",
          verification_method: "Run collection verification test in Vireoniq Lab"
        }
      },
      {
        task_id: "aiml-alt-3",
        title: "Draft STAR Story on Optimizing GPU LLM Inference Latency Under Budget",
        task_type: "BEHAVIORAL_STAR",
        estimated_minutes: 15,
        projected_delta: "+0.7",
        status: "COMPLETED",
        difficulty: "Bar Raiser • Cost & Scale Ownership",
        why: "Demonstrates engineering pragmatism and resource optimization required by tech giants.",
        how: {
          steps: [
            { phase: "Minute 0–4: Situation", detail: "LLM inference p99 latency reached 2.8s during peak customer loads, driving $18K/mo GPU spend." },
            { phase: "Minute 4–8: Task", detail: "Reduce latency to <800ms and reduce cluster spend by 40% ahead of marketing campaign." },
            { phase: "Minute 8–12: Action", detail: "Implemented vLLM engine with continuous batching, KV-cache quantization, and torch.compile optimizations." },
            { phase: "Minute 12–15: Result", detail: "Cut p99 latency to 480ms (82% reduction), slashed GPU instances from 12 to 4, saving $84,000 annually." }
          ],
          optimal_approach: "Concrete benchmark data, trade-off analysis, and verified financial ROI metrics.",
          code_blueprint: `Situation: LLM inference p99 latency reached 2.8s during peak customer loads, driving $18K/mo GPU spend.
Task: Reduce latency to <800ms and reduce cluster spend by 40% ahead of marketing campaign.
Action: Implemented vLLM engine with continuous batching, KV-cache quantization, and torch.compile optimizations.
Result: Cut p99 latency to 480ms (82% reduction), slashed GPU instances from 12 to 4, saving $84,000 annually.`,
          common_pitfalls: ["Claiming 'we optimized it' without explaining specific technical levers.", "Omitting exact cost and latency numbers."]
        },
        where: {
          platform: "Vireoniq Interview Twin Studio",
          url: "/app/interview-simulator",
          mnc_companies: ["Meta", "Google", "Amazon", "Nvidia", "Microsoft"],
          recommended_tools: "Vireoniq Voice Studio"
        },
        when: {
          recommended_time: "Evening (05:00 PM – 05:15 PM) — Behavioral rehearsal",
          duration_minutes: 15,
          sprint_phase: "Day 2 of 14: Executive Communication"
        },
        proof_criteria: {
          deliverable: "Structured STAR written summary with before/after metrics.",
          verification_method: "AI rubric evaluation"
        }
      }
    ]
  },

  "Backend Engineer": {
    mission_date: todayDate,
    target_role: "Backend Engineer",
    active_plan_title: "14-Day Backend Engineer Accelerated Readiness Sprints (Set B)",
    rationale: "Targeting BFS/DFS matrix traversals, distributed rate limiting with Redis Lua & 50K TPS scaling.",
    tasks_count: 3,
    total_estimated_minutes: 65,
    progress_pct: 45,
    tasks: [
      {
        task_id: "be-alt-1",
        title: "Solve LeetCode #200: Number of Islands (BFS/DFS Grid Traversal)",
        task_type: "CODING_DRILL",
        estimated_minutes: 25,
        projected_delta: "+1.2",
        status: "PENDING",
        difficulty: "Medium • Essential Graph/Matrix",
        why: "Standard MNC phone screen benchmark testing 2D matrix exploration without stack overflow.",
        how: {
          steps: [
            { phase: "Minute 0–5: In-Place Marking", detail: "Sink visited land: mutate grid[r][c] = '0' directly to avoid extra memory set." },
            { phase: "Minute 5–15: BFS Queue", detail: "When '1' encountered, increment island count and initiate BFS queue to flood-fill adjacent horizontal/vertical land cells." },
            { phase: "Minute 15–25: Boundary Checks", detail: "Verify 0 <= nr < rows and 0 <= nc < cols before pushing to queue. Complexity: O(M*N) time, O(min(M,N)) space." }
          ],
          optimal_approach: "In-place grid sinking with BFS queue for O(M*N) time and optimal memory usage.",
          code_blueprint: `from collections import deque
def numIslands(grid: list[list[str]]) -> int:
    if not grid: return 0
    rows, cols = len(grid), len(grid[0])
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                count += 1
                q = deque([(r, c)])
                grid[r][c] = '0'
                while q:
                    cr, cc = q.popleft()
                    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == '1':
                            grid[nr][nc] = '0'
                            q.append((nr, nc))
    return count`,
          common_pitfalls: ["Mutating grid after popping instead of before pushing (causes duplicate entries and TLE).", "Checking diagonal directions."]
        },
        where: {
          platform: "LeetCode #200",
          url: "https://leetcode.com/problems/number-of-islands/",
          mnc_companies: ["Amazon", "Microsoft", "Bloomberg", "Google", "Meta"],
          recommended_tools: "LeetCode / Python"
        },
        when: {
          recommended_time: "Morning (09:00 AM – 09:25 AM) — Matrix traversal sprint",
          duration_minutes: 25,
          sprint_phase: "Day 2 of 14: Graph & Matrix Algorithms"
        },
        proof_criteria: {
          deliverable: "Accepted LeetCode submission passing 100% test cases.",
          verification_method: "MNC Coding Studio"
        }
      },
      {
        task_id: "be-alt-2",
        title: "Design Distributed Rate Limiter Using Redis Token Bucket & Lua Script",
        task_type: "SYSTEM_DESIGN",
        estimated_minutes: 25,
        projected_delta: "+1.4",
        status: "PENDING",
        difficulty: "Senior • Distributed Caching",
        why: "Guarantees atomic API throttling without race conditions under 100,000 concurrent requests/sec.",
        how: {
          steps: [
            { phase: "Minute 0–7: Token Bucket Invariants", detail: "Capacity C, refill rate R tokens/sec. Compute replenished tokens dynamically based on timestamp delta." },
            { phase: "Minute 7–16: Redis Lua Atomicity", detail: "Execute read-calculate-write in single atomic Redis EVAL script to completely prevent race conditions." },
            { phase: "Minute 16–25: Headers & Degraded Mode", detail: "Return X-RateLimit-Limit, X-RateLimit-Remaining, and Retry-After headers with graceful in-memory fallback." }
          ],
          optimal_approach: "Redis Token Bucket with single atomic Lua script calculating continuous time elapsed.",
          code_blueprint: `LUA_SCRIPT = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local data = redis.call('HMGET', key, 'tokens', 'last_updated')
local tokens = tonumber(data[1]) or capacity
local last_updated = tonumber(data[2]) or now

local elapsed = math.max(0, now - last_updated)
tokens = math.min(capacity, tokens + (elapsed * refill_rate))

if tokens >= 1 then
    tokens = tokens - 1
    redis.call('HMSET', key, 'tokens', tokens, 'last_updated', now)
    redis.call('EXPIRE', key, 3600)
    return 1
else
    return 0
end
"""`,
          common_pitfalls: ["Calling Redis GET then SET in application code (race condition causes 2x rate limit breach).", "Using fixed window counters which allow double bursts across window boundaries."]
        },
        where: {
          platform: "Distributed Systems Sandbox",
          url: "https://redis.io/docs/manual/patterns/distributed-locks/",
          mnc_companies: ["Stripe", "Cloudflare", "Netflix", "Amazon", "Twitter/X"],
          recommended_tools: "Redis CLI / Python redis-py"
        },
        when: {
          recommended_time: "Afternoon (02:00 PM – 02:25 PM) — API gateway resilience",
          duration_minutes: 25,
          sprint_phase: "Day 2 of 14: Distributed Rate Limiting"
        },
        proof_criteria: {
          deliverable: "Working Lua rate limiting script benchmarked under simulated concurrency.",
          verification_method: "Vireoniq Design Twin"
        }
      },
      {
        task_id: "be-alt-3",
        title: "Draft STAR Story on Scaling API Gateway to 50,000 TPS for Flash Sale",
        task_type: "BEHAVIORAL_STAR",
        estimated_minutes: 15,
        projected_delta: "+0.7",
        status: "COMPLETED",
        difficulty: "Senior Level • High Concurrency",
        why: "Demonstrates proven track record handling extreme traffic spikes and capacity planning.",
        how: {
          steps: [
            { phase: "Minute 0–4: Situation", detail: "Anticipated 50,000 TPS load for Black Friday; existing infrastructure degraded at 14,000 TPS." },
            { phase: "Minute 4–8: Task", detail: "Re-architect ingress API gateway within 4 weeks to guarantee 99.99% uptime under 4x traffic." },
            { phase: "Minute 8–12: Action", detail: "Deployed Envoy proxy with distributed Redis caching, connection multiplexing, and priority queuing for checkout APIs." },
            { phase: "Minute 12–15: Result", detail: "Handled 52,400 TPS with 34ms p99 latency; zero dropped transactions and 100% uptime." }
          ],
          optimal_approach: "Quantified capacity planning and layered architecture defense.",
          code_blueprint: `Situation: Anticipated 50,000 TPS load for Black Friday; existing infrastructure degraded at 14,000 TPS.
Task: Re-architect ingress API gateway within 4 weeks to guarantee 99.99% uptime under 4x traffic.
Action: Deployed Envoy proxy with distributed Redis caching, connection multiplexing, and priority queuing for checkout APIs.
Result: Handled 52,400 TPS with 34ms p99 latency; zero dropped transactions and 100% uptime.`,
          common_pitfalls: ["Focusing purely on throwing more servers at the problem without architectural optimizations.", "Not mentioning the business dollar impact."]
        },
        where: {
          platform: "Vireoniq Interview Twin Studio",
          url: "/app/interview-simulator",
          mnc_companies: ["Amazon", "Uber", "Walmart", "Shopify", "DoorDash"],
          recommended_tools: "Vireoniq Audio Simulator"
        },
        when: {
          recommended_time: "Evening (05:00 PM – 05:15 PM) — Leadership rehearsal",
          duration_minutes: 15,
          sprint_phase: "Day 2 of 14: Concurrency & Scale"
        },
        proof_criteria: {
          deliverable: "Structured STAR writeup with TPS and latency metrics.",
          verification_method: "Automated AI rubric evaluation"
        }
      }
    ]
  },

  "Data Engineer": {
    mission_date: todayDate,
    target_role: "Data Engineer",
    active_plan_title: "14-Day Data Engineer Accelerated Readiness Sprints (Set B)",
    rationale: "Targeting coordinate geometry algorithms, Delta Lake / Iceberg storage partitioning & Snowflake compute optimization.",
    tasks_count: 3,
    total_estimated_minutes: 70,
    progress_pct: 40,
    tasks: [
      {
        task_id: "de-alt-1",
        title: "Solve LeetCode #42: Trapping Rain Water (Two-Pointer Elevation Volume Calculation)",
        task_type: "CODING_DRILL",
        estimated_minutes: 30,
        projected_delta: "+1.5",
        status: "PENDING",
        difficulty: "Hard • Big Tech Algorithmic Standard",
        why: "Demonstrates optimal space efficiency O(1) and coordinate convergence essential for physical metric aggregations.",
        how: {
          steps: [
            { phase: "Minute 0–7: Invariant Analysis", detail: "Water trapped at index i is determined by min(max_left, max_right) - height[i]. Two pointers eliminate O(N) array storage." },
            { phase: "Minute 7–20: Two Pointer Convergence", detail: "Move pointer from shorter side inwards. Update left_max or right_max, adding difference to accumulated water volume." },
            { phase: "Minute 20–30: Edge Verification", detail: "Check monotonic heights ([1,2,3,4,5] -> 0), empty list, and valleys. Time: O(N), Auxiliary Space: O(1)." }
          ],
          optimal_approach: "Two Pointers moving inwards with left_max and right_max bounds. O(N) Time, O(1) Space.",
          code_blueprint: `def trap(height: list[int]) -> int:
    if not height: return 0
    l, r = 0, len(height) - 1
    left_max, right_max = height[l], height[r]
    water = 0
    while l < r:
        if left_max < right_max:
            l += 1
            left_max = max(left_max, height[l])
            water += left_max - height[l]
        else:
            r -= 1
            right_max = max(right_max, height[r])
            water += right_max - height[r]
    return water`,
          common_pitfalls: ["Using nested loops O(N^2), timing out on 100,000 array sizes.", "Forgetting to update max bounds before adding trapped water."]
        },
        where: {
          platform: "LeetCode #42",
          url: "https://leetcode.com/problems/trapping-rain-water/",
          mnc_companies: ["Google", "Amazon", "Bloomberg", "Meta", "Goldman Sachs"],
          recommended_tools: "LeetCode / Python"
        },
        when: {
          recommended_time: "Morning (09:00 AM – 09:30 AM) — Algorithmic rigor",
          duration_minutes: 30,
          sprint_phase: "Day 2 of 14: Two Pointers & Space Optimization"
        },
        proof_criteria: {
          deliverable: "Accepted LeetCode submission passing all 322 test cases with O(1) space.",
          verification_method: "Vireoniq Coding Studio"
        }
      },
      {
        task_id: "de-alt-2",
        title: "Design Lakehouse Bronze-Silver-Gold Medallion Partitioning with Delta Lake / Iceberg",
        task_type: "SYSTEM_DESIGN",
        estimated_minutes: 25,
        projected_delta: "+1.3",
        status: "PENDING",
        difficulty: "Senior • Modern Lakehouse Architecture",
        why: "Industry standard at Databricks, Snowflake, and Uber for petabyte-scale analytics and ACID reliability.",
        how: {
          steps: [
            { phase: "Minute 0–7: Medallion Layering", detail: "Bronze (Raw append-only landing) -> Silver (Cleaned, deduplicated, enriched) -> Gold (Aggregated business data marts)." },
            { phase: "Minute 7–16: Partitioning & Z-Ordering", detail: "Partition by date (year/month/day), apply Z-order clustering on high-cardinality lookup dimensions (userId, deviceId)." },
            { phase: "Minute 16–25: Compaction & Vacuuming", detail: "Design automated compaction job resolving small-file problems (bin-packing) and setting VACUUM retention periods." }
          ],
          optimal_approach: "Delta Lake Medallion Architecture with auto-compact, Z-order clustering, and strict retention SLAs.",
          code_blueprint: `from delta.tables import DeltaTable
# Silver Layer Upsert (Merge Schema & Deduplicate)
deltaTable = DeltaTable.forPath(spark, "s3://lakehouse/silver/events")
deltaTable.alias("target").merge(
    source_df.alias("source"),
    "target.event_id = source.event_id"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

# Optimize & Z-Order for sub-second query performance
spark.sql("OPTIMIZE delta.\`s3://lakehouse/silver/events\` ZORDER BY (user_id, event_type)")`,
          common_pitfalls: ["Over-partitioning by high cardinality keys (creating millions of 1KB files).", "Running VACUUM with zero retention during concurrent writes, corrupting active reads."]
        },
        where: {
          platform: "Delta Lake Architecture",
          url: "https://delta.io/",
          mnc_companies: ["Databricks", "Apple", "Uber", "Adobe", "Microsoft"],
          recommended_tools: "Apache Spark / Delta Lake"
        },
        when: {
          recommended_time: "Afternoon (02:00 PM – 02:25 PM) — Lakehouse engineering",
          duration_minutes: 25,
          sprint_phase: "Day 2 of 14: Lakehouse Storage Optimization"
        },
        proof_criteria: {
          deliverable: "Medallion architecture diagram and PySpark merge/optimize pipeline script.",
          verification_method: "Vireoniq Design Twin"
        }
      },
      {
        task_id: "de-alt-3",
        title: "Draft STAR Story on Slashing BigQuery / Snowflake Compute Bill by 60% via Clustering",
        task_type: "BEHAVIORAL_STAR",
        estimated_minutes: 15,
        projected_delta: "+0.7",
        status: "COMPLETED",
        difficulty: "Essential • FinOps & Cost Leadership",
        why: "Demonstrates business-minded cost optimization, partition pruning, and cluster clustering.",
        how: {
          steps: [
            { phase: "Minute 0–4: Situation", detail: "Snowflake warehouse compute costs surged to $45,000/month as analyst queries executed unindexed 50TB full-table scans." },
            { phase: "Minute 4–8: Task", detail: "Audit query patterns, eliminate full-table scans, and slash cloud data warehouse spend by at least 40%." },
            { phase: "Minute 8–12: Action", detail: "Restructured core fact tables with date partitioning and org_id clustering keys; replaced hourly batch rebuilds with incremental dynamic tables." },
            { phase: "Minute 12–15: Result", detail: "Cut scanned data volume by 84%, reduced dashboard load time by 3.2x, and reduced annual spend by $324,000." }
          ],
          optimal_approach: "Systematic query log profiling -> Partitioning & Clustering -> Materialized Views -> Measured Dollar Savings.",
          code_blueprint: `Situation: Snowflake warehouse compute costs surged to $45,000/month as analyst queries executed unindexed 50TB full-table scans.
Task: Audit query patterns, eliminate full-table scans, and slash cloud data warehouse spend by at least 40%.
Action: Restructured core fact tables with date partitioning and org_id clustering keys; replaced hourly batch rebuilds with incremental dynamic tables.
Result: Cut scanned data volume by 84%, reduced dashboard load time by 3.2x, and reduced annual spend by $324,000.`,
          common_pitfalls: ["Speaking vaguely about cost without specific dollar amounts or scanned gigabyte metrics.", "Not explaining the technical mechanism behind the savings."]
        },
        where: {
          platform: "Vireoniq Interview Twin Studio",
          url: "/app/interview-simulator",
          mnc_companies: ["Snowflake", "Databricks", "Amazon", "Meta", "Google"],
          recommended_tools: "Vireoniq Voice Studio"
        },
        when: {
          recommended_time: "Evening (05:00 PM – 05:15 PM) — Leadership rehearsal",
          duration_minutes: 15,
          sprint_phase: "Day 2 of 14: FinOps & Storage Strategy"
        },
        proof_criteria: {
          deliverable: "Structured STAR writeup with audited cost reduction percentages.",
          verification_method: "Automated AI rubric"
        }
      }
    ]
  }
};

export function getRoleDailyMission(role: string, cycle: number = 0): DailyMissionData {
  const normalized = normalizeRole(role);
  const isAlt = cycle % 2 === 1;
  const pool = isAlt ? ROLE_MISSIONS_ALT : ROLE_MISSIONS_PRIMARY;
  const mission = pool[normalized] || ROLE_MISSIONS_PRIMARY[normalized] || ROLE_MISSIONS_PRIMARY["Backend Engineer"];
  return {
    ...mission,
    mission_date: new Date().toISOString().split('T')[0]
  };
}
