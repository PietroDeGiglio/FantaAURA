import unicodedata
import re

def normalize_name(name):
    if not name or not isinstance(name, str):
        return ""
    # Remove accents
    n = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
    # Lowercase
    n = n.lower()
    # Remove punctuation
    n = re.sub(r'[^\w\s]', '', n)
    # Normalize spaces
    n = re.sub(r'\s+', ' ', n).strip()
    return n