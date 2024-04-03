import sys
import os
import pathlib
 
from model.pretrained_model import pipe
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import pdfplumber
import os
import re
import pandas as pd


def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a given PDF file.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ''
            for i in range(len(pdf.pages)):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    full_text += page_text
            return full_text
    except Exception as e:
        print(f"Error: {e}")
        return ''
    
nltk.download('punkt')
nltk.download('stopwords')

stemmer = SnowballStemmer("english")
stop_words = set(stopwords.words("english"))

def clean_text(text):
    """
    Cleans the extracted text.
    - Removes special characters
    - Normalizes whitespace
    - Converts to lowercase (if necessary)
    """
    
    RE_WSPACE = re.compile(r"\s+", re.IGNORECASE)
    RE_TAGS = re.compile(r"<[^>]+>")
    RE_ASCII = re.compile(r"[^A-Za-zÀ-ž .]", re.IGNORECASE)
    RE_WDOT = re.compile(r"\.+", re.IGNORECASE)
    RE_SINGLECHAR = re.compile(r"\b[A-Za-zÀ-ž]\b", re.IGNORECASE)
    
    text = re.sub(RE_TAGS, " ", text)
    text = re.sub(RE_WDOT, ".", text)
    text = re.sub(RE_ASCII, " ", text)
    text = re.sub(RE_SINGLECHAR, " ", text)
    text = re.sub(RE_WSPACE, " ", text)
    text = text.replace(" .", ".")
    text = text.replace("..", ".")
    # Convert to lowercase
    word_tokens = word_tokenize(text)
    words_tokens_lower = [word.lower() for word in word_tokens]
    #words_filtered = [stemmer.stem(word) for word in words_tokens_lower if word not in stop_words]

    text_clean = " ".join(word_tokens)
    return text_clean.title()

full_text = extract_text_from_pdf("../data/Unstructured data/Azithromycin_tab_50730_RC1-08.pdf")
text = clean_text(full_text)
sentences = nltk.tokenize.sent_tokenize(text)


entities_data = []

for sentence in sentences:
    entities = pipe(sentence)
    for entity in entities:
        entity_data = {
            'entity_group': entity['entity_group'],
            'word': entity['word']
        }
        entities_data.append(entity_data)

# Convert to DataFrame
df = pd.DataFrame(entities_data)



def merge_tokens(df):
    merged_data = []
    current_word = ''
    current_entity_group = None

    for _, row in df.iterrows():
        # Check if the current row continues the current word
        if row['entity_group'] == current_entity_group and (current_word.endswith('##') or row['word'].startswith('##')):
            current_word += row['word'].lstrip('#')
        else:
            if current_word:
                # Save the previous word before starting a new one
                merged_data.append({'entity_group': current_entity_group, 'word': current_word})
            current_word = row['word'].lstrip('#')
            current_entity_group = row['entity_group']

    # Don't forget to add the last word
    if current_word:
        merged_data.append({'entity_group': current_entity_group, 'word': current_word})

    return pd.DataFrame(merged_data)


df = merge_tokens(df)


# Save to Parquet file
parquet_file_path = "../data/Structured data/entities.parquet"
df.to_parquet(parquet_file_path, engine = "fastparquet", index=False)

print(f"Entities saved to {parquet_file_path}")