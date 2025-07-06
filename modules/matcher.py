import yaml
from modules.weights import load_weights
import spacy
from spacy.util import is_package
from spacy.cli import download

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

def extract_skills(text):
    doc = nlp(text.lower())

    # Bọc noun_chunks để tránh lỗi nếu parser thiếu
    noun_chunks = set()
    try:
        noun_chunks = set(chunk.text.strip() for chunk in doc.noun_chunks if len(chunk.text.strip().split()) <= 5)
    except:
        pass

    # Entity tên kỹ năng, tổ chức, sản phẩm
    entities = set(ent.text.strip() for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "SKILL", "WORK_OF_ART"])

    # Lọc token: không stopword, không số, không email, không từ ngắn
    tokens = set(
        token.text.strip() for token in doc
        if not token.is_stop and not token.is_punct and
           not token.like_num and not token.like_email and
           len(token.text.strip()) > 2 and token.is_alpha
    )

    # Kết hợp và loại các biểu thức vô nghĩa
    all_candidates = noun_chunks | entities | tokens
    clean_skills = set()
    for w in all_candidates:
        if re.search(r'\d', w): continue
        if "@" in w or ".com" in w: continue
        if len(w) < 3: continue
        clean_skills.add(w.lower())

    return clean_skills


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
