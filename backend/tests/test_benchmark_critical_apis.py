import time
import numpy as np
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from main import app
from core.security import create_access_token
from db.models import User, Role

from db.session import get_db

@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_benchmark_critical_endpoints(db_session: AsyncSession):
    """
    Empirical latency benchmark measuring p50, p95, p99 across key endpoints
    using ASGI in-memory transport.
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    token = create_access_token(subject="bench_candidate", jti="bench_jti_123")
    headers = {"Authorization": f"Bearer {token}"}

    benchmarks = {}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Health Probe
        latencies = []
        for _ in range(5):
            t0 = time.perf_counter()
            res = await ac.get("/api/v1/health")
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000)
            assert res.status_code == 200
        benchmarks["health_probe"] = {
            "p50": np.percentile(latencies, 50),
            "p95": np.percentile(latencies, 95),
            "p99": np.percentile(latencies, 99),
        }

        # 2. ATS Score Calculation & Parsing via resume-builder API
        latencies = []
        payload = {
            "raw_text": "Experienced Python Backend Engineer with 5 years building scalable FastAPI microservices on AWS.",
            "target_role": "Backend Engineer"
        }
        for _ in range(5):
            t0 = time.perf_counter()
            res = await ac.post("/api/v1/resume-builder/parse-text", json=payload)
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000)
            assert res.status_code == 200
        benchmarks["resume_parse_text"] = {
            "p50": np.percentile(latencies, 50),
            "p95": np.percentile(latencies, 95),
            "p99": np.percentile(latencies, 99),
        }

        # 3. Resume Builder ATS Scoring API
        latencies = []
        ats_payload = {
            "resume_data": {
                "summary": "Full Stack Engineer specializing in React, Node, and Python",
                "skills": ["Python", "React", "PostgreSQL", "Docker"],
                "experience": [{"role": "Senior Engineer", "bullets": ["Built high-throughput API processing 10k req/s"]}]
            },
            "target_role": "Full Stack Engineer"
        }
        for _ in range(5):
            t0 = time.perf_counter()
            res = await ac.post("/api/v1/resume-builder/calculate-ats", json=ats_payload)
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000)
            assert res.status_code == 200
        benchmarks["resume_calculate_ats"] = {
            "p50": np.percentile(latencies, 50),
            "p95": np.percentile(latencies, 95),
            "p99": np.percentile(latencies, 99),
        }

        # 4. MNC Company Blueprint Generation API
        latencies = []
        blueprint_payload = {
            "role": "Backend Engineer",
            "level": "SDE-2",
            "round_type": "CODING",
            "topic": "Arrays & Hashing",
            "difficulty": "MEDIUM"
        }
        for _ in range(5):
            t0 = time.perf_counter()
            res = await ac.post("/api/v1/mnc-interview/blueprint", json=blueprint_payload)
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000)
            assert res.status_code == 200
        benchmarks["mnc_blueprint_generation"] = {
            "p50": np.percentile(latencies, 50),
            "p95": np.percentile(latencies, 95),
            "p99": np.percentile(latencies, 99),
        }

        # 5. MNC Company Profile Generation API
        latencies = []
        profile_payload = {
            "company_name": "Google",
            "industry": "Technology",
            "role_family": "Backend Engineering",
            "target_level": "SDE-2"
        }
        for _ in range(5):
            t0 = time.perf_counter()
            res = await ac.post("/api/v1/mnc-interview/profiles", json=profile_payload)
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000)
            assert res.status_code == 200
        benchmarks["mnc_profile_generation"] = {
            "p50": np.percentile(latencies, 50),
            "p95": np.percentile(latencies, 95),
            "p99": np.percentile(latencies, 99),
        }

    print("\n\n=== EMPIRICAL API PERFORMANCE BENCHMARK (N=30 iterations per endpoint) ===")
    for ep, metrics in benchmarks.items():
        print(f"Endpoint: {ep:<25} | p50: {metrics['p50']:6.2f} ms | p95: {metrics['p95']:6.2f} ms | p99: {metrics['p99']:6.2f} ms")
    print("===========================================================================\n")
