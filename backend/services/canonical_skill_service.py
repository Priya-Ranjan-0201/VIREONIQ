"""
Canonical Skill Service.
Manages normalized skill entities, alias dictionaries, hierarchical taxonomies,
semantic relationships (prerequisite, parent, complementary), and evidence-derived proficiency levels.
"""

from typing import Dict, Any, List, Optional, Tuple
import uuid
import re
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from db.models import CanonicalSkill, SkillRelationship

logger = logging.getLogger(__name__)

# Standard seed taxonomy and aliases
CANONICAL_SKILL_SEEDS = [
    {
        "name": "Python",
        "category": "Programming",
        "aliases": ["python3", "python 3", "py", "python programming", "cpython"],
        "description": "High-level, general-purpose interpreted programming language."
    },
    {
        "name": "FastAPI",
        "category": "API Engineering",
        "aliases": ["fastapi framework", "fast-api"],
        "description": "Modern high-performance web framework for building APIs with Python."
    },
    {
        "name": "PostgreSQL",
        "category": "Databases",
        "aliases": ["postgres", "pgsql", "postgresql 15", "postgres db"],
        "description": "Powerful open source object-relational database system."
    },
    {
        "name": "Redis",
        "category": "Databases",
        "aliases": ["redis cache", "redis key-value"],
        "description": "In-memory data structure store used as database, cache, and message broker."
    },
    {
        "name": "System Design",
        "category": "Architecture",
        "aliases": ["distributed architecture", "systems design", "high level design", "hld"],
        "description": "Architecting scalable, fault-tolerant distributed software systems."
    },
    {
        "name": "Docker",
        "category": "DevOps",
        "aliases": ["docker containers", "containerization"],
        "description": "OS-level virtualization platform for packaging software into containers."
    },
    {
        "name": "Kubernetes",
        "category": "DevOps",
        "aliases": ["k8s", "kube"],
        "description": "Automated container orchestration, scaling, and management."
    },
    {
        "name": "TypeScript",
        "category": "Frontend",
        "aliases": ["ts", "typescript lang"],
        "description": "Strict syntactical superset of JavaScript adding static type definitions."
    },
    {
        "name": "React",
        "category": "Frontend",
        "aliases": ["reactjs", "react.js", "react framework"],
        "description": "JavaScript library for building component-based user interfaces."
    },
    {
        "name": "Machine Learning",
        "category": "AI/ML",
        "aliases": ["ml", "applied ml", "machine learning algorithms"],
        "description": "Statistical modeling and algorithms that iteratively learn from data."
    },
    {
        "name": "PyTorch",
        "category": "AI/ML",
        "aliases": ["torch", "pytorch deep learning"],
        "description": "Open source machine learning framework based on the Torch library."
    }
]

# Standard Relationships
SKILL_RELATIONSHIP_SEEDS = [
    ("Python", "FastAPI", "prerequisite"),
    ("Python", "PyTorch", "prerequisite"),
    ("PostgreSQL", "Redis", "complementary"),
    ("FastAPI", "PostgreSQL", "complementary"),
    ("Docker", "Kubernetes", "prerequisite"),
    ("System Design", "Distributed Systems", "related"),
    ("TypeScript", "React", "complementary"),
]

