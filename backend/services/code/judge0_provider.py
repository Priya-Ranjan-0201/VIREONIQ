import asyncio
import time
from typing import Any, Dict, List
import httpx
import structlog

from core.config import settings

logger = structlog.get_logger("vireoniq.judge0")

ALL_JUDGE0_LANGUAGES = [
    {"id": 71, "name": "Python (3.12 Sandboxed)", "key": "python", "monacoLang": "python", "extension": "py"},
    {"id": 62, "name": "Java (OpenJDK 21 LTS)", "key": "java", "monacoLang": "java", "extension": "java"},
    {"id": 54, "name": "C++ (GCC 13.2 / C++20)", "key": "cpp", "monacoLang": "cpp", "extension": "cpp"},
    {"id": 50, "name": "C (GCC 13.2 / C11)", "key": "c", "monacoLang": "c", "extension": "c"},
    {"id": 63, "name": "JavaScript (Node.js 20)", "key": "javascript", "monacoLang": "javascript", "extension": "js"},
    {"id": 74, "name": "TypeScript (TS 5.4 / Node)", "key": "typescript", "monacoLang": "typescript", "extension": "ts"},
    {"id": 60, "name": "Go (Golang 1.22)", "key": "go", "monacoLang": "go", "extension": "go"},
    {"id": 73, "name": "Rust (Rust 1.77 / Cargo)", "key": "rust", "monacoLang": "rust", "extension": "rs"},
    {"id": 51, "name": "C# (.NET 8.0 SDK)", "key": "csharp", "monacoLang": "csharp", "extension": "cs"},
    {"id": 78, "name": "Kotlin (Kotlin 1.9 JVM)", "key": "kotlin", "monacoLang": "kotlin", "extension": "kt"},
    {"id": 83, "name": "Swift (Swift 5.10 Native)", "key": "swift", "monacoLang": "swift", "extension": "swift"},
    {"id": 72, "name": "Ruby (Ruby 3.3 YJIT)", "key": "ruby", "monacoLang": "ruby", "extension": "rb"},
    {"id": 68, "name": "PHP (PHP 8.3 Zend)", "key": "php", "monacoLang": "php", "extension": "php"},
    {"id": 81, "name": "Scala (Scala 3.4 JVM)", "key": "scala", "monacoLang": "scala", "extension": "scala"},
    {"id": 90, "name": "Dart (Dart 3.3 AOT)", "key": "dart", "monacoLang": "dart", "extension": "dart"},
    {"id": 82, "name": "SQL (PostgreSQL 16 Engine)", "key": "sql", "monacoLang": "sql", "extension": "sql"},
    {"id": 46, "name": "Bash (GNU Bash 5.2 Shell)", "key": "bash", "monacoLang": "shell", "extension": "sh"},
]

LANGUAGE_KEY_TO_ID = {l["key"]: l["id"] for l in ALL_JUDGE0_LANGUAGES}
LANGUAGE_ID_TO_NAME = {l["id"]: l["name"] for l in ALL_JUDGE0_LANGUAGES}


def _sandbox_unavailable_result(reason: str) -> Dict[str, Any]:
    return {
        "stdout": None,
        "stderr": reason,
        "compile_output": None,
        "time": "0.0",
        "memory": 0,
        "status": {"id": 13, "description": "Execution Sandbox Unavailable"},
    }


class Judge0Provider:
    """Client for external isolated Judge0 execution sandbox (never executes untrusted host code)."""

    def __init__(self):
        self.base_url = (settings.JUDGE0_API_URL or "").rstrip("/")
        self._unavailable_submissions: Dict[str, Dict[str, Any]] = {}

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if settings.JUDGE0_API_KEY:
            headers["X-Auth-Token"] = settings.JUDGE0_API_KEY
        return headers

    async def create_submission(
        self, source_code: str, language_id: int, stdin: str = "", expected_output: str = ""
    ) -> str:
        if not self.base_url:
            token = f"unavailable-{int(time.time() * 1000)}"
            self._unavailable_submissions[token] = _sandbox_unavailable_result(
                "Execution sandbox unavailable: JUDGE0_API_URL is not configured."
            )
            return token

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                payload = {
                    "source_code": source_code,
                    "language_id": language_id,
                    "stdin": stdin,
                    "expected_output": expected_output,
                }
                response = await client.post(
                    f"{self.base_url}/submissions?wait=false",
                    json=payload,
                    headers=self._headers(),
                )
                response.raise_for_status()
                data = response.json()
                return data["token"]
        except Exception as e:
            logger.warning("judge0_submission_failed", error=str(e))
            token = f"unavailable-{int(time.time() * 1000)}"
            self._unavailable_submissions[token] = _sandbox_unavailable_result(
                "Execution sandbox is currently unreachable. Host execution is disabled for security."
            )
            return token

    async def get_submission(self, token: str) -> Dict[str, Any]:
        if token in self._unavailable_submissions:
            return self._unavailable_submissions[token]
        if not self.base_url:
            return _sandbox_unavailable_result("Execution sandbox unavailable: JUDGE0_API_URL is not configured.")

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                for _ in range(10):
                    response = await client.get(
                        f"{self.base_url}/submissions/{token}",
                        headers=self._headers(),
                    )
                    response.raise_for_status()
                    data = response.json()
                    status_id = data.get("status", {}).get("id")
                    if status_id not in (1, 2):
                        return data
                    await asyncio.sleep(1)

                return {"status": {"id": 1, "description": "Timeout"}, "stdout": None}
        except Exception as e:
            logger.warning("judge0_poll_failed", error=str(e))
            return _sandbox_unavailable_result("Failed to retrieve sandbox execution result.")

    async def get_languages(self) -> List[Dict[str, Any]]:
        if not self.base_url:
            return ALL_JUDGE0_LANGUAGES
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{self.base_url}/languages", headers=self._headers())
                response.raise_for_status()
                return response.json()
        except Exception:
            logger.info("judge0_languages_fallback_catalog")
            return ALL_JUDGE0_LANGUAGES


judge0_provider = Judge0Provider()
