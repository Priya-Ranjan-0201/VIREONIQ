import re
from typing import Tuple, List, Dict, Any, Optional

try:
    import spacy  # type: ignore
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        import spacy.cli  # type: ignore
        spacy.cli.download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

STRONG_ACTION_VERBS = {
    "architected", "spearheaded", "developed", "engineered", "designed", 
    "optimized", "reduced", "increased", "managed", "implemented", "launched",
    "orchestrated", "transformed", "modernized"
}

def analyze_resume(sections: dict, target_role: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    # Combine text for holistic NLP analysis
    full_text = "\n".join(sections.values())
    entities = []
    quantified_count = 0
    strong_verb_count = 0
    weak_verb_count = 0
    doc = None

    if nlp is not None:
        try:
            doc = nlp(full_text)
            for sent in doc.sents:
                has_number = any(token.like_num for token in sent)
                if has_number and ("%" in sent.text or "$" in sent.text or "reduced" in sent.text.lower() or "increased" in sent.text.lower()):
                    quantified_count += 1
                    entities.append({"entity_type": "quantified_achievement", "entity_value": "metric", "context": sent.text})

                for token in sent:
                    if token.pos_ == "VERB":
                        if token.lemma_.lower() in STRONG_ACTION_VERBS:
                            strong_verb_count += 1
                            entities.append({"entity_type": "action_verb", "entity_value": token.lemma_.lower(), "context": sent.text})
                        else:
                            weak_verb_count += 1
        except Exception:
            doc = None

    if nlp is None or doc is None:
        # High-speed fallback analyzer without spacy
        sentences = [s.strip() for s in re.split(r'[.\n]+', full_text) if s.strip()]
        for sent in sentences:
            sent_lower = sent.lower()
            if any(char.isdigit() for char in sent) and any(m in sent_lower for m in ["%", "$", "reduced", "increased", "latency", "f1", "roc"]):
                quantified_count += 1
                entities.append({"entity_type": "quantified_achievement", "entity_value": "metric", "context": sent})
            words = re.findall(r'\b[a-zA-Z]+\b', sent_lower)
            for w in words:
                if w in STRONG_ACTION_VERBS:
                    strong_verb_count += 1
                    entities.append({"entity_type": "action_verb", "entity_value": w, "context": sent})
                elif w.endswith(('ed', 'ing')):
                    weak_verb_count += 1
                    
    # Calculate Scores (0-100)
    # Completeness checks if major sections are populated
    completeness_score = min(100.0, sum([20 for k, v in sections.items() if len(v.strip()) > 50]))
    
    # 5 quantified achievements = 100 points
    quantified_score = min(100.0, quantified_count * 20.0)
    
    # Action verb ratio
    total_verbs = strong_verb_count + weak_verb_count
    verb_ratio = (strong_verb_count / total_verbs) if total_verbs > 0 else 0
    action_verb_score = min(100.0, verb_ratio * 100.0 * 2) # Assume 50% strong verbs is a 100 score
    
    # Keyword match (simplified heuristic vs target role)
    role_keywords = [w.strip().lower() for w in target_role.split()]
    matched_keywords = sum(1 for kw in role_keywords if kw in full_text.lower())
    keyword_score = (matched_keywords / len(role_keywords)) * 100.0 if role_keywords else 100.0
    
    # Master Score Formula
    overall_score = (
        (completeness_score * 0.20) +
        (quantified_score * 0.20) +
        (action_verb_score * 0.15) +
        (keyword_score * 0.25) +
        (85.0 * 0.10) + # Formatting clarity baseline (OCR based in a full impl)
        (80.0 * 0.10)   # Role Relevance baseline
    )
    
    scores = {
        "overall_score": round(overall_score, 2),
        "keyword_match_score": round(keyword_score, 2),
        "completeness_score": round(completeness_score, 2),
        "quantified_achievements_score": round(quantified_score, 2),
        "action_verb_score": round(action_verb_score, 2),
        "formatting_score": 85.00,
        "role_relevance_score": 80.00,
        "improvement_notes": {
            "quantified": f"Found {quantified_count} quantified achievements. Add more metrics to your bullet points to increase this score.",
            "verbs": f"Used {strong_verb_count} strong action verbs. Replace weak verbs with strong leadership verbs.",
            "keywords": f"Matched {matched_keywords} out of {len(role_keywords)} keywords for the role '{target_role}'."
        }
    }
    
    return scores, entities


def compute_ats_compatibility_score(
    cv_text: str,
    candidate_skills: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Computes an advanced ATS compatibility score calibrated for Tier-1 MNC hiring:
      1. Structural Section Completeness (35% weight)
      2. Skill Keyword Density & Taxonomy Alignment (25% weight)
      3. Quantified Impact & STAR Metric Density (25% weight)
      4. Formatting & Readability Compliance (15% weight)
    """
    import re

    if not cv_text or not cv_text.strip():
        return {
            "score": 0,
            "categories": {
                "Section Completeness": 0,
                "Skill Keyword Density": 0,
                "Quantified Impact & STAR": 0,
                "Formatting & Readability": 0
            },
            "recommendations": ["Upload or paste your resume text to receive an ATS score."]
        }

    text_lower = cv_text.lower()
    skills = candidate_skills or []

    # 1. Structural Section Checks (Max 35 points)
    # Recognize both professional industry and academic/student technical formats (Harvard / Wall Street)
    has_summary = any(x in text_lower for x in ["summary", "profile", "about me", "professional summary", "executive summary", "objective", "overview"])
    has_education = any(x in text_lower for x in ["education", "academic", "university", "college", "degree", "bachelor", "master", "b.s.", "m.s.", "b.tech", "m.tech", "school", "cgpa", "percentage", "matriculation", "intermediate"])
    has_experience = any(x in text_lower for x in ["experience", "employment", "work history", "professional experience", "career history", "internship", "internships", "training", "trainings", "industrial training"])
    has_projects = any(x in text_lower for x in ["projects", "personal projects", "key projects", "technical projects", "open source", "academic projects"])
    has_skills = bool(candidate_skills) or any(x in text_lower for x in ["skills", "technical skills", "competencies", "technologies", "languages", "frameworks", "tools & platforms"])
    has_certs_or_extra = any(x in text_lower for x in ["certifications", "certificates", "certified", "hackathon", "extra-curricular", "activities", "achievements", "kaggle", "competitions"])

    # High-density tech resumes often omit summaries to maximize room for projects and internships
    section_score = 0.0
    if has_experience: section_score += 10.0
    if has_projects: section_score += 9.0
    if has_skills: section_score += 8.0
    if has_education: section_score += 8.0
    if has_summary: section_score += 5.0
    if has_certs_or_extra: section_score += 5.0
    section_score = min(35.0, section_score)

    # 2. Skill Density (Max 25 points)
    # Check both candidate_skills argument and skills embedded in resume
    detected_skills = list(skills)
    common_tech = [
        "python", "javascript", "typescript", "c++", "java", "react", "react.js", "angular", "node.js",
        "fastapi", "express", "html", "css", "tailwind", "docker", "kubernetes", "aws", "git", "github",
        "sql", "postgresql", "mongodb", "redis", "scikit-learn", "machine learning", "nlp", "generative ai",
        "gemini", "linux", "rest api", "graphql", "ag-grid", "jasmine", "vite", "pandas", "numpy", "streamlit"
    ]
    for ct in common_tech:
        if ct in text_lower and ct not in [s.lower() for s in detected_skills]:
            detected_skills.append(ct)

    skill_count = len(detected_skills)
    skill_score = min(25.0, 15.0 + (min(10, skill_count) * 1.0)) if skill_count >= 3 else (skill_count * 4.0)

    # 3. Quantified Impact & Action Verb / STAR Density (Max 25 points)
    # Includes standard metrics, technical benchmark metrics, performance indices, and academic metrics
    metric_regex = r"(\d+(?:\.\d+)?%|\$\d+(?:,\d+)*(?:\.\d+)?(?:k|m|b)?|₹\d+(?:,\d+)*(?:\.\d+)?(?:l|cr|k)?|\d+\+?\s*(?:users|requests|req/sec|ms|events|queries|nodes|clusters|seconds|minutes|hours|days|years|clients|customers|rps|tps|lpa|stars|downloads)|\b\d+x\b|cgpa:\s*\d+(?:\.\d+)?|percentage:\s*\d+(?:\.\d+)?%?|f1-score|roc-auc|oof|latency|throughput|load time|sub-second|real-time|v3|manifest v3|ag-grid|server-side pagination)"
    quantified_matches = re.findall(metric_regex, text_lower)
    quantified_count = len(quantified_matches)

    action_verbs = [
        "architected", "engineered", "spearheaded", "orchestrated", "developed",
        "optimized", "accelerated", "designed", "implemented", "scaled", "automated",
        "built", "reduced", "increased", "streamlined", "containerized", "refactored",
        "contributed", "improved", "enhanced", "wrote", "evaluated", "deployed", "integrated",
        "authored", "standardized", "applied", "pioneered", "championed", "led"
    ]
    action_matches = [v for v in action_verbs if re.search(r"\b" + v + r"\b", text_lower)]
    action_verb_count = len(action_matches)

    impact_score = min(25.0, 10.0 + (min(6, quantified_count) * 1.5) + (min(6, action_verb_count) * 1.0))

    # 4. Readability & Formatting (Max 15 points)
    words = cv_text.split()
    word_count = len(words)
    readability_score = 15.0 if 220 <= word_count <= 950 else (12.0 if 150 <= word_count < 220 or 950 < word_count <= 1300 else 8.0)

    total_score = round(section_score + skill_score + impact_score + readability_score)
    total_score = max(35, min(99, total_score))

    recs = []
    if not has_experience:
        recs.append("Detail your Work Experience or Internships with quantified achievements using the STAR methodology.")
    if not has_projects:
        recs.append("Add a Key Projects section with links to verified GitHub repositories or live production demos.")
    if len(detected_skills) < 6:
        recs.append("Include more industry-standard technical competencies to satisfy ATS keyword filters.")
    if quantified_count < 2:
        recs.append("Quantify your achievements: incorporate measurable metrics (e.g., 'reduced latency by 45%', 'scaled to 10M+ events', 'F1-score 0.94').")
    if action_verb_count < 3:
        recs.append("Elevate action verbs: replace passive phrasing with strong leadership verbs like 'Architected', 'Spearheaded', 'Engineered'.")
    if word_count < 200:
        recs.append("Your resume is sparse (under 200 words). Elaborate on technical responsibilities and measurable outcomes.")

    if not recs:
        recs.append("Your resume structure, STAR metric density, and keyword alignment satisfy top-tier MNC ATS filters!")

    return {
        "score": total_score,
        "categories": {
            "Section Completeness": round((section_score / 35.0) * 100),
            "Skill Keyword Density": round((skill_score / 25.0) * 100),
            "Quantified Impact & STAR": round((impact_score / 25.0) * 100),
            "Formatting & Readability": round((readability_score / 15.0) * 100)
        },
        "metrics_found": quantified_count,
        "action_verbs_found": action_verb_count,
        "word_count": word_count,
        "recommendations": recs
    }
