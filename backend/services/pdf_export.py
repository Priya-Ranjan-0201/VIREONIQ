"""
Gap Report / Offer Letter PDF generation service.
Uses standard HTML-to-PDF mappings or simple ReportLab outputs.
"""
from typing import Dict, Any
import io


def generate_offer_letter_pdf(
    student_name: str,
    company_name: str,
    role_name: str,
    ctc: float
) -> bytes:
    """
    Generate a mock PDF file stream for the offer letter.
    For simplicity and reliability, returns a beautifully formatted PDF-compatible text buffer.
    """
    buffer = io.BytesIO()
    
    # Simple plain-text structure mapping to a PDF envelope
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
<< /Length {1000} >>
stream
BT
/F1 24 Tf
50 700 Td
(VIREONIQ PLACEMENT INTELLIGENCE MOCK OFFER) Tj
/F1 12 Tf
0 -40 Td
(Dear {student_name},) Tj
0 -20 Td
(We are pleased to extend you an offer from {company_name} for the position of {role_name}.) Tj
0 -20 Td
(Annual CTC: INR {ctc} LPA) Tj
0 -40 Td
(Best Regards,) Tj
0 -20 Td
(The VIREONIQ Simulation Team) Tj
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
    return buffer.getvalue()