# Multidimensional Decomposition Schemas
SKILL_DIMENSION_SCHEMAS: Dict[str, List[str]] = {
    "Python": [
        "Syntax & Idioms", "Data Structures", "Algorithms", "OOP & Modularity",
        "Async Programming", "Testing & Mocking", "API Engineering",
        "Performance & Optimization", "Production Packaging"
    ],
    "FastAPI": [
        "Routing & Path Operations", "Pydantic Schemas", "Dependency Injection",
        "Middleware & Authentication", "Background Tasks", "TestClient Suite", "OpenAPI Standards"
    ],
    "System Design": [
        "Architectural Decomposition", "Database Partitioning & Sharding", "Caching Strategies",
        "Load Balancing & Proxies", "Consistency & Replication", "Observability & Telemetry"
    ],
    "PostgreSQL": [
        "Relational Schema Design", "B-Tree & GIN Indexing", "Complex Joins & Aggregations",
        "Transactions & ACID Isolation", "Connection Management", "Migration Versioning"
    ],
    "TypeScript": [
        "Type Inference & Annotations", "Generics & Conditional Types", "Interfaces & Type Aliases",
        "Async Control Flow", "React Component Typing", "TSConfig Strict Mode"
    ],
    "React": [
        "Component Composition", "Hooks Lifecycle & State", "Context & Global State",
        "Memoization & Performance", "Client Routing", "Accessibility & ARIA"
    ],
    "Docker": [
        "Dockerfile Optimization", "Multi-stage Builds", "Volume Mounting",
        "Docker Compose Networking", "Container Security & Non-Root"
    ],
    "Kubernetes": [
        "Pods & Deployments", "Services & Ingress", "ConfigMaps & Secrets",
        "HPA & Autoscaling", "Helm Chart Templating", "Cluster Observability"
    ],
    "Data Structures": [
        "Arrays & Strings", "Hash Maps & Sets", "Linked Lists & Trees",
        "Graphs & BFS/DFS", "Heaps & Priority Queues", "Dynamic Programming"
    ]
}

# Strict Prerequisite Dependency Tree (Child -> List of Direct Prerequisites)
PREREQUISITE_DEPENDENCY_TREE: Dict[str, List[str]] = {
    "FastAPI": ["Python"],
    "PyTorch": ["Python", "Data Structures"],
    "Kubernetes": ["Docker"],
    "Microservices": ["REST APIs", "Docker"],
    "Distributed Systems": ["System Design", "Microservices"],
    "REST APIs": ["HTTP & Networking"],
    "Database Partitioning": ["PostgreSQL"],
    "Caching Strategies": ["Redis"],
    "React": ["TypeScript", "HTML/CSS"],
    "Full Stack Development": ["React", "FastAPI", "PostgreSQL"]
}

def find_true_prerequisite_bottleneck(
    candidate_skills: Dict[str, float],
    target_skill: str
) -> Optional[Dict[str, Any]]:
    """
    Traverses the prerequisite dependency tree recursively to identify the TRUE foundational bottleneck.
    Prevents prematurely recommending advanced competencies when prerequisites are ungrounded.
    """
    canonical_target = normalize_skill_name(target_skill)
    norm_candidate_skills = {normalize_skill_name(k).lower(): float(v) for k, v in candidate_skills.items()}

    # Map normalized prerequisite tree
    norm_prereq_tree = {}
    for parent, children in PREREQUISITE_DEPENDENCY_TREE.items():
        norm_parent = normalize_skill_name(parent).lower()
        norm_prereq_tree[norm_parent] = [normalize_skill_name(c) for c in children]

    ROLE_PREREQ_MAP = {
        "backend engineer": ["Distributed Systems", "Microservices", "FastAPI", "REST APIs"],
        "frontend engineer": ["React", "TypeScript"],
        "full stack engineer": ["Full Stack Development"],
        "full stack developer": ["Full Stack Development"],
        "devops engineer": ["Kubernetes", "Docker"],
        "ai/ml engineer": ["PyTorch", "Data Structures"],
        "data scientist": ["PyTorch"]
    }

    visited = set()
    queue = []
    
    if canonical_target.lower() in ROLE_PREREQ_MAP:
        queue.extend(ROLE_PREREQ_MAP[canonical_target.lower()])
    else:
        queue.append(canonical_target)

    while queue:
        curr = queue.pop(0)
        curr_norm = normalize_skill_name(curr).lower()
        if curr_norm in visited:
            continue
        visited.add(curr_norm)

        prereqs = norm_prereq_tree.get(curr_norm, [])
        for p in prereqs:
            p_norm = normalize_skill_name(p).lower()
            current_score = norm_candidate_skills.get(p_norm, 0.0)
            if current_score < 65.0:
                # Found the root unfulfilled prerequisite
                return {
                    "target_skill": curr,
                    "bottleneck_skill": p,
                    "current_score": current_score,
                    "required_threshold": 65.0,
                    "reason": f"Cannot effectively master {curr} without grounded foundational competency in {p}."
                }
            queue.append(p)

    return None

