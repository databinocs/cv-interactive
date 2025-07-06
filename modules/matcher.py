import re
import os
import yaml
from modules.weights import load_weights
import spacy
from spacy.util import is_package
from spacy.cli import download
from spacy.lang.en.stop_words import STOP_WORDS

# Load SpaCy model an toàn
def get_nlp():
    if not is_package("en_core_web_sm"):
        try:
            print("⏬ Downloading SpaCy model...")
            download("en_core_web_sm")
        except:
            print("⚠️ Cannot download SpaCy model. Fallback to blank English model.")
            return spacy.blank("en")
    return spacy.load("en_core_web_sm")

nlp = get_nlp()


# Load kỹ năng chuẩn từ file
SKILLS_FILE = os.path.join(os.path.dirname(__file__), "..", "known_skills.txt")
with open(SKILLS_FILE, "r", encoding="utf-8") as f:
    KNOWN_SKILLS = set(line.strip().lower() for line in f if line.strip() and not line.startswith("#"))


# Trích xuất kỹ năng từ văn bản
def extract_skills(text):
    doc = nlp(text.lower())

    # Fallback nếu không có parser/ner
    if not nlp.has_pipe("parser") or not nlp.has_pipe("ner"):
        noun_chunks = set()
        entities = set()
    else:
        noun_chunks = set(chunk.text.strip() for chunk in doc.noun_chunks)
        entities = set(ent.text.strip() for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "SKILL"])

    tokens = set(token.text.strip() for token in doc if not token.is_stop and not token.is_punct)

    candidates = noun_chunks | entities | tokens

    found = set()
    for cand in candidates:
        if len(cand) < 2 or len(cand.split()) > 5:
            continue
        if re.search(r"\d", cand):  # bỏ số điện thoại, năm
            continue
        for skill in KNOWN_SKILLS:
            if skill in cand.lower():
                found.add(skill)
    return found

# Match kỹ năng giữa CV và JD
def match_skills(cv_text, jd_text):
    cv_keywords = extract_skills(cv_text)
    jd_keywords = extract_skills(jd_text)

    matched = cv_keywords & jd_keywords
    missing = jd_keywords - cv_keywords
    extra = cv_keywords - jd_keywords

    weights = load_weights()
    matched_weight = sum(weights.get(skill, 1) for skill in matched)
    total_weight = sum(weights.get(skill, 1) for skill in jd_keywords)

    score = round((matched_weight / total_weight) * 100, 2) if total_weight else 0

    return {
        "score": score,
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "cv_skills": cv_keywords,
        "jd_skills": jd_keywords
    }
