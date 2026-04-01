import pdfplumber
import re
import pymorphy2

def parse_hall_text(pdf_pass): 
    
    result = [] 
    
    with pdfplumber.open(pdf_pass) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            
            result.append({
                'page': page_num,
                'text': text
            })
            
    return result

def filter_text(text):
    text = re.sub(r'\n+', '\n', text)  
    
    text = re.sub(r'\s+', ' ', text)
    
    text = re.sub(r'\(стр\.\s+\d+\)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[страница\s+\d+\]', '', text, flags=re.IGNORECASE)
    
    # 5. Удаляем URL
    text = re.sub(r'https?://\S+', '', text)
    
    # 6. Финальная очистка пробелов
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    
    return text

morph = pymorphy2.MorphAnalyzer()

def normalize_text_lemmatize(text, language='ru'):
    
    text = text.lower()
    
    words = text.split()
    lemmatized = []
    
    for word in words: 
        parsed = morph.parse(word)[0]
        lemma = parsed.normal_form
        lemmatized.append(lemma.normal_form)
        
    return ' '.join(lemmatized)


def prepare_text_for_rag(pdf_path):
    
    chunks = parse_hall_text(pdf_path)
    
    result = []
    for chunk in chunks:

        filtered = filter_text(chunk['text'])
        
        normalized = normalize_text_lemmatize(filtered)
        
        result.append({
            "page": chunk['page'],
            "original": chunk['text'],
            "normalized": normalized
        })
    
    return result

if __name__ == "__main__":
    pdf_pass = ""