def compute_multidimensional_skill_mastery(
    skill_name: str,
    base_score: float = 75.0,
    evidence_tier: str = "ASSESSED",
    evidence_count: int = 2
) -> Dict[str, Any]:
    """
    Constructs a granular multidimensional breakdown for a skill node with mastery, confidence,
    evidence coverage, freshness, and weakest/strongest dimensions.
    """
    canonical_skill = normalize_skill_name(skill_name)
    sub_dims = SKILL_DIMENSION_SCHEMAS.get(canonical_skill, [
        "Core Fundamentals", "Applied Problem Solving", "Architecture & Modularity",
        "Testing & Verification", "Performance & Optimization"
    ])

    # Derive dimensional scores deterministically
    dimensions_breakdown = []
    dim_scores = []

    # Assign deterministic variance based on evidence tier
    variance_offsets = [0.0, 4.0, -8.0, -3.0, 5.0, -12.0, 2.0, -5.0, 1.0]
    for idx, dim in enumerate(sub_dims):
        offset = variance_offsets[idx % len(variance_offsets)]
        if evidence_tier == "CLAIMED":
            dim_score = max(30.0, min(100.0, base_score + offset - 15.0))
            status = "CLAIMED"
        elif evidence_tier == "DEMONSTRATED":
            dim_score = max(40.0, min(100.0, base_score + offset))
            status = "DEMONSTRATED"
        elif evidence_tier in ("ASSESSED", "VERIFIED"):
            dim_score = max(50.0, min(100.0, base_score + offset))
            status = "ASSESSED"
        else:
            dim_score = max(20.0, min(100.0, base_score + offset - 20.0))
            status = "INFERRED"

        dim_scores.append(dim_score)
        dimensions_breakdown.append({
            "dimension_name": dim,
            "score": round(dim_score, 1),
            "status": status,
            "is_weakness": dim_score < 70.0
        })

    avg_mastery = round(sum(dim_scores) / len(dim_scores), 1) if dim_scores else base_score
    coverage_pct = round(min(100.0, (evidence_count / max(1, len(sub_dims))) * 100.0 + 35.0), 1) if evidence_tier != "CLAIMED" else 20.0

    weakest = min(dimensions_breakdown, key=lambda x: x["score"]) if dimensions_breakdown else None
    strongest = max(dimensions_breakdown, key=lambda x: x["score"]) if dimensions_breakdown else None

    return {
        "skill_name": canonical_skill,
        "mastery_score": avg_mastery,
        "evidence_tier": evidence_tier,
        "confidence": "HIGH" if evidence_tier in ("ASSESSED", "VERIFIED") else "MEDIUM" if evidence_tier == "DEMONSTRATED" else "LOW",
        "evidence_coverage_pct": coverage_pct,
        "freshness": "HIGH",
        "weakest_dimension": weakest["dimension_name"] if weakest else None,
        "strongest_dimension": strongest["dimension_name"] if strongest else None,
        "dimensions": dimensions_breakdown
    }


def normalize_skill_name(raw_name: str) -> str:
    """
    Normalizes any raw user/resume/job skill string into its canonical entity name.
    Example: 'python 3' -> 'Python', 'fast-api' -> 'FastAPI', 'postgres' -> 'PostgreSQL'.
    """
    if not raw_name:
        return "Unknown Skill"
    
    cleaned = raw_name.strip()
    cleaned_lower = cleaned.lower()

    for seed in CANONICAL_SKILL_SEEDS:
        if cleaned_lower == seed["name"].lower():
            return seed["name"]
        for alias in seed["aliases"]:
            if cleaned_lower == alias.lower() or re.sub(r'[^a-z0-9]', '', cleaned_lower) == re.sub(r'[^a-z0-9]', '', alias.lower()):
                return seed["name"]

    # Title case clean fallback
    return cleaned.title()


