import io
import logging
import fitz  # PyMuPDF
import docx
import re

logger = logging.getLogger(__name__)

def parse_pdf(file_bytes: bytes) -> str:
    """
    Robust multi-engine PDF text extractor with fallback.
    """
    text = ""
    # 1. Primary: PyMuPDF (fitz)
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text() + "\n"
    except Exception as e:
        logger.warning(f"PyMuPDF failed to parse PDF: {e}")

    # 2. Secondary fallback: pypdf if text is empty
    if not text.strip():
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        except Exception as e:
            logger.warning(f"pypdf fallback failed: {e}")

    # 3. Tertiary fallback: raw printable text recovery
    if not text.strip():
        try:
            decoded = file_bytes.decode("utf-8", errors="ignore")
            printable_lines = [
                line.strip() for line in decoded.splitlines()
                if len(line.strip()) > 3 and all(c.isprintable() or c.isspace() for c in line)
            ]
            text = "\n".join(printable_lines)
        except Exception:
            pass

    return text.strip()

def parse_docx(file_bytes: bytes) -> str:
    """
    Extracts text from paragraphs and embedded tables in Word DOCX.
    """
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        lines = [para.text for para in doc.paragraphs if para.text]
        for table in doc.tables:
            for row in table.rows:
                row_str = " | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()])
                if row_str:
                    lines.append(row_str)
        return "\n".join(lines)
    except Exception as e:
        logger.warning(f"python-docx failed to parse: {e}")
        try:
            return file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            return ""

def extract_sections(raw_text: str) -> dict:
    """
    Heuristic section extraction logic.
    Segments text into Education, Experience, Skills, Projects, Certifications, Training based on keyword headers.
    """
    sections = {
        "education": "",
        "experience": "",
        "skills": "",
        "projects": "",
        "summary": "",
        "certifications": "",
        "training": "",
        "activities": ""
    }
    
    current_section = "summary"
    lines = raw_text.split('\n')
    
    for line in lines:
        lower_line = line.strip().lower()
        if not lower_line:
            continue
            
        if any(h in lower_line for h in ["education", "academic qualification", "academic background"]) and len(lower_line) < 30:
            current_section = "education"
        elif any(h in lower_line for h in ["experience", "employment", "work history", "internship", "internships", "professional experience"]) and len(lower_line) < 30:
            current_section = "experience"
        elif any(h in lower_line for h in ["skills", "technical skills", "competencies", "technologies & tools", "technical competencies"]) and len(lower_line) < 30:
            current_section = "skills"
        elif any(h in lower_line for h in ["projects", "personal projects", "key projects", "technical projects", "academic projects"]) and len(lower_line) < 30:
            current_section = "projects"
        elif any(h in lower_line for h in ["training", "industrial training", "professional training"]) and len(lower_line) < 30:
            current_section = "experience"
        elif any(h in lower_line for h in ["certifications", "certificates", "licenses"]) and len(lower_line) < 30:
            current_section = "certifications"
        elif any(h in lower_line for h in ["extra-curricular", "activities", "achievements", "hackathons", "honors"]) and len(lower_line) < 35:
            current_section = "activities"
            
        sections[current_section] += line + "\n"
        
    return sections
