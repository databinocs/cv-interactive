import re
import html

def create_span(word, color, tooltip=""):
    return f"<span title='{html.escape(tooltip)}' style='background-color:{color}; padding:2px 4px; border-radius:4px;'>{html.escape(word)}</span>"

def highlight_skills_by_group(text, matched, missing, extra):
    def apply_highlight(input_text, word_list, color, tooltip):
        result = input_text
        for word in sorted(word_list, key=len, reverse=True):
            if not word.strip(): continue
            pattern = re.compile(rf"\b({re.escape(word)})\b", re.IGNORECASE)
            result = pattern.sub(lambda m: create_span(m.group(1), color, tooltip), result)
        return result

    escaped = html.escape(text)
    highlighted = apply_highlight(escaped, matched, "#b7e4c7", "Matched skill in CV")
    highlighted = apply_highlight(highlighted, missing, "#fdd6a0", "Missing skill from CV")
    highlighted = apply_highlight(highlighted, extra, "#f2b5d4", "Extra skill in CV")

    return f"<div style='line-height:1.6; font-size:15px'>{highlighted.replace(chr(10), '<br>')}</div>"