def derive_proficiency_level(
    evidence_tier: str,
    mastery_score: float,
    evidence_count: int = 1
) -> Tuple[int, str]:
    """
    Derives standardized proficiency level (0-5) strictly from grounded evidence.
    0: Unknown, 1: Familiar, 2: Beginner, 3: Intermediate, 4: Advanced, 5: Expert.
    """
    if not evidence_tier or evidence_tier == "CLAIMED":
        return 1, "Familiar (Self-Claimed)"
    elif evidence_tier == "INFERRED":
        return 2, "Beginner (Contextually Inferred)"
    elif evidence_tier == "DEMONSTRATED":
        if mastery_score >= 80.0:
            return 3, "Intermediate (Demonstrated in Projects)"
        return 2, "Beginner (Demonstrated)"
    elif evidence_tier == "ASSESSED":
        if mastery_score >= 90.0:
            return 4, "Advanced (Controlled Assessment Passed)"
        elif mastery_score >= 70.0:
            return 3, "Intermediate (Controlled Assessment Passed)"
        return 2, "Beginner (Assessment < 70%)"
    elif evidence_tier == "VERIFIED":
        if mastery_score >= 92.0 and evidence_count >= 3:
            return 5, "Expert (Multi-Source Verified)"
        elif mastery_score >= 80.0:
            return 4, "Advanced (Verified Assessment)"
        return 3, "Intermediate (Verified)"
    
    return 0, "Unknown"


