import spacy
import yaml
from modules.weights import load_weights
from spacy.cli import download
from spacy.util import is_package

if not is_package("en_core_web_sm"):
    download("en_core_web_sm")

nlp = spacy.load("en_core_web_sm")

KNOWN_SKILLS = {
    "python", "sql", "excel", "power bi", "tableau",
    "machine learning", "deep learning", "data analysis",
    "communication", "project management", "ai", "git"
}

def extract_skills(text):
    doc = nlp(text.lower())
    noun_chunks = set(chunk.text.strip() for chunk in doc.noun_chunks)
    entities = set(ent.text.strip() for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "SKILL"])
    tokens = set(token.text.strip() for token in doc if not token.is_stop and not token.is_punct)
    candidates = noun_chunks | entities | tokens
    found = {skill for skill in KNOWN_SKILLS for cand in candidates if skill in cand}
    return found

def match_skills(cv_text, jd_text):
    weights = load_weights()
    cv_keywords = extract_skills(cv_text)
    jd_keywords = extract_skills(jd_text)

    matched = cv_keywords & jd_keywords
    missing = jd_keywords - cv_keywords
    extra = cv_keywords - jd_keywords

    total_weight = sum(weights.get(skill, 1) for skill in jd_keywords)
    matched_weight = sum(weights.get(skill, 1) for skill in matched)
    score = round((matched_weight / total_weight) * 100, 2) if total_weight else 0

    return {
        "score": score,
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "cv_skills": cv_keywords,
        "jd_skills": jd_keywords
    }
