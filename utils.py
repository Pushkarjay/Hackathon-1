import PyPDF2
import nltk
import re
import os
from nltk.tokenize import word_tokenize
from nltk.data import find

# Ensure 'punkt' and 'punkt_tab' are downloaded
try:
    find('tokenizers/punkt')
    find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = "".join(page.extract_text() or "" for page in reader.pages)
            return text if text else "No text extracted"
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def preprocess_text(text):
    """Cleans and tokenizes text for NLP."""
    tokens = word_tokenize(text.lower())
    return " ".join(tokens[:200])  # Limit to 200 tokens

def extract_email(text):
    """Extracts email from CV text."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    return match.group(0) if match else "unknown@example.com"

# Example usage (for testing)
if __name__ == "_main_":
    text = extract_text_from_pdf("data/CVs1/C1061.pdf")
    processed = preprocess_text(text)
    email = extract_email(text)
    print("Processed text sample:", processed[:100])
    print("Extracted email:", email)