async def get_or_create_canonical_skill(
    skill_name: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Retrieves or creates canonical skill record.
    """
    canonical_name = normalize_skill_name(skill_name)
    slug = canonical_name.lower().replace(" ", "-").replace("/", "-")

    stmt = select(CanonicalSkill).where(CanonicalSkill.name == canonical_name)
    skill_obj = (await db.execute(stmt)).scalars().first()

    if not skill_obj:
        # Check if seed meta exists
        meta = next((s for s in CANONICAL_SKILL_SEEDS if s["name"] == canonical_name), None)
        category = meta["category"] if meta else "Technical"
        aliases = meta["aliases"] if meta else []
        desc = meta["description"] if meta else f"Technical competency in {canonical_name}."

        skill_obj = CanonicalSkill(
            name=canonical_name,
            slug=slug,
            category=category,
            aliases=aliases,
            description=desc
        )
        db.add(skill_obj)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            # Retry select if created concurrently
            stmt = select(CanonicalSkill).where(CanonicalSkill.name == canonical_name)
            skill_obj = (await db.execute(stmt)).scalars().first()

    return {
        "id": str(skill_obj.id) if skill_obj else None,
        "name": skill_obj.name if skill_obj else canonical_name,
        "slug": skill_obj.slug if skill_obj else slug,
        "category": skill_obj.category if skill_obj else "Technical",
        "aliases": skill_obj.aliases if skill_obj else [],
        "description": skill_obj.description if skill_obj else ""
    }


def get_skill_relationships(skill_name: str) -> List[Dict[str, Any]]:
    """
    Returns relational connections (prerequisites, complementary, related) for a skill.
    """
    canonical = normalize_skill_name(skill_name)
    results = []
    for src, tgt, rel in SKILL_RELATIONSHIP_SEEDS:
        if src.lower() == canonical.lower():
            results.append({"target_skill": tgt, "relationship_type": rel, "direction": "outgoing"})
        elif tgt.lower() == canonical.lower():
            results.append({"source_skill": src, "relationship_type": rel, "direction": "incoming"})
    return results


class SkillKnowledgeGraph:
    """
    Graph-based Skill Inference Engine using Personalized PageRank.
    Infers implicit competencies and complementary tech skills based on explicit evidence.
    """
    def __init__(self):
        self._graph = None
        self._build_graph()

    def _build_graph(self):
        try:
            import networkx as nx
            self._graph = nx.Graph()
            base_edges = [
                ("React", "JavaScript", 0.95),
                ("React", "HTML", 0.85),
                ("React", "CSS", 0.85),
                ("React", "TypeScript", 0.90),
                ("React", "Next.js", 0.90),
                ("Next.js", "TypeScript", 0.90),
                ("Redux", "React", 0.85),
                ("Redux", "JavaScript", 0.90),
                ("Node.js", "JavaScript", 0.95),
                ("Node.js", "TypeScript", 0.85),
                ("Express", "Node.js", 0.90),
                ("FastAPI", "Python", 0.95),
                ("FastAPI", "PostgreSQL", 0.85),
                ("FastAPI", "Redis", 0.80),
                ("Django", "Python", 0.95),
                ("Flask", "Python", 0.90),
                ("Pandas", "Python", 0.90),
                ("NumPy", "Python", 0.85),
                ("PyTorch", "Python", 0.95),
                ("PyTorch", "Machine Learning", 0.95),
                ("PyTorch", "Deep Learning", 0.90),
                ("TensorFlow", "Python", 0.90),
                ("TensorFlow", "Machine Learning", 0.95),
                ("LangChain", "Python", 0.90),
                ("LangChain", "Vector Database", 0.85),
                ("Qdrant", "Vector Database", 0.95),
                ("Docker", "Linux", 0.85),
                ("Docker", "Containerization", 0.95),
                ("Kubernetes", "Docker", 0.90),
                ("Kubernetes", "Cloud Computing", 0.85),
                ("AWS", "Cloud Computing", 0.95),
                ("AWS", "Docker", 0.80),
                ("Terraform", "DevOps", 0.90),
                ("Terraform", "AWS", 0.85),
                ("PostgreSQL", "SQL", 0.95),
                ("PostgreSQL", "Database Design", 0.90),
                ("PostgreSQL", "Relational Database", 0.95),
                ("System Design", "Distributed Systems", 0.95),
                ("System Design", "Microservices", 0.90),
                ("Redis", "Caching", 0.95),
                ("Redis", "Distributed Systems", 0.85),
                ("Kafka", "Event-Driven Architecture", 0.90),
                ("Kafka", "Distributed Systems", 0.90),
                ("Git", "CI/CD", 0.85)
            ]
            for src, dst, weight in base_edges:
                self._graph.add_edge(src.lower(), dst.lower(), weight=weight)
        except Exception as e:
            logger.warning(f"Failed to initialize NetworkX SkillKnowledgeGraph: {e}")
            self._graph = None

    def infer_skills(self, explicit_skills: List[str], threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Uses Personalized PageRank with explicit skills as teleport targets to compute implicit affinities.
        """
        if not self._graph or not explicit_skills:
            return []

        import networkx as nx
        explicit_canonical = [normalize_skill_name(s) for s in explicit_skills if s]
        explicit_lower = {s.lower() for s in explicit_canonical}

        # Teleport personalization dictionary
        personalization = {node: (1.0 if node in explicit_lower else 0.0) for node in self._graph.nodes()}
        if sum(personalization.values()) == 0:
            return []

        try:
            pagerank_scores = nx.pagerank(self._graph, personalization=personalization, weight="weight")
            non_explicit_scores = [score for node, score in pagerank_scores.items() if node not in explicit_lower]
            max_score = max(non_explicit_scores) if non_explicit_scores else 1.0

            inferred = []
            for node, score in pagerank_scores.items():
                norm_score = (score / max_score) if max_score > 0 else 0.0
                if node not in explicit_lower and norm_score >= threshold:
                    canonical_name = normalize_skill_name(node)
                    inferred.append({
                        "skill_name": canonical_name,
                        "confidence_score": round(norm_score * 100, 1),
                        "evidence_type": "GRAPH_INFERRED",
                        "status": "INFERRED",
                        "source": "Skill Knowledge Graph (PageRank)"
                    })
            return sorted(inferred, key=lambda x: x["confidence_score"], reverse=True)
        except Exception as exc:
            logger.error(f"Skill inference error: {exc}")
            return []

_kg_instance: Optional[SkillKnowledgeGraph] = None

def get_skill_knowledge_graph() -> SkillKnowledgeGraph:
    global _kg_instance
    if _kg_instance is None:
        _kg_instance = SkillKnowledgeGraph()
    return _kg_instance

def infer_implicit_skills_from_graph(explicit_skills: List[str], threshold: float = 0.5) -> List[Dict[str, Any]]:
    return get_skill_knowledge_graph().infer_skills(explicit_skills, threshold)
