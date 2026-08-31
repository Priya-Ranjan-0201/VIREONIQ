from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from services.code.judge0_provider import judge0_provider, LANGUAGE_KEY_TO_ID
from api import deps
from db.models import User

router = APIRouter()

class CodeExecutionRequest(BaseModel):
    source_code: Optional[str] = None
    code: Optional[str] = None
    language_id: Optional[int] = None
    language: Optional[str] = None
    stdin: str = ""

class CodeExecutionResponse(BaseModel):
    stdout: str | None
    stderr: str | None
    compile_output: str | None
    time: str | None
    memory: int | None
    status: dict

@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(
    request: CodeExecutionRequest,
    current_user: User = Depends(deps.get_current_active_user)
) -> CodeExecutionResponse:
    """
    Executes source code in the Judge0 sandbox environments.
    Supports either source_code/language_id or code/language payload structures.
    Requires an authenticated, active user account.
    """
    src = request.source_code or request.code or ""
    lang_id = request.language_id
    if lang_id is None and request.language:
        lang_id = LANGUAGE_KEY_TO_ID.get(request.language.lower(), 71)
    if lang_id is None:
        lang_id = 71

    # 1. Create submission
    token = await judge0_provider.create_submission(
        source_code=src,
        language_id=lang_id,
        stdin=request.stdin
    )
    
    # 2. Poll for result (simulated as immediate in mock)
    result = await judge0_provider.get_submission(token)
    
    return CodeExecutionResponse(
        stdout=result.get("stdout"),
        stderr=result.get("stderr"),
        compile_output=result.get("compile_output"),
        time=result.get("time"),
        memory=result.get("memory"),
        status=result.get("status", {"id": 3, "description": "Accepted"})
    )

@router.get("/languages", response_model=List[Dict[str, Any]])
async def get_supported_languages(
    current_user: User = Depends(deps.get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    Returns a list of supported programming languages and versions.
    Requires an authenticated, active user account.
    """
    return await judge0_provider.get_languages()
