"""
Cybersecurity interview track and question generator engine.
Supports targeted tracks: SOC Analyst, Ethical Hacker, Network Security, and Cloud Security.
Applies content safety filters to reject any working exploit code/commands.
"""

import logging
import random
import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

from core.llm.nvidia import NVIDIA_NIM_Client
from core.config import settings

logger = logging.getLogger(__name__)

CYBERSECURITY_TRACKS = {
    "soc_analyst": {
        "categories": ["log_analysis", "alert_triage", "incident_timeline",
                        "mitre_attack", "escalation_decision", "ioc_identification"],
        "log_types": ["apache_access", "windows_event", "syslog", "firewall"],
        "mitre_tactics": ["Initial Access", "Execution", "Persistence", "Privilege Escalation",
                          "Defense Evasion", "Credential Access", "Discovery", "Lateral Movement",
                          "Collection", "Exfiltration", "Command and Control"]
    },
    "ethical_hacker": {
        "categories": ["recon_methodology", "owasp_top10", "cve_reading",
                        "pentest_reporting", "scope_roe", "vulnerability_concepts"],
        "owasp": ["A01_Broken_Access_Control", "A02_Cryptographic_Failures",
                   "A03_Injection", "A04_Insecure_Design", "A05_Security_Misconfiguration",
                   "A06_Vulnerable_Components", "A07_Auth_Failures", "A08_SSRF",
                   "A09_Logging_Failures", "A10_SSRF"]
    },
    "network_security": {
        "categories": ["acl_analysis", "vpn_architecture", "ids_vs_ips",
                        "pcap_interpretation", "segmentation_design", "firewall_logic"]
    },
    "cloud_security": {
        "categories": ["iam_analysis", "zero_trust", "misconfiguration_detection",
                        "shared_responsibility", "cloud_native_threats", "encryption_at_rest"]
    }
}

CONTENT_SAFETY_FILTER = [
    "exploit", "payload", "shellcode", "reverse shell", "metasploit", "msfconsole",
    "sqlmap --", "nmap --script vuln", "CVE-exploit", "bypass authentication", 
    "credential dump", "mimikatz", "pass the hash attack command",
    "here is the code to exploit", "to hack this system", "actual working"
]

SYNTHETIC_LOG_SAMPLES = {
    "apache_access": """
192.168.1.50 - - [21/Jun/2026:10:00:01 +0530] "GET /index.html HTTP/1.1" 200 4523
192.168.1.50 - - [21/Jun/2026:10:00:05 +0530] "GET /about.html HTTP/1.1" 200 2341
192.168.1.50 - - [21/Jun/2026:10:00:10 +0530] "GET /products.php?category=1 HTTP/1.1" 200 12045
10.0.5.12 - - [21/Jun/2026:10:01:15 +0530] "GET /login.php HTTP/1.1" 200 1540
10.0.5.12 - - [21/Jun/2026:10:01:22 +0530] "POST /login.php HTTP/1.1" 401 123
10.0.5.12 - - [21/Jun/2026:10:01:30 +0530] "POST /login.php HTTP/1.1" 401 123
192.168.1.50 - - [21/Jun/2026:10:02:00 +0530] "GET /contact.html HTTP/1.1" 200 3412
203.0.113.85 - - [21/Jun/2026:10:03:45 +0530] "GET /products.php?category=1%20UNION%20SELECT%20null,username,password%20FROM%20users HTTP/1.1" 500 240
203.0.113.85 - - [21/Jun/2026:10:03:55 +0530] "GET /products.php?category=1%20AND%201=1 HTTP/1.1" 200 12045
192.168.1.50 - - [21/Jun/2026:10:04:10 +0530] "GET /css/style.css HTTP/1.1" 200 5231
192.168.1.50 - - [21/Jun/2026:10:04:12 +0530] "GET /js/app.js HTTP/1.1" 200 12340
    """.strip(),
    "windows_event": """
Event ID: 4625 | Category: Logon | Description: An account failed to log on. | Source IP: 198.51.100.12 | Account Name: Administrator | Time: 2026-06-21 10:15:01
Event ID: 4625 | Category: Logon | Description: An account failed to log on. | Source IP: 198.51.100.12 | Account Name: Administrator | Time: 2026-06-21 10:15:05
Event ID: 4625 | Category: Logon | Description: An account failed to log on. | Source IP: 198.51.100.12 | Account Name: Administrator | Time: 2026-06-21 10:15:10
Event ID: 4624 | Category: Logon | Description: An account was successfully logged on. | Source IP: 198.51.100.12 | Account Name: Administrator | Logon Type: 3 (Network) | Time: 2026-06-21 10:15:15
Event ID: 7045 | Category: Service Creation | Description: A service was installed in the system. | Service Name: PwnSvc | Service File Name: C:\\Windows\\Temp\\nc.exe -lvp 4444 -e cmd.exe | Time: 2026-06-21 10:16:02
    """.strip()
}

