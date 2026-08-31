from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, TargetRole
from crud import crud_resume, crud_gap
from schemas.gap import AnalyzeGapRequest
from services.gap_engine import analyze_gap

async def perform_gap_analysis(db: AsyncSession, request: AnalyzeGapRequest, current_user: User):
    # Get latest active resume
    resumes = await crud_resume.get_user_resumes(db, current_user.id)
    if not resumes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active resume found. Please upload a resume first.")
    
    latest_resume = resumes[0]
    
    # Fetch target role benchmarks
    target_role = await crud_gap.get_target_role(db, request.target_role)
    if not target_role:
        # For MVP, auto-create a mock target role if it doesn't exist
        mock_skills = ["Python", "React", "SQL", "Docker", "AWS"]
        if "frontend" in request.target_role.lower():
            mock_skills = ["HTML", "CSS", "JavaScript", "React", "Redux"]
        elif "backend" in request.target_role.lower():
            mock_skills = ["Python", "Django", "FastAPI", "PostgreSQL", "Docker"]
            
        target_role = TargetRole(
            role_name=request.target_role,
            required_skills=mock_skills,
            min_projects=2,
            min_experience_years=request.experience_level_years,
            salary_band_base=70000.00
        )
        db.add(target_role)
        await db.flush()
        
    # Run Engine
    analysis_data, recommendations = await analyze_gap(
        parsed_resume=latest_resume.parsed_data,
        target_role=target_role,
        company_type=request.company_type
    )
    
    analysis_data["user_id"] = current_user.id
    analysis_data["target_role_id"] = target_role.id
    analysis_data["target_role_name"] = target_role.role_name
    analysis_data["company_type"] = request.company_type
    
    # Save
    gap_record = await crud_gap.create_gap_analysis(db, analysis_data)
    await crud_gap.create_gap_recommendations(db, gap_record.id, recommendations)
    
    # Fetch updated history to return latest full record
    history = await crud_gap.get_user_gap_history(db, current_user.id)
    return history[0]
