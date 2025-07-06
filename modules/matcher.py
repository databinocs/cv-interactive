import re
import yaml
from modules.weights import load_weights
import spacy
from spacy.util import is_package
from spacy.cli import download
from spacy.lang.en.stop_words import STOP_WORDS

def get_nlp():
    if not is_package("en_core_web_sm"):
        try:
            download("en_core_web_sm")
        except:
            print("⚠️ Cannot download SpaCy model.")
            return spacy.blank("en")
    return spacy.load("en_core_web_sm")

nlp = get_nlp()


KNOWN_SKILLS = {
    "python", "sql", "excel", "power bi", "tableau",
    "machine learning", "deep learning", "data analysis",
    "communication", "project management", "ai", "git"
}


nlp = spacy.load("en_core_web_sm")

def clean_word(w):
    w = w.lower().strip()
    if len(w) <= 2:
        return False
    if re.search(r'\d', w):
        return False
    if not w.isalpha():
        return False
    if w in STOP_WORDS:
        return False
    return True

def extract_skills(text):
    doc = nlp(text.lower())
    noun_chunks = set(chunk.text.strip() for chunk in doc.noun_chunks)
    entities = set(ent.text.strip() for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "SKILL", "PERSON"])
    tokens = set(token.text.strip() for token in doc if not token.is_stop and not token.is_punct)
    candidates = noun_chunks | entities | tokens

    # Lọc
    cleaned = set()
    for w in candidates:
        if clean_word(w):
            cleaned.add(w.lower())
    return cleaned


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
