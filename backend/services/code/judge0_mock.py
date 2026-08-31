import logging
import asyncio
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MockJudge0Provider:
    """
    Mock implementation of Judge0 execution sandbox.
    Will be replaced by real Judge0 container in production.
    """
    
    async def create_submission(self, source_code: str, language_id: int, stdin: str = "", expected_output: str = "") -> str:
        # Returns a mock submission token
        logger.info(f"Mock Judge0: Created submission for lang {language_id}")
        await asyncio.sleep(1.5)  # Simulate container execution latency
        return "mock-token-12345"
        
    async def get_submission(self, token: str) -> Dict[str, Any]:
        # Returns a successful mock execution result
        return {
            "source_code": "print('Hello')",
            "language_id": 71,  # Python 3
            "stdin": "",
            "expected_output": "",
            "stdout": "Hello\n",
            "status_id": 3,  # Accepted
            "created_at": "2023-01-01T00:00:00.000Z",
            "finished_at": "2023-01-01T00:00:01.000Z",
            "time": "0.01",
            "memory": 2048,
            "stderr": None,
            "token": token,
            "compile_output": None,
            "message": None,
            "status": {
                "id": 3,
                "description": "Accepted"
            }
        }

    async def get_languages(self) -> List[Dict[str, Any]]:
        return [
            {"id": 71, "name": "Python (3.8.1)"},
            {"id": 62, "name": "Java (13.0.1)"},
            {"id": 54, "name": "C++ (GCC 9.2.0)"},
            {"id": 63, "name": "JavaScript (Node.js 12.14.0)"}
        ]

judge0_provider = MockJudge0Provider()