@dataclass
class CybersecurityQuestion:
    question_text: str
    key_points_required: List[str]
    sample_answer: str
    common_mistakes: List[str]
    log_context: Optional[str] = None

def get_fallback_question(topic: str) -> CybersecurityQuestion:
    """Safe fallback question if generation fails or is blocked by safety filters."""
    return CybersecurityQuestion(
        question_text=f"Explain the primary security considerations and defense-in-depth methodologies relating to {topic} in enterprise systems.",
        key_points_required=["defense-in-depth principles", "least privilege model", "continuous monitoring and logging"],
        sample_answer="Defense in depth relies on layering security controls at the network, host, application, and data levels, combined with security policies and personnel training to eliminate single points of failure.",
        common_mistakes=["relying on a single perimeter control", "overlooking network segmentation", "failing to log actions"]
    )

async def generate_cybersecurity_question(
    role_profile: str,
    topic: str,
    difficulty: int,
    context: dict,
    anthropic_client = None
) -> CybersecurityQuestion:
    """
    Selects security track, queries LLM with safety filters, and returns a conceptual question.
    """
    # 1. Map role_profile to tracks
    track_name = "soc_analyst"
    if "hacker" in role_profile.lower() or "pentest" in role_profile.lower():
        track_name = "ethical_hacker"
    elif "network" in role_profile.lower():
        track_name = "network_security"
    elif "cloud" in role_profile.lower():
        track_name = "cloud_security"

    track = CYBERSECURITY_TRACKS[track_name]
    categories = track["categories"]
    
    # Select category matching topic or random
    category = topic if topic in categories else random.choice(categories)

    log_context = None
    if category == "log_analysis":
        log_context = SYNTHETIC_LOG_SAMPLES.get(random.choice(track.get("log_types", ["apache_access"])))

    specific_category_instructions = ""
    if log_context:
        specific_category_instructions = f"Analyze the following synthetic log data to formulate the question:\n{log_context}"

    prompt = f"""
    Generate ONE professional cybersecurity interview question for a candidate applying for a {track_name} track.
    Category: {category}. Difficulty: {difficulty}/10.
    
    STRICT RULES — your question MUST NOT contain:
    - Any working exploit code, payloads, or command lines to launch attacks.
    - Step-by-step instructions to exploit a real CVE.
    - Specific commands to hack real systems.
    - Names of real vulnerable organizations or target brands.
    
    Your question MUST be:
    - Conceptual, architectural, and educational.
    - Formatted similar to professional certifications (e.g. CISSP, CEH, Security+).
    - Focused on evaluation of defense, analysis, and containment skills rather than offensive hacking ability.
    
    {specific_category_instructions}
    
    Return ONLY valid JSON format with keys:
    "question_text": "...",
    "key_points_required": ["point 1", "point 2"],
    "sample_answer": "...",
    "common_mistakes": ["mistake 1", "mistake 2"]
    """

    # Retry generation up to 3 times if safety checks trigger
    for attempt in range(3):
        try:
            if settings.ANTHROPIC_API_KEY:
                from anthropic import Anthropic
                client = anthropic_client or Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                resp = client.messages.create(
                    model=settings.CLAUDE_MODEL,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                raw_content = resp.content[0].text
            else:
                client = NVIDIA_NIM_Client()
                raw_content = await client.generate(prompt)

            # Parse JSON
            import json
            import re
            match = re.search(r"\{.*\}", raw_content, re.DOTALL)
            if not match:
                continue
                
            data = json.loads(match.group(0))
            question_text = data.get("question_text", "")

            # Content Safety Filter Check
            violation = False
            for pattern in CONTENT_SAFETY_FILTER:
                if pattern.lower() in question_text.lower():
                    logger.warning(f"Safety violation triggered for pattern '{pattern}' on attempt {attempt+1}!")
                    violation = True
                    break
            
            if violation:
                continue

            return CybersecurityQuestion(
                question_text=question_text,
                key_points_required=data.get("key_points_required", []),
                sample_answer=data.get("sample_answer", ""),
                common_mistakes=data.get("common_mistakes", []),
                log_context=log_context
            )
        except Exception as e:
            logger.error(f"Error during cybersecurity question generation: {e}")

    # Fallback to safe question if all attempts fail
    return get_fallback_question(topic)
