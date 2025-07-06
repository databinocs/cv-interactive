import streamlit as st
import yaml
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import spacy

from spacy.util import is_package
from spacy.cli import download

if not is_package("en_core_web_sm"):
    download("en_core_web_sm")

from modules.parser import extract_text_from_pdf
from modules.matcher import match_skills, extract_skills
from modules.exporter import export_text_as_md, export_text_as_pdf
from modules.translate import auto_translate_to_english
from modules.highlighter import highlight_skills_by_group
from modules.weights import load_weights

st.markdown("""
<style>
    .block-container { padding: 2rem 3rem; font-family: 'Segoe UI', sans-serif; }
    .stMarkdown p { margin-bottom: 0.5rem; line-height: 1.6; }
    span[title] { cursor: help; text-decoration: underline dotted; }
</style>
""", unsafe_allow_html=True)

def load_profile():
    with open("profile.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

profile = load_profile()
st.set_page_config(page_title=f"{profile['name']} | CV", layout="wide")
st.title("📄 CV Interactive + Resume Match")

# Sidebar
with st.sidebar:
    st.image(profile["avatar"], width=150)
    st.header(profile["name"])
    st.caption(profile["title"])
    st.markdown("### 📬 Contact")
    st.markdown(f"📧 [{profile['contact']['email']}](mailto:{profile['contact']['email']})")
    st.markdown(f"🔗 [LinkedIn]({profile['contact']['linkedin']})")
    st.markdown(f"🐱 [GitHub]({profile['contact']['github']})")

from modules.weights import load_weights  # nếu load từ file weights.yaml

def build_skill_table(matched, missing, extra, weights):
    rows = []
    for skill in sorted(matched):
        rows.append({"Skill": skill, "Group": "Matched", "Weight": weights.get(skill, 1)})
    for skill in sorted(missing):
        rows.append({"Skill": skill, "Group": "Missing", "Weight": weights.get(skill, 1)})
    for skill in sorted(extra):
        rows.append({"Skill": skill, "Group": "Extra", "Weight": "—"})
    return pd.DataFrame(rows)


# Tabs
tabs = st.tabs(["About", "Experience", "Skills", "Projects", "🧠 Resume Match"])

with tabs[0]:
    st.subheader("About Me")
    st.markdown(profile["about"])

with tabs[1]:
    st.subheader("Experience")
    for job in profile["experience"]:
        st.markdown(f"**{job['role']}**, *{job['company']}* ({job['years']})")
        st.markdown(f"- {job['desc']}")

with tabs[2]:
    st.subheader("Skills")
    st.markdown("✅ " + "\n✅ ".join(profile["skills"]))

with tabs[3]:
    st.subheader("Projects")
    for proj in profile["projects"]:
        st.markdown(f"🔗 **[{proj['title']}]({proj['link']})** — {proj['desc']}")

with tabs[4]:
    st.subheader("🧠 Resume Match & Skill Analyzer")

    st.markdown("📄 Upload Job Description (optional)")
    jd_file = st.file_uploader("Upload JD PDF (optional)", type="pdf")
    jd_text = ""

    if jd_file:
        jd_text = extract_text_from_pdf(jd_file)
        st.success("✅ JD loaded from PDF")
    else:
        jd_text = st.text_area("📝 Or paste Job Description", height=200)

    cv_file = st.file_uploader("📄 Upload your CV (PDF)", type="pdf")

    if cv_file and jd_text and st.button("🔍 Analyze CV & JD"):
        with st.spinner("🔁 Translating JD if needed..."):
            jd_translated = auto_translate_to_english(jd_text)

        with st.spinner("🔍 Matching skills..."):
            cv_text = extract_text_from_pdf(cv_file)
            result = match_skills(cv_text, jd_translated)
            score = result["score"]
            matched = result["matched"]
            missing = result["missing"]
            extra = result["extra"]
            cv_keywords = result["cv_skills"]
            jd_keywords = result["jd_skills"]

        st.metric("🎯 Match Score", f"{score}%")

        # Hiển thị 3 nhóm kỹ năng
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"### ✅ Matched Skills ({len(matched)})")
            st.write(", ".join(sorted(matched)) or "None")

        with col2:
            st.markdown(f"### ⚠️ Missing Skills from CV ({len(missing)})")
            st.write(", ".join(sorted(missing)) or "None")

        with col3:
            st.markdown(f"### 🧩 Extra Skills in CV ({len(extra)})")
            st.write(", ".join(sorted(extra)) or "None")

        st.markdown("---")
        st.markdown("### 📌 Highlighted JD with Skills (Color Grouped)")
        st.markdown(highlight_skills_by_group(jd_translated, matched, missing, extra), unsafe_allow_html=True)

        # Export report
        report = f"""# 📄 Resume Match Report

## 🔍 Overview

- Match Score: {score}%
- Total Skills in JD: {len(matched) + len(missing)}
- Matched Skills: {len(matched)}
- Missing Skills: {len(missing)}

---

## ✅ Matched Skills
{chr(10).join(f"- {skill}" for skill in sorted(matched)) or 'None'}

---

## ⚠️ Missing Skills
{chr(10).join(f"- {skill}" for skill in sorted(missing)) or 'None'}

---

## 🧩 Extra Skills in CV
{chr(10).join(f"- {skill}" for skill in sorted(extra)) or 'None'}

---

## 📋 Extracted Keywords

**From CV:**
{chr(10).join(f"- {kw}" for kw in sorted(cv_keywords)) or 'None'}

**From JD:**
{chr(10).join(f"- {kw}" for kw in sorted(jd_keywords)) or 'None'}

---

## 💡 Recommendations

- Consider strengthening your experience or wording related to:
{chr(10).join(f"  - {skill}" for skill in sorted(missing)) or '  - (None)'}

- You can enhance your CV by adding or emphasizing the missing skills (if you already have them).
- Tailor the language in your CV to match the JD terminology.

---

_Report generated automatically by CV Interactive._
"""
        st.markdown("### 📄 Export Report")
        st.markdown(export_text_as_md(report), unsafe_allow_html=True)
        st.markdown(export_text_as_pdf(report), unsafe_allow_html=True)

        # Radar chart 
        st.markdown("### 📊 Radar Chart")
        labels = list(matched | missing)
        values = [1 if l in matched else 0 for l in labels]
        values += values[:1]
        angles = [n / float(len(labels)) * 2 * 3.14159265 for n in range(len(labels))]
        angles += angles[:1]
        fig, ax = plt.subplots(subplot_kw={'polar': True})
        ax.plot(angles, values)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_yticklabels([])
        st.pyplot(fig)

        # Skill Table
        st.markdown("### 📋 Skill Breakdown Table")
        weights = load_weights()
        skill_df = build_skill_table(matched, missing, extra, weights)
        st.dataframe(skill_df, use_container_width=True)
