from deep_translator import GoogleTranslator

def auto_translate_to_english(text):
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        return translated
    except Exception as e:
        return f"Error translating text: {e}"
