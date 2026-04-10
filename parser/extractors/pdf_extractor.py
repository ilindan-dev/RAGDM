import re
import pdfplumber
from tqdm import tqdm

def extract_text_from_pdf(pdf_path: str) -> str:
    """Извлекает текст, удаляя колонтитулы (номера страниц формата 1 / 1738)."""
    full_text = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in tqdm(pdf.pages, desc=f"Чтение {pdf_path.name}"):
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            clean_lines = []
            for line in lines:
                # Пропускаем номера страниц
                if re.match(r'^\s*\d+\s*/\s*\d+\s*$', line):
                    continue
                clean_lines.append(line)
                
            full_text.append('\n'.join(clean_lines))
            
    return '\n'.join(full_text)
