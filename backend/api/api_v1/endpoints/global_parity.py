import io
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from db.session import get_db
from api import deps
from db.models import User, TalentPassport
from services import global_parity_service

router = APIRouter()

class TranslateCredentialRequest(BaseModel):
    target_market: str

@router.post("/generate-passport")
async def generate_passport(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Triggers generation of the candidate's global Talent Passport.
    """
    passport = await global_parity_service.generate_talent_passport(
        user_id=current_user.id,
        db=db
    )
    return passport

@router.get("/my-passport")
async def get_my_passport(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns the authenticated user's Talent Passport details.
    """
    stmt = select(TalentPassport).where(TalentPassport.user_id == current_user.id)
    passport = (await db.execute(stmt)).scalars().first()
    if not passport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Talent Passport profile not found. Generate one first."
        )
    return passport

@router.get("/my-passport.pdf")
async def get_my_passport_pdf(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates a PDF version of the Talent Passport with a professional layout.
    """
    stmt = select(TalentPassport).where(TalentPassport.user_id == current_user.id)
    passport = (await db.execute(stmt)).scalars().first()
    if not passport:
        raise HTTPException(
            status_code=404,
            detail="Talent Passport not found. Please generate one first."
        )

    # Attempt PDF creation via ReportLab, falling back to a clean raw PDF stream
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=12
        )
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['BodyText'],
            fontSize=11,
            spaceAfter=6
        )

        story.append(Paragraph("<b>PLACEIQ GLOBAL TALENT PASSPORT</b>", title_style))
        story.append(Paragraph(f"<b>Passport ID:</b> {passport.passport_id}", body_style))
        story.append(Paragraph(f"<b>Verified Role:</b> {passport.verified_role}", body_style))
        story.append(Paragraph(f"<b>Skill Tier:</b> {passport.skill_tier.upper()}", body_style))
        story.append(Paragraph(f"<b>PRS Score:</b> {passport.prs_score}", body_style))
        story.append(Paragraph(f"<b>English Proficiency:</b> {passport.english_proficiency_tier}", body_style))
        
        # Dimensions Table
        data = [
            ["Metric", "Value"],
            ["Global Tier Eligibility", ", ".join(passport.eligible_company_tiers or [])],
            ["Contractor Rate range", f"${passport.contractor_rate_min} - ${passport.contractor_rate_max} / hr"],
            ["Verification URL", passport.public_passport_url or "https://placeiq.app"]
        ]
        t = Table(data, colWidths=[150, 350])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (1,0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0,0), (1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
        ]))
        
        story.append(Spacer(1, 15))
        story.append(t)
        doc.build(story)
        pdf_bytes = buffer.getvalue()
    except Exception:
        # Fallback raw PDF stream
        buffer = io.BytesIO()
        pdf_content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 1200 >>
stream
BT
/F1 20 Tf
50 700 Td
(PLACEIQ GLOBAL TALENT PASSPORT) Tj
/F1 11 Tf
0 -40 Td
(Passport ID: {passport.passport_id}) Tj
0 -20 Td
(Verified Role: {passport.verified_role}) Tj
0 -20 Td
(Skill Tier: {passport.skill_tier.upper()}) Tj
0 -20 Td
(PRS Score: {passport.prs_score}) Tj
0 -20 Td
(English Level: {passport.english_proficiency_tier}) Tj
0 -20 Td
(Contractor Rate: ${passport.contractor_rate_min} - ${passport.contractor_rate_max} / hr) Tj
0 -40 Td
(Verification URL: {passport.public_passport_url}) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000056 00000 n 
0000000111 00000 n 
0000000277 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
500
%%EOF
"""
        buffer.write(pdf_content.encode("utf-8"))
        pdf_bytes = buffer.getvalue()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=passport_{passport.passport_id}.pdf"}
    )

@router.get("/opportunities")
async def get_opportunities(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns list of matching global remote-first opportunities for authenticated user.
    """
    opps = await global_parity_service.find_global_opportunities(
        user_id=current_user.id,
        db=db
    )
    return opps

@router.post("/translate-credential")
async def translate_credential(
    payload: TranslateCredentialRequest,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Translates candidate profiles for specific foreign job markets.
    """
    trans = await global_parity_service.translate_credential_for_market(
        user_id=current_user.id,
        target_market=payload.target_market,
        db=db
    )
    return trans

@router.get("/passport/{passport_id}")
async def get_public_passport(
    passport_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Public recruiter verification lookup for a specific passport (anonymized).
    """
    stmt = select(TalentPassport).where(TalentPassport.passport_id == passport_id)
    passport = (await db.execute(stmt)).scalars().first()
    if not passport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passport not found."
        )
    return {
        "passport_id": passport.passport_id,
        "verified_role": passport.verified_role,
        "skill_tier": passport.skill_tier,
        "prs_score": passport.prs_score,
        "english_proficiency_tier": passport.english_proficiency_tier,
        "eligible_company_tiers": passport.eligible_company_tiers,
        "contractor_rate_min": passport.contractor_rate_min,
        "contractor_rate_max": passport.contractor_rate_max
    }

@router.get("/country-guide/{country_code}")
async def get_country_guide(
    country_code: str
):
    """
    Returns visa pathways and rates for country profiles.
    """
    code = country_code.upper()
    if code not in global_parity_service.COUNTRY_HIRING_PROFILES:
        raise HTTPException(
            status_code=404,
            detail="Country profile not found."
        )
    return global_parity_service.COUNTRY_HIRING_PROFILES[code]
