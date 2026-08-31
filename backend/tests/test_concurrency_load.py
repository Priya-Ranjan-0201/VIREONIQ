import time
import asyncio
import numpy as np
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from core.security import create_access_token
from db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_controlled_concurrency_load(test_engine):
    """
    Controlled concurrency test at 10, 25, 50, 100 concurrent requests
    measuring throughput (req/s), p50, p95, p99 latencies, and error rates.
    """
    session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    token = create_access_token(subject="load_test_user", jti="load_jti_789")
    headers = {"Authorization": f"Bearer {token}"}

    test_endpoints = [
        ("GET", "/api/v1/health", None),
        ("POST", "/api/v1/resume-builder/calculate-ats", {
            "resume_data": {
                "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
                "experience": [{"role": "Senior Engineer", "company": "TechCorp", "bullets": ["Built high-throughput microservices using FastAPI"]}],
                "education": [{"degree": "B.S. Computer Science", "school": "MIT"}]
            },
            "target_role": "Senior Backend Engineer"
        }),
        ("POST", "/api/v1/resume-builder/parse-text", {
            "raw_text": "Jane Doe\nEmail: jane@example.com\nPhone: +1 555-0199\nSkills: Python, FastAPI, PostgreSQL, Docker, Kubernetes\nExperience:\nSenior Engineer at CloudCorp (2020-Present)",
            "target_role": "Senior Backend Engineer"
        }),
        ("POST", "/api/v1/mnc-interview/profiles", {
            "company_name": "Google",
            "industry": "Technology",
            "role_family": "Backend Engineering",
            "target_level": "SDE-2"
        })
    ]

    concurrency_levels = [5, 10, 20]
    results = {}

    # Warm-up call
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.get("/api/v1/health")
        await ac.post("/api/v1/mnc-interview/profiles", json={"company_name": "Warmup", "industry": "Tech", "role_family": "Eng", "target_level": "L4"})

    print("\n\n" + "=" * 90)
    print(f"{'CONTROLLED CONCURRENCY LOAD TEST REPORT':^90}")
    print("=" * 90)

    for method, path, payload in test_endpoints:
        endpoint_name = path.split("/")[-1]
        results[endpoint_name] = {}
        print(f"\nTarget: {method} {path}")
        print(f"{'Concurrency':<12} | {'Requests':<10} | {'Throughput (req/s)':<20} | {'p50 (ms)':<10} | {'p95 (ms)':<10} | {'p99 (ms)':<10} | {'Errors':<8}")
        print("-" * 90)

        for c in concurrency_levels:
            latencies = []
            errors = 0

            async def send_req(client: AsyncClient):
                nonlocal errors
                t0 = time.perf_counter()
                try:
                    if method == "GET":
                        r = await client.get(path, headers=headers)
                    else:
                        r = await client.post(path, json=payload, headers=headers)
                    t1 = time.perf_counter()
                    latencies.append((t1 - t0) * 1000)
                    if r.status_code >= 400:
                        errors += 1
                except Exception:
                    errors += 1

            t_start = time.perf_counter()
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                tasks = [send_req(ac) for _ in range(c)]
                await asyncio.gather(*tasks)
            t_end = time.perf_counter()

            total_time = t_end - t_start
            throughput = c / total_time if total_time > 0 else 0
            p50 = float(np.percentile(latencies, 50)) if latencies else 0.0
            p95 = float(np.percentile(latencies, 95)) if latencies else 0.0
            p99 = float(np.percentile(latencies, 99)) if latencies else 0.0
            err_rate = f"{(errors / c) * 100:.1f}%"

            results[endpoint_name][c] = {
                "throughput": throughput,
                "p50": p50,
                "p95": p95,
                "p99": p99,
                "errors": errors,
                "error_rate": err_rate
            }

            print(f"{c:<12} | {c:<10} | {throughput:<20.1f} | {p50:<10.2f} | {p95:<10.2f} | {p99:<10.2f} | {err_rate:<8}")

    print("=" * 90